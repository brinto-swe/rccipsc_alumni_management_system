"""Authentication and account-side services."""

from ipaddress import ip_address as parse_ip_address

from accounts.models import AccountAuditLog


def normalize_ip_address(value):
    """Return a database-safe IP string or ``None`` for invalid proxy values."""

    if not value:
        return None

    candidate = str(value).strip()
    if not candidate:
        return None

    # Proxy chains often arrive as "client, proxy1, proxy2" - keep the client IP.
    if "," in candidate:
        candidate = candidate.split(",", 1)[0].strip()

    # IPv4 addresses may include a port in some runtimes: "203.0.113.10:443".
    if "." in candidate and candidate.count(":") == 1:
        candidate = candidate.rsplit(":", 1)[0].strip()

    # Bracketed IPv6 forms can include a port, e.g. "[2001:db8::1]:443".
    if candidate.startswith("[") and "]" in candidate:
        candidate = candidate[1 : candidate.index("]")]

    try:
        return str(parse_ip_address(candidate))
    except ValueError:
        return None


def record_account_audit(*, action: str, actor=None, target_user=None, message: str = "", metadata=None, ip_address=None):
    return AccountAuditLog.objects.create(
        action=action,
        actor=actor,
        target_user=target_user,
        message=message,
        metadata=metadata or {},
        ip_address=normalize_ip_address(ip_address),
    )
