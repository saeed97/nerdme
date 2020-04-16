import bleach
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from groups.forms import AddEditgroupForm
from groups.models import group, groupList
from groups.utils import send_notify_mail, staff_check


@login_required
@user_passes_test(staff_check)
def list_detail(request, list_id=None, list_slug=None, view_completed=False) -> HttpResponse:
    """Display and manage Groups in a groups list.
    """

    # Defaults
    group_list = None
    form = None

    # Which Groups to show on this list view?
    if list_slug == "mine":
        Groups = group.objects.filter(assigned_to=request.user)

    else:
        # Show a specific list, ensuring permissions.
        group_list = get_object_or_404(groupList, id=list_id)
        if group_list.group not in request.user.groups.all() and not request.user.is_superuser:
            raise PermissionDenied
        Groups = group.objects.filter(group_list=group_list.id)

    # Additional filtering
    if view_completed:
        Groups = Groups.filter(completed=True)
    else:
        Groups = Groups.filter(completed=False)

    # ######################
    #  Add New group Form
    # ######################

    if request.POST.getlist("add_edit_group"):
        form = AddEditgroupForm(
            request.user,
            request.POST,
            initial={"assigned_to": request.user.id, "priority": 999, "group_list": group_list},
        )

        if form.is_valid():
            new_group = form.save(commit=False)
            new_group.created_by = request.user
            new_group.note = bleach.clean(form.cleaned_data["note"], strip=True)
            form.save()

            # Send email alert only if Notify checkbox is checked AND assignee is not same as the submitter
            if (
                "notify" in request.POST
                and new_group.assigned_to
                and new_group.assigned_to != request.user
            ):
                send_notify_mail(new_group)

            messages.success(request, 'New group "{t}" has been added.'.format(t=new_group.title))
            return redirect(request.path)
    else:
        # Don't allow adding new Groups on some views
        if list_slug not in ["mine", "recent-add", "recent-complete"]:
            form = AddEditgroupForm(
                request.user,
                initial={"assigned_to": request.user.id, "priority": 999, "group_list": group_list},
            )

    context = {
        "list_id": list_id,
        "list_slug": list_slug,
        "group_list": group_list,
        "form": form,
        "Groups": Groups,
        "view_completed": view_completed,
    }

    return render(request, "groups/list_detail.html", context)
