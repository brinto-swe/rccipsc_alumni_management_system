"""Reusable DRF pagination classes."""

from rest_framework.pagination import PageNumberPagination


class DefaultPageNumberPagination(PageNumberPagination):
    """Default page-number pagination for list endpoints."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
