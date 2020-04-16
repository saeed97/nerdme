import bleach
import pytest

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse

from groups.models import group, groupList

"""
First the "smoketests" - do they respond at all for a logged in admin user?
Next permissions tests - some views should respond for staffers only.
After that, view contents and behaviors.
"""


@pytest.mark.django_db
def test_groups_setup(groups_setup):
    assert group.objects.all().count() == 6


def test_view_list_lists(groups_setup, admin_client):
    url = reverse("groups:lists")
    response = admin_client.get(url)
    assert response.status_code == 200


def test_view_reorder(groups_setup, admin_client):
    url = reverse("groups:reorder_Groups")
    response = admin_client.get(url)
    assert response.status_code == 201  # Special case return value expected


def test_view_external_add(groups_setup, admin_client, settings):
    default_list = groupList.objects.first()
    settings.groups_DEFAULT_LIST_SLUG = default_list.slug
    assert settings.groups_DEFAULT_LIST_SLUG == default_list.slug
    url = reverse("groups:external_add")
    response = admin_client.get(url)
    assert response.status_code == 200


def test_view_mine(groups_setup, admin_client):
    url = reverse("groups:mine")
    response = admin_client.get(url)
    assert response.status_code == 200


def test_view_list_completed(groups_setup, admin_client):
    tlist = groupList.objects.get(slug="zip")
    url = reverse(
        "groups:list_detail_completed", kwargs={"list_id": tlist.id, "list_slug": tlist.slug}
    )
    response = admin_client.get(url)
    assert response.status_code == 200


def test_view_list(groups_setup, admin_client):
    tlist = groupList.objects.get(slug="zip")
    url = reverse("groups:list_detail", kwargs={"list_id": tlist.id, "list_slug": tlist.slug})
    response = admin_client.get(url)
    assert response.status_code == 200


def test_view_add_list(groups_setup, admin_client):
    url = reverse("groups:add_list")
    response = admin_client.get(url)
    assert response.status_code == 200


def test_view_group_detail(groups_setup, admin_client):
    group = group.objects.first()
    url = reverse("groups:group_detail", kwargs={"group_id": group.id})
    response = admin_client.get(url)
    assert response.status_code == 200


def test_del_group(groups_setup, admin_user, client):
    group = group.objects.first()
    url = reverse("groups:delete_group", kwargs={"group_id": group.id})
    # View accepts POST, not GET
    client.login(username="admin", password="password")
    response = client.get(url)
    assert response.status_code == 403
    response = client.post(url)
    assert not group.objects.filter(id=group.id).exists()


def test_group_toggle_done(groups_setup, admin_user, client):
    group = group.objects.first()
    assert not group.completed
    url = reverse("groups:group_toggle_done", kwargs={"group_id": group.id})
    # View accepts POST, not GET
    client.login(username="admin", password="password")
    response = client.get(url)
    assert response.status_code == 403

    client.post(url)
    group.refresh_from_db()
    assert group.completed


def test_view_search(groups_setup, admin_client):
    url = reverse("groups:search")
    response = admin_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_no_javascript_in_group_note(groups_setup, client):
    group_list = groupList.objects.first()
    user = get_user_model().objects.get(username="u2")
    title = "Some Unique String"
    note = "foo <script>alert('oh noez');</script> bar"
    data = {
        "group_list": group_list.id,
        "created_by": user.id,
        "priority": 10,
        "title": title,
        "note": note,
        "add_edit_group": "Submit",
    }

    client.login(username="u2", password="password")
    url = reverse("groups:list_detail", kwargs={"list_id": group_list.id, "list_slug": group_list.slug})

    response = client.post(url, data)
    assert response.status_code == 302

    # Retrieve new group and compare notes field
    group = group.objects.get(title=title)
    assert group.note != note  # Should have been modified by bleach since note included javascript!
    assert group.note == bleach.clean(note, strip=True)


@pytest.mark.django_db
def test_created_by_unchanged(groups_setup, client):

    group_list = groupList.objects.first()
    u2 = get_user_model().objects.get(username="u2")
    title = "Some Unique String with unique chars: ab78539e"
    note = "a note"
    data = {
        "group_list": group_list.id,
        "created_by": u2.id,
        "priority": 10,
        "title": title,
        "note": note,
        "add_edit_group": "Submit",
    }

    client.login(username="u2", password="password")
    url_add_group = reverse(
        "groups:list_detail", kwargs={"list_id": group_list.id, "list_slug": group_list.slug}
    )

    response = client.post(url_add_group, data)
    assert response.status_code == 302

    # Retrieve new group and compare created_by
    group = group.objects.get(title=title)
    assert group.created_by == u2

    # Now that we've created the group, edit it as another user.
    # After saving, created_by should remain unchanged.
    extra_g2_user = get_user_model().objects.get(username="extra_g2_user")

    client.login(username="extra_g2_user", password="password")

    url_edit_group = reverse("groups:group_detail", kwargs={"group_id": group.id})

    dataTwo = {
        "group_list": group.group_list.id,
        "created_by": extra_g2_user.id,  # this submission is attempting to change created_by
        "priority": 10,
        "title": group.title,
        "note": "the note was changed",
        "add_edit_group": "Submit",
    }

    response = client.post(url_edit_group, dataTwo)
    assert response.status_code == 302

    group.refresh_from_db()

    # Proof that the group was saved:
    assert group.note == "the note was changed"

    # client was unable to modify created_by:
    assert group.created_by == u2


@pytest.mark.django_db
@pytest.mark.parametrize("test_input, expected", [(True, True), (False, False)])
def test_completed_unchanged(test_input, expected, groups_setup, client):
    """Groups are marked completed/uncompleted by buttons,
    not via checkbox on the group edit form. Editing a group should
    not change its completed status. Test with both completed and incomplete Groups."""

    group = group.objects.get(title="group 1", created_by__username="u1")
    group.completed = test_input
    group.save()
    assert group.completed == expected

    url_edit_group = reverse("groups:group_detail", kwargs={"group_id": group.id})

    data = {
        "group_list": group.group_list.id,
        "title": "Something",
        "note": "the note was changed",
        "add_edit_group": "Submit",
        "completed": group.completed,
    }

    client.login(username="u1", password="password")
    response = client.post(url_edit_group, data)
    assert response.status_code == 302

    # Prove the group is still marked complete/incomplete
    # (despite the default default state for completed being False)
    group.refresh_from_db()
    assert group.completed == expected


@pytest.mark.django_db
def test_no_javascript_in_members(groups_setup, client):
    user = get_user_model().objects.get(username="u2")
    client.login(username="u2", password="password")

    group = group.objects.first()
    group.created_by = user
    group.save()

    user.groups.add(group.group_list.group)

    comment = "foo <script>alert('oh noez');</script> bar"
    data = {"comment-body": comment, "add_comment": "Submit"}
    url = reverse("groups:group_detail", kwargs={"group_id": group.id})

    response = client.post(url, data)
    assert response.status_code == 200

    group.refresh_from_db()
    newcomment = group.comment_set.last()
    assert newcomment != comment  # Should have been modified by bleach
    assert newcomment.body == bleach.clean(comment, strip=True)


# ### PERMISSIONS ###


def test_view_add_list_nonadmin(groups_setup, client):
    url = reverse("groups:add_list")
    client.login(username="you", password="password")
    response = client.get(url)
    assert response.status_code == 302  # Redirected to login


def test_view_del_list_nonadmin(groups_setup, client):
    tlist = groupList.objects.get(slug="zip")
    url = reverse("groups:del_list", kwargs={"list_id": tlist.id, "list_slug": tlist.slug})
    client.login(username="you", password="password")
    response = client.get(url)
    assert response.status_code == 302  # Fedirected to login


def test_del_list_not_in_list_group(groups_setup, admin_client):
    tlist = groupList.objects.get(slug="zip")
    url = reverse("groups:del_list", kwargs={"list_id": tlist.id, "list_slug": tlist.slug})
    response = admin_client.get(url)
    assert response.status_code == 403


def test_view_list_mine(groups_setup, client):
    """View a list in a group I belong to.
    """
    tlist = groupList.objects.get(slug="zip")  # User u1 is in this group's list
    url = reverse("groups:list_detail", kwargs={"list_id": tlist.id, "list_slug": tlist.slug})
    client.login(username="u1", password="password")
    response = client.get(url)
    assert response.status_code == 200


def test_view_list_not_mine(groups_setup, client):
    """View a list in a group I don't belong to.
    """
    tlist = groupList.objects.get(slug="zip")  # User u1 is in this group, user u2 is not.
    url = reverse("groups:list_detail", kwargs={"list_id": tlist.id, "list_slug": tlist.slug})
    client.login(username="u2", password="password")
    response = client.get(url)
    assert response.status_code == 403


def test_view_group_mine(groups_setup, client):
    # Users can always view their own Groups
    group = group.objects.filter(created_by__username="u1").first()
    client.login(username="u1", password="password")
    url = reverse("groups:group_detail", kwargs={"group_id": group.id})
    response = client.get(url)
    assert response.status_code == 200


def test_view_group_my_group(groups_setup, client, django_user_model):
    """User can always view Groups that are NOT theirs IF the group is in a shared group.
    u1 and u2 are in different groups in the fixture -
    Put them in the same group."""
    g1 = Group.objects.get(name="Workgroup One")
    u2 = django_user_model.objects.get(username="u2")
    u2.groups.add(g1)

    # Now u2 should be able to view one of u1's Groups.
    group = group.objects.filter(created_by__username="u1").first()
    url = reverse("groups:group_detail", kwargs={"group_id": group.id})
    client.login(username="u2", password="password")
    response = client.get(url)
    assert response.status_code == 200


def test_view_group_not_in_my_group(groups_setup, client):
    # User canNOT view a group that isn't theirs if the two users are not in a shared group.
    # For this we can use the fixture data as-is.
    group = group.objects.filter(created_by__username="u1").first()
    url = reverse("groups:group_detail", kwargs={"group_id": group.id})
    client.login(username="u2", password="password")
    response = client.get(url)
    assert response.status_code == 403


def test_setting_groups_STAFF_ONLY_False(groups_setup, client, settings):
    # We use Django's user_passes_test to call `staff_check` utility function on all views.
    # Just testing one view here; if it works, it works for all of them.
    settings.groups_STAFF_ONLY = False
    url = reverse("groups:lists")
    client.login(username="u2", password="password")
    response = client.get(url)
    assert response.status_code == 200


def test_setting_groups_STAFF_ONLY_True(groups_setup, client, settings, django_user_model):
    # We use Django's user_passes_test to call `staff_check` utility function on some views.
    # Just testing one view here...
    settings.groups_STAFF_ONLY = True
    url = reverse("groups:lists")

    # Remove staff privileges from user u2; they should not be able to access
    u2 = django_user_model.objects.get(username="u2")
    u2.is_staff = False
    u2.save()

    client.login(username="u2", password="password")
    response = client.get(url)
    assert response.status_code == 302  # Redirected to login view
