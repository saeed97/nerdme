from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from groups.models import StudentsGroups
from groups.utils import staff_check


@login_required
@user_passes_test(staff_check)
def delete_group(request, group_id: int) -> HttpResponse:
    """Delete specified group.
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

        group.delete()

        messages.success(request, "group '{}' has been deleted".format(group.title))
        return redirect(redir_url)

    else:
        raise PermissionDenied
