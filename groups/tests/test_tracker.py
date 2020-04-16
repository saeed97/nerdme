import pytest

from django.core import mail

from groups.models import group, Comment
from groups.mail.consumers import tracker_consumer
from email.message import EmailMessage


def consumer(*args, title_format="[TEST] {subject}", **kwargs):
    return tracker_consumer(
        group="Workgroup One", group_list_slug="zip", priority=1, group_title_format=title_format
    )(*args, **kwargs)


def make_message(subject, content):
    msg = EmailMessage()
    msg.set_content(content)
    msg["Subject"] = subject
    return msg


def test_tracker_group_creation(groups_setup, django_user_model):
    msg = make_message("test1 subject", "test1 content")
    msg["From"] = "test1@example.com"
    msg["Message-ID"] = "<a@example.com>"

    # test group creation
    group_count = group.objects.count()
    consumer([msg])

    assert group_count + 1 == group.objects.count(), "group wasn't created"
    group = group.objects.filter(title="[TEST] test1 subject").first()
    assert group is not None, "group was created with the wrong name"

    # test thread answers
    msg = make_message("test2 subject", "test2 content")
    msg["From"] = "test1@example.com"
    msg["Message-ID"] = "<b@example.com>"
    msg["References"] = "<nope@example.com> <a@example.com>"

    group_count = group.objects.count()
    consumer([msg])
    assert group_count == group.objects.count(), "comment created another group"
    Comment.objects.get(
        group=group, body__contains="test2 content", email_message_id="<b@example.com>"
    )

    # test notification answer
    msg = make_message("test3 subject", "test3 content")
    msg["From"] = "test1@example.com"
    msg["Message-ID"] = "<c@example.com>"
    msg["References"] = "<thread-{}@django-groups> <unknown@example.com>".format(group.pk)

    group_count = group.objects.count()
    consumer([msg])
    assert group_count == group.objects.count(), "comment created another group"
    Comment.objects.get(
        group=group, body__contains="test3 content", email_message_id="<c@example.com>"
    )
