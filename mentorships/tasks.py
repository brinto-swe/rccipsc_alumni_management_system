"""Task placeholders for mentorship reminders and async actions."""

from common.tasks import noop_async_hook


def queue_mentorship_notification(*args, **kwargs):
    return noop_async_hook(*args, **kwargs)
