from django.contrib import admin

from groups.models import Attachment, Comment, group, groupList


class groupAdmin(admin.ModelAdmin):
    list_display = ("title", "group_list", "completed", "priority", "due_date")
    list_filter = ("group_list",)
    ordering = ("priority",)
    search_fields = ("title",)


class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "date", "snippet")


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("group", "added_by", "timestamp", "file")
    autocomplete_fields = ["added_by", "group"]


admin.site.register(groupList)
admin.site.register(Comment, CommentAdmin)
admin.site.register(group, groupAdmin)
admin.site.register(Attachment, AttachmentAdmin)
