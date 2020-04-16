from django.conf import settings
from django.urls import path

from groups import views
from groups.features import HAS_group_MERGE

app_name = "groups"


urlpatterns = [
    path("", views.list_lists, name="lists"),
    # View reorder_Groups is only called by JQuery for drag/drop group ordering.
    path("reorder_Groups/", views.reorder_Groups, name="reorder_Groups"),
    # Allow users to post Groups from outside django-groups (e.g. for filing tickets - see docs)
    path("ticket/add/", views.external_add, name="external_add"),
    # Three paths into `list_detail` view
    path("mine/", views.list_detail, {"list_slug": "mine"}, name="mine"),
    path(
        "<int:list_id>/<str:list_slug>/completed/",
        views.list_detail,
        {"view_completed": True},
        name="list_detail_completed",
    ),
    path("<int:list_id>/<str:list_slug>/", views.list_detail, name="list_detail"),
    path("<int:list_id>/<str:list_slug>/delete/", views.del_list, name="del_list"),
    path("add_list/", views.add_list, name="add_list"),
    path("group/<int:group_id>/", views.group_detail, name="group_detail"),
    path(
        "attachment/remove/<int:attachment_id>/", views.remove_attachment, name="remove_attachment"
    ),
]

if HAS_group_MERGE:
    # ensure mail tracker autocomplete is optional
    from groups.views.group_autocomplete import groupAutocomplete

    urlpatterns.append(
        path(
            "group/<int:group_id>/autocomplete/", groupAutocomplete.as_view(), name="group_autocomplete"
        )
    )

urlpatterns.extend(
    [
        path("toggle_done/<int:group_id>/", views.toggle_done, name="group_toggle_done"),
        path("delete/<int:group_id>/", views.delete_group, name="delete_group"),
        path("search/", views.search, name="search"),
        path("import_csv/", views.import_csv, name="import_csv"),
    ]
)
