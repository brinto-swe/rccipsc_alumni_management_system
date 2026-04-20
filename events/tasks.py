"""Async task hooks for events."""

from common.tasks import noop_async_hook


def queue_event_reminder(*args, **kwargs):
    return noop_async_hook(*args, **kwargs)
