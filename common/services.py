"""Shared service helpers."""


def build_metadata(**kwargs) -> dict:
    """Strip empty values from metadata payloads before persistence."""

    return {key: value for key, value in kwargs.items() if value not in ("", None, [], {})}
