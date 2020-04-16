from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string

from groups.defaults import defaults
from groups.forms import AddExternalgroupForm
from groups.models import groupList
from groups.utils import staff_check


@login_required
@user_passes_test(staff_check)
def external_add(request) -> HttpResponse:
    """Allow authenticated users who don't have access to the rest of the ticket system to file a ticket
    in the list specified in settings (e.g. django-groups can be used a ticket filing system for a school, where
    students can file tickets without access to the rest of the groups system).

    Publicly filed tickets are unassigned unless settings.DEFAULT_ASSIGNEE exists.
    """

    if not settings.groups_DEFAULT_LIST_SLUG:
        # We do NOT provide a default in defaults
        raise RuntimeError(
            "This feature requires groups_DEFAULT_LIST_SLUG: in settings. See documentation."
        )

    if not groupList.objects.filter(slug=settings.groups_DEFAULT_LIST_SLUG).exists():
        raise RuntimeError(
            "There is no groupList with slug specified for groups_DEFAULT_LIST_SLUG in settings."
        )

    if request.POST:
        form = AddExternalgroupForm(request.POST)

        if form.is_valid():
            current_site = Site.objects.get_current()
            group = form.save(commit=False)
            group.group_list = groupList.objects.get(slug=settings.groups_DEFAULT_LIST_SLUG)
            group.created_by = request.user
            if defaults("groups_DEFAULT_ASSIGNEE"):
                group.assigned_to = get_user_model().objects.get(username=settings.groups_DEFAULT_ASSIGNEE)
            group.save()

            # Send email to assignee if we have one
            if group.assigned_to:
                email_subject = render_to_string(
                    "groups/email/assigned_subject.txt", {"group": group.title}
                )
                email_body = render_to_string(
                    "groups/email/assigned_body.txt", {"group": group, "site": current_site}
                )
                try:
                    send_mail(
                        email_subject,
                        email_body,
                        group.created_by.email,
                        [group.assigned_to.email],
                        fail_silently=False,
                    )
                except ConnectionRefusedError:
                    messages.warning(
                        request, "group saved but mail not sent. Contact your administrator."
                    )

            messages.success(
                request, "Your trouble ticket has been submitted. We'll get back to you soon."
            )
            return redirect(defaults("groups_PUBLIC_SUBMIT_REDIRECT"))

    else:
        form = AddExternalgroupForm(initial={"priority": 999})

    context = {"form": form}

    return render(request, "groups/add_group_external.html", context)
