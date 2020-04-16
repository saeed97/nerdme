from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from groups.models import group
from groups.utils import toggle_group_completed
from groups.utils import staff_check


@login_required
@user_passes_test(staff_check)
def toggle_done(request, group_id: int) -> HttpResponse:
    """Toggle the completed status of a group from done to undone, or vice versa.
    Redirect to the list from which the group came.
    """

    if request.method == "POST":
        group = get_object_or_404(group, pk=group_id)

        redir_url = reverse(
            "groups:list_detail",
            kwargs={"list_id": group.group_list.id, "list_slug": group.group_list.slug},
        )

        # Permissions
        if not (
            (group.created_by == request.user)
            or (request.user.is_superuser)
            or (group.assigned_to == request.user)
            or (group.group_list.group in request.user.groups.all())
        ):
            raise PermissionDenied

        toggle_group_completed(group.id)
        messages.success(request, "group status changed for '{}'".format(group.title))

        return redirect(redir_url)

    else:
        raise PermissionDenied
