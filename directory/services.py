"""Service helpers for directory use cases."""


def build_directory_ordering(ordering_param: str | None) -> str:
    return ordering_param or "full_name"
