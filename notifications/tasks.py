"""Async hooks for future email and notification workers."""

from common.tasks import noop_async_hook


def dispatch_email_queue(*args, **kwargs):
    return noop_async_hook(*args, **kwargs)
