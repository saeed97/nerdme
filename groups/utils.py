import email.utils
import logging
import os
import time

from django.conf import settings
from django.contrib.sites.models import Site
from django.core import mail
from django.template.loader import render_to_string

from groups.defaults import defaults
from groups.models import Attachment, Comment, group

log = logging.getLogger(__name__)


def staff_check(user):
    """If groups_STAFF_ONLY is set to True, limit view access to staff users only.
        # FIXME: More granular access control needed - see
        https://github.com/shacker/django-groups/issues/50
    """

    if defaults("groups_STAFF_ONLY"):
        return user.is_staff
    else:
        # If unset or False, allow all logged in users
        return True


def user_can_read_group(group, user):
    return group.group_list.group in user.groups.all() or user.is_superuser


def groups_get_backend(group):
    """Returns a mail backend for some group"""
    mail_backends = getattr(settings, "groups_MAIL_BACKENDS", None)
    if mail_backends is None:
        return None

    group_backend = mail_backends[group.group_list.slug]
    if group_backend is None:
        return None

    return group_backend


def groups_get_mailer(user, group):
    """A mailer is a (from_address, backend) pair"""
    group_backend = groups_get_backend(group)
    if group_backend is None:
        return (None, mail.get_connection)

    from_address = getattr(group_backend, "from_address")
    from_address = email.utils.formataddr((user.username, from_address))
    return (from_address, group_backend)


def groups_send_mail(user, group, subject, body, recip_list):
    """Send an email attached to group, triggered by user"""
    references = Comment.objects.filter(group=group).only("email_message_id")
    references = (ref.email_message_id for ref in references)
    references = " ".join(filter(bool, references))

    from_address, backend = groups_get_mailer(user, group)
    message_hash = hash((subject, body, from_address, frozenset(recip_list), references))

    message_id = (
        # the group_id enables attaching back notification answers
        "<notif-{group_id}."
        # the message hash / epoch pair enables deduplication
        "{message_hash:x}."
        "{epoch}@django-groups>"
    ).format(
        group_id=group.pk,
        # avoid the -hexstring case (hashes can be negative)
        message_hash=abs(message_hash),
        epoch=int(time.time()),
    )

    # the thread message id is used as a common denominator between all
    # notifications for some group. This message doesn't actually exist,
    # it's just there to make threading possible
    thread_message_id = "<thread-{}@django-groups>".format(group.pk)
    references = "{} {}".format(references, thread_message_id)

    with backend() as connection:
        message = mail.EmailMessage(
            subject,
            body,
            from_address,
            recip_list,
            [],  # Bcc
            headers={
                **getattr(backend, "headers", {}),
                "Message-ID": message_id,
                "References": references,
                "In-reply-to": thread_message_id,
            },
            connection=connection,
        )
        message.send()


def send_notify_mail(new_group):
    """
    Send email to assignee if group is assigned to someone other than submittor.
    Unassigned Groups should not try to notify.
    """

    if new_group.assigned_to == new_group.created_by:
        return

    current_site = Site.objects.get_current()
    subject = render_to_string("groups/email/assigned_subject.txt", {"group": new_group})
    body = render_to_string(
        "groups/email/assigned_body.txt", {"group": new_group, "site": current_site}
    )

    recip_list = [new_group.assigned_to.email]
    groups_send_mail(new_group.created_by, new_group, subject, body, recip_list)


def send_email_to_thread_participants(group, msg_body, user, subject=None):
    """Notify all previous commentors on a group about a new comment."""

    current_site = Site.objects.get_current()
    email_subject = subject
    if not subject:
        subject = render_to_string("groups/email/assigned_subject.txt", {"group": group})

    email_body = render_to_string(
        "groups/email/newcomment_body.txt",
        {"group": group, "body": msg_body, "site": current_site, "user": user},
    )

    # Get all thread participants
    commenters = Comment.objects.filter(group=group)
    recip_list = set(ca.author.email for ca in commenters if ca.author is not None)
    for related_user in (group.created_by, group.assigned_to):
        if related_user is not None:
            recip_list.add(related_user.email)
    recip_list = list(m for m in recip_list if m)

    groups_send_mail(user, group, email_subject, email_body, recip_list)


def toggle_group_completed(group_id: int) -> bool:
    """Toggle the `completed` bool on group from True to False or vice versa."""
    try:
        group = group.objects.get(id=group_id)
        group.completed = not group.completed
        group.save()
        return True

    except group.DoesNotExist:
        log.info(f"group {group_id} not found.")
        return False


def remove_attachment_file(attachment_id: int) -> bool:
    """Delete an Attachment object and its corresponding file from the filesystem."""
    try:
        attachment = Attachment.objects.get(id=attachment_id)
        if attachment.file:
            if os.path.isfile(attachment.file.path):
                os.remove(attachment.file.path)

        attachment.delete()
        return True

    except Attachment.DoesNotExist:
        log.info(f"Attachment {attachment_id} not found.")
        return False
