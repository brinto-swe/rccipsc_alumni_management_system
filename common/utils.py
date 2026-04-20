"""Shared utility functions."""

from pathlib import Path

from django.utils.deconstruct import deconstructible
from django.utils.text import slugify


@deconstructible
class UploadToPath:
    """Reusable upload path generator that is safe to serialize into migrations."""

    def __init__(self, *segments: str):
        self.segments = segments

    def __call__(self, instance, filename: str) -> str:
        suffix = Path(filename).suffix.lower()
        model_name = instance.__class__.__name__.lower()
        identifier = getattr(instance, "id", "pending")
        base = "/".join(segment.strip("/") for segment in self.segments if segment)
        return f"{base}/{model_name}/{identifier}{suffix}"


def upload_to(*segments: str) -> UploadToPath:
    return UploadToPath(*segments)


def generate_slug(value: str) -> str:
    return slugify(value).strip("-")


def mask_string(value: str, keep: int = 3) -> str:
    if not value:
        return value
    if len(value) <= keep:
        return "*" * len(value)
    return value[:keep] + "*" * (len(value) - keep)
