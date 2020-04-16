import datetime
import os

import bleach
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from groups.defaults import defaults
from groups.features import HAS_group_MERGE
from groups.forms import AddEditgroupForm
from groups.models import Attachment, Comment, group
from groups.utils import (
    send_email_to_thread_participants,
    staff_check,
    toggle_group_completed,
    user_can_read_group,
)

if HAS_group_MERGE:
    from dal import autocomplete


def handle_add_comment(request, group):
    if not request.POST.get("add_comment"):
        return

    Comment.objects.create(
        author=request.user, group=group, body=bleach.clean(request.POST["comment-body"], strip=True)
    )

    send_email_to_thread_participants(
        group,
        request.POST["comment-body"],
        request.user,
        subject='New comment posted on group "{}"'.format(group.title),
    )

    messages.success(request, "Comment posted. Notification email sent to thread participants.")


@login_required
@user_passes_test(staff_check)
def group_detail(request, group_id: int) -> HttpResponse:
    """View group details. Allow group details to be edited. Process new members on group.
    """

    group = get_object_or_404(group, pk=group_id)
    comment_list = Comment.objects.filter(group=group_id).order_by("-date")

    # Ensure user has permission to view group. Superusers can view all Groups.
    # Get the group this group belongs to, and check whether current user is a member of that group.
    if not user_can_read_group(group, request.user):
        raise PermissionDenied

    # Handle group merging
    if not HAS_group_MERGE:
        merge_form = None
    else:

        class MergeForm(forms.Form):
            merge_target = forms.ModelChoiceField(
                queryset=group.objects.all(),
                widget=autocomplete.ModelSelect2(
                    url=reverse("groups:group_autocomplete", kwargs={"group_id": group_id})
                ),
            )

        # Handle group merging
        if not request.POST.get("merge_group_into"):
            merge_form = MergeForm()
        else:
            merge_form = MergeForm(request.POST)
            if merge_form.is_valid():
                merge_target = merge_form.cleaned_data["merge_target"]
            if not user_can_read_group(merge_target, request.user):
                raise PermissionDenied

            group.merge_into(merge_target)
            return redirect(reverse("groups:group_detail", kwargs={"group_id": merge_target.pk}))

    # Save submitted members
    handle_add_comment(request, group)

    # Save group edits
    if not request.POST.get("add_edit_group"):
        form = AddEditgroupForm(request.user, instance=group, initial={"group_list": group.group_list})
    else:
        form = AddEditgroupForm(
            request.user, request.POST, instance=group, initial={"group_list": group.group_list}
        )

        if form.is_valid():
            item = form.save(commit=False)
            item.note = bleach.clean(form.cleaned_data["note"], strip=True)
            item.title = bleach.clean(form.cleaned_data["title"], strip=True)
            item.save()
            messages.success(request, "The group has been edited.")
            return redirect(
                "groups:list_detail", list_id=group.group_list.id, list_slug=group.group_list.slug
            )

    # Mark complete
    if request.POST.get("toggle_done"):
        results_changed = toggle_group_completed(group.id)
        if results_changed:
            messages.success(request, f"Changed completion status for group {group.id}")

        return redirect("groups:group_detail", group_id=group.id)

    if group.due_date:
        thedate = group.due_date
    else:
        thedate = datetime.datetime.now()

    # Handle uploaded files
    if request.FILES.get("attachment_file_input"):
        file = request.FILES.get("attachment_file_input")

        if file.size > defaults("groups_MAXIMUM_ATTACHMENT_SIZE"):
            messages.error(request, f"File exceeds maximum attachment size.")
            return redirect("groups:group_detail", group_id=group.id)

        name, extension = os.path.splitext(file.name)

        if extension not in defaults("groups_LIMIT_FILE_ATTACHMENTS"):
            messages.error(request, f"This site does not allow upload of {extension} files.")
            return redirect("groups:group_detail", group_id=group.id)

        Attachment.objects.create(
            group=group, added_by=request.user, timestamp=datetime.datetime.now(), file=file
        )
        messages.success(request, f"File attached successfully")
        return redirect("groups:group_detail", group_id=group.id)

    context = {
        "group": group,
        "comment_list": comment_list,
        "form": form,
        "merge_form": merge_form,
        "thedate": thedate,
        "comment_classes": defaults("groups_COMMENT_CLASSES"),
        "attachments_enabled": defaults("groups_ALLOW_FILE_ATTACHMENTS"),
    }

    return render(request, "groups/group_detail.html", context)
