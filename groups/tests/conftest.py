import pytest

from django.contrib.auth.models import Group

from groups.models import group, groupList


@pytest.fixture
def groups_setup(django_user_model):
    # Two groups with different users, two sets of Groups.

    g1 = Group.objects.create(name="Workgroup One")
    u1 = django_user_model.objects.create_user(
        username="u1", password="password", email="u1@example.com", is_staff=True
    )
    u1.groups.add(g1)
    tlist1 = groupList.objects.create(group=g1, name="Zip", slug="zip")
    group.objects.create(created_by=u1, title="group 1", group_list=tlist1, priority=1)
    group.objects.create(created_by=u1, title="group 2", group_list=tlist1, priority=2, completed=True)
    group.objects.create(created_by=u1, title="group 3", group_list=tlist1, priority=3)

    g2 = Group.objects.create(name="Workgroup Two")
    u2 = django_user_model.objects.create_user(
        username="u2", password="password", email="u2@example.com", is_staff=True
    )
    u2.groups.add(g2)
    tlist2 = groupList.objects.create(group=g2, name="Zap", slug="zap")
    group.objects.create(created_by=u2, title="group 1", group_list=tlist2, priority=1)
    group.objects.create(created_by=u2, title="group 2", group_list=tlist2, priority=2, completed=True)
    group.objects.create(created_by=u2, title="group 3", group_list=tlist2, priority=3)

    # Add a third user for a test that needs two users in the same group.
    extra_g2_user = django_user_model.objects.create_user(
        username="extra_g2_user", password="password", email="extra_g2_user@example.com", is_staff=True
    )
    extra_g2_user.groups.add(g2)


@pytest.fixture()
# Set up an in-memory mail server to receive test emails
def email_backend_setup(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
