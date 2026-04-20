"""Reusable validators for uploads and date ranges."""

from datetime import date
from pathlib import Path

from django.core.exceptions import ValidationError

from .constants import (
    DOCUMENT_EXTENSIONS,
    IMAGE_EXTENSIONS,
    MAX_DOCUMENT_SIZE_MB,
    MAX_IMAGE_SIZE_MB,
)


def _validate_size(value, max_size_mb: int, label: str):
    if value.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"{label} size must not exceed {max_size_mb} MB.")


def _validate_extension(value, allowed_extensions: set[str], label: str):
    extension = Path(value.name).suffix.lower()
    if extension not in allowed_extensions:
        allowed = ", ".join(sorted(allowed_extensions))
        raise ValidationError(f"{label} must use one of: {allowed}.")


def validate_image_upload(value):
    _validate_size(value, MAX_IMAGE_SIZE_MB, "Image")
    _validate_extension(value, IMAGE_EXTENSIONS, "Image")


def validate_document_upload(value):
    _validate_size(value, MAX_DOCUMENT_SIZE_MB, "Document")
    _validate_extension(value, DOCUMENT_EXTENSIONS, "Document")


def validate_end_date_not_before_start(start_date: date, end_date: date | None, label: str):
    if end_date and start_date and end_date < start_date:
        raise ValidationError(f"{label} end date cannot be earlier than the start date.")
