from dal import autocomplete
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from groups.models import group
from groups.utils import user_can_read_group


class groupAutocomplete(autocomplete.Select2QuerySetView):
    @method_decorator(login_required)
    def dispatch(self, request, group_id, *args, **kwargs):
        self.group = get_object_or_404(group, pk=group_id)
        if not user_can_read_group(self.group, request.user):
            raise PermissionDenied

        return super().dispatch(request, group_id, *args, **kwargs)

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return group.objects.none()

        qs = group.objects.filter(group_list=self.group.group_list).exclude(pk=self.group.pk)

        if self.q:
            qs = qs.filter(title__istartswith=self.q)

        return qs
