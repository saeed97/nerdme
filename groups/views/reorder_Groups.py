from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from groups.models import StudentsGroups
from groups.utils import staff_check


@csrf_exempt
@login_required
@user_passes_test(staff_check)
def reorder_Groups(request) -> HttpResponse:
    """Handle group re-ordering (priorities) from JQuery drag/drop in list_detail.html
    """
    newgrouplist = request.POST.getlist("grouptable[]")
    if newgrouplist:
        # First group in received list is always empty - remove it
        del newgrouplist[0]

        # Re-prioritize each group in list
        i = 1
        for id in newgrouplist:
            try:
                group = group.objects.get(pk=id)
                group.priority = i
                group.save()
                i += 1
            except group.DoesNotExist:
                # Can occur if group is deleted behind the scenes during re-ordering.
                # Not easy to remove it from the UI without page refresh, but prevent crash.
                pass

    # All views must return an httpresponse of some kind ... without this we get
    # error 500s in the log even though things look peachy in the browser.
    return HttpResponse(status=201)
