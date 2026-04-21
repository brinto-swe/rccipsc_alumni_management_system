"""Reusable serializer fields for Cloudinary-backed uploads."""

from rest_framework import serializers


def _cloudinary_asset_url(value):
    if not value:
        return None

    if hasattr(value, "url"):
        return value.url

    if hasattr(value, "build_url"):
        return value.build_url()

    return str(value)


class CloudinaryImageSerializerField(serializers.ImageField):
    """Accept uploaded images and always serialize them as a resolved URL."""

    def to_representation(self, value):
        return _cloudinary_asset_url(value)


class CloudinaryFileSerializerField(serializers.FileField):
    """Accept uploaded files and always serialize them as a resolved URL."""

    def to_representation(self, value):
        return _cloudinary_asset_url(value)
