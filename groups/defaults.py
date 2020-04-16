# If a documented django-groups option is NOT configured in settings, use these values.
from django.conf import settings

hash = {
    "groups_ALLOW_FILE_ATTACHMENTS": True,
    "groups_COMMENT_CLASSES": [],
    "groups_DEFAULT_ASSIGNEE": None,
    "groups_LIMIT_FILE_ATTACHMENTS": [".jpg", ".gif", ".png", ".csv", ".pdf", ".zip"],
    "groups_MAXIMUM_ATTACHMENT_SIZE": 5000000,
    "groups_PUBLIC_SUBMIT_REDIRECT": "/",
    "groups_STAFF_ONLY": True,
}

# These intentionally have no defaults (user MUST set a value if their features are used):
# groups_DEFAULT_LIST_SLUG
# groups_MAIL_BACKENDS
# groups_MAIL_TRACKERS


def defaults(key: str):
    """Try to get a setting from project settings.
    If empty or doesn't exist, fall back to a value from defaults hash."""

    if hasattr(settings, key):
        val = getattr(settings, key)
    else:
        val = hash.get(key)
    return val
