from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from groups.models import group, groupList
from groups.utils import staff_check


@login_required
@user_passes_test(staff_check)
def del_list(request, list_id: int, list_slug: str) -> HttpResponse:
    """Delete an entire list. Only staff members should be allowed to access this view.
    """
    group_list = get_object_or_404(groupList, id=list_id)

    # Ensure user has permission to delete list. Get the group this list belongs to,
    # and check whether current user is a member of that group AND a staffer.
    if group_list.group not in request.user.groups.all():
        raise PermissionDenied    
    if not request.user.is_staff:
        raise PermissionDenied

    if request.method == "POST":
        groupList.objects.get(id=group_list.id).delete()
        messages.success(request, "{list_name} is gone.".format(list_name=group_list.name))
        return redirect("groups:lists")
    else:
        group_count_done = group.objects.filter(group_list=group_list.id, completed=True).count()
        group_count_undone = group.objects.filter(group_list=group_list.id, completed=False).count()
        group_count_total = group.objects.filter(group_list=group_list.id).count()

    context = {
        "group_list": group_list,
        "group_count_done": group_count_done,
        "group_count_undone": group_count_undone,
        "group_count_total": group_count_total,
    }

    return render(request, "groups/del_list.html", context)
