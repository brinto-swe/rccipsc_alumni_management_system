"""Shared task placeholders for future Celery integration."""


def noop_async_hook(*args, **kwargs):
    """Placeholder callable kept so async workflows can be plugged in later."""

    return {"args": args, "kwargs": kwargs, "queued": False}
