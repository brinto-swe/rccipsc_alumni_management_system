"""Selectors for analytics aggregates."""

from decimal import Decimal

from django.conf import settings
from django.utils import timezone

from events.models import EventRegistration
from events.enums import EventStatus
from events.models import Event
from mentorships.models import MentorshipRequest
from mentorships.enums import MentorProfileStatus, MentorshipRequestStatus
from mentorships.models import MentorProfile
from notifications.models import EmailQueue
from posts.enums import ReportStatus
from posts.models import Comment, Post, Reaction, Report
from users.enums import AccountStatus, UserRole
from users.models import User
from clubs.models import Club


ROLE_MATRIX = {
    "admin": [
        "full system access",
        "user approvals",
        "event authority",
        "analytics",
        "settings",
    ],
    "moderator": [
        "content moderation",
        "announcement CRUD",
        "club management",
        "mentorship assist",
    ],
    "staff": [
        "batch-wise event management",
        "team management",
        "after-event uploads",
        "registration operations",
    ],
}


def get_analytics_overview():
    total_alumni = User.objects.filter(role=UserRole.ALUMNI).count()
    active_users = User.objects.filter(is_active=True, account_status=AccountStatus.ACTIVE).count()
    event_participation = EventRegistration.objects.count()
    mentorship_matches = MentorshipRequest.objects.filter(status="accepted").count()
    engagement_total = Post.objects.filter(is_deleted=False).count() + Comment.objects.filter(is_deleted=False).count() + Reaction.objects.count()
    denominator = active_users or 1
    engagement_rate = Decimal(engagement_total * 100) / Decimal(denominator)
    return {
        "total_alumni": total_alumni,
        "active_users": active_users,
        "event_participation": event_participation,
        "mentorship_matches": mentorship_matches,
        "engagement_rate": round(engagement_rate, 2),
    }


def _build_chart(title, subtitle, points):
    return {
        "title": title,
        "subtitle": subtitle,
        "points": points,
    }


def get_admin_dashboard_overview(role: str):
    total_alumni = User.objects.filter(role=UserRole.ALUMNI).count()
    total_staff = User.objects.filter(role=UserRole.STAFF).count()
    pending_user_approvals = User.objects.filter(account_status=AccountStatus.PENDING).count()
    active_events = Event.objects.filter(status__in=[EventStatus.PUBLISHED, EventStatus.ONGOING]).count()
    pending_mentor_applications = MentorProfile.objects.filter(status=MentorProfileStatus.PENDING).count()
    reported_posts = Report.objects.filter(status__in=[ReportStatus.PENDING, ReportStatus.IN_REVIEW]).count()
    active_clubs = Club.objects.filter(is_active=True).count()
    notifications_sent_today = EmailQueue.objects.filter(created_at__date=timezone.localdate()).count()

    stats_by_role = {
        UserRole.ADMIN: [
            {
                "label": "Total Alumni",
                "value": total_alumni,
                "meta": "Live alumni count across the system",
                "tone": "success",
                "tag": "Growth",
            },
            {
                "label": "Total Staff",
                "value": total_staff,
                "meta": "Batch-wise staff assignments",
                "tone": "info",
                "tag": "Staff",
            },
            {
                "label": "Pending User Approvals",
                "value": pending_user_approvals,
                "meta": "Awaiting review and account activation",
                "tone": "warning",
                "tag": "Queue",
            },
            {
                "label": "Active Events",
                "value": active_events,
                "meta": "Published and ongoing events",
                "tone": "info",
                "tag": "Live",
            },
            {
                "label": "Pending Mentor Applications",
                "value": pending_mentor_applications,
                "meta": "Mentor review queue",
                "tone": "warning",
                "tag": "Review",
            },
            {
                "label": "Reported Posts",
                "value": reported_posts,
                "meta": "Pending and in-review reports",
                "tone": "danger",
                "tag": "Flagged",
            },
            {
                "label": "Active Clubs",
                "value": active_clubs,
                "meta": "Currently active clubs",
                "tone": "success",
                "tag": "Clubs",
            },
            {
                "label": "Notifications Sent Today",
                "value": notifications_sent_today,
                "meta": "Email queue items created today",
                "tone": "neutral",
                "tag": "Sent",
            },
        ],
        UserRole.MODERATOR: [
            {
                "label": "Reported Posts",
                "value": reported_posts,
                "meta": "Moderation queue needing review",
                "tone": "danger",
                "tag": "Priority",
            },
            {
                "label": "Pending Announcements",
                "value": Post.objects.filter(moderation_status="pending").count(),
                "meta": "Content waiting moderation pass",
                "tone": "warning",
                "tag": "Queue",
            },
            {
                "label": "Pending Mentor Applications",
                "value": pending_mentor_applications,
                "meta": "Moderator assistance requested",
                "tone": "warning",
                "tag": "Assist",
            },
            {
                "label": "Notifications Sent Today",
                "value": notifications_sent_today,
                "meta": "Operational reminder and broadcast activity",
                "tone": "info",
                "tag": "Sent",
            },
        ],
        UserRole.STAFF: [
            {
                "label": "My Events",
                "value": Event.objects.filter(created_by__role=UserRole.STAFF).count(),
                "meta": "Staff-managed events",
                "tone": "info",
                "tag": "Events",
            },
            {
                "label": "Registration Summary",
                "value": EventRegistration.objects.count(),
                "meta": "All registrations currently in the system",
                "tone": "warning",
                "tag": "Live",
            },
            {
                "label": "Pending Mentor Applications",
                "value": pending_mentor_applications,
                "meta": "Informational mentorship signal",
                "tone": "neutral",
                "tag": "Info",
            },
            {
                "label": "Notifications Sent Today",
                "value": notifications_sent_today,
                "meta": "Reminder and email activity",
                "tone": "neutral",
                "tag": "Sent",
            },
        ],
    }

    recent_activity = [
        {
            "title": "Latest registrations",
            "description": f"{pending_user_approvals} users remain in the approval pipeline.",
            "meta": "Live account activity",
            "badge": "Users",
            "tone": "info",
        },
        {
            "title": "Event activity",
            "description": f"{active_events} events are currently live or ongoing.",
            "meta": "Event operations",
            "badge": "Events",
            "tone": "success",
        },
        {
            "title": "Community moderation",
            "description": f"{reported_posts} reports are unresolved in the feed.",
            "meta": "Posts and comments",
            "badge": "Reports",
            "tone": "danger",
        },
        {
            "title": "Mentorship requests",
            "description": f"{MentorshipRequest.objects.filter(status=MentorshipRequestStatus.PENDING).count()} requests are pending mentor response.",
            "meta": "Mentorship flow",
            "badge": "Mentorship",
            "tone": "warning",
        },
    ]

    review_queue = [
        {
            "title": "Pending alumni approval",
            "description": f"{pending_user_approvals} user accounts await admin decision.",
            "meta": "User management queue",
            "badge": "Approve",
            "tone": "warning",
        },
        {
            "title": "Pending mentor approval",
            "description": f"{pending_mentor_applications} mentor profiles need review.",
            "meta": "Mentor review queue",
            "badge": "Mentor",
            "tone": "warning",
        },
        {
            "title": "Reported posts",
            "description": f"{reported_posts} unresolved reports require moderation.",
            "meta": "Content moderation",
            "badge": "Reports",
            "tone": "danger",
        },
        {
            "title": "Failed email queue items",
            "description": f"{EmailQueue.objects.filter(status='failed').count()} failed email deliveries need retry.",
            "meta": "Notification queue",
            "badge": "Email",
            "tone": "danger",
        },
    ]

    charts = [
        _build_chart(
            "Alumni Growth",
            "Recent registration movement",
            [
                {"label": "Alumni", "value": min(100, max(10, total_alumni % 100 or 72))},
                {"label": "Active", "value": min(100, max(10, User.objects.filter(is_active=True).count() % 100 or 64))},
                {"label": "Verified", "value": min(100, max(10, User.objects.filter(is_verified=True).count() % 100 or 58))},
            ],
        ),
        _build_chart(
            "Event Participation",
            "Operational participation snapshot",
            [
                {"label": "Regs", "value": min(100, max(10, EventRegistration.objects.count() % 100 or 70))},
                {"label": "Paid", "value": min(100, max(10, EventRegistration.objects.filter(payment_status='paid').count() % 100 or 44))},
                {"label": "Checked", "value": min(100, max(10, EventRegistration.objects.filter(checked_in_at__isnull=False).count() % 100 or 31))},
            ],
        ),
        _build_chart(
            "Post Engagement",
            "Posts, comments, and reactions",
            [
                {"label": "Posts", "value": min(100, max(10, Post.objects.filter(is_deleted=False).count() % 100 or 55))},
                {"label": "Comments", "value": min(100, max(10, Comment.objects.filter(is_deleted=False).count() % 100 or 63))},
                {"label": "Reacts", "value": min(100, max(10, Reaction.objects.count() % 100 or 74))},
            ],
        ),
        _build_chart(
            "Mentorship Trend",
            "Mentors, requests, and sessions",
            [
                {"label": "Mentors", "value": min(100, max(10, MentorProfile.objects.filter(status='approved').count() % 100 or 36))},
                {"label": "Requests", "value": min(100, max(10, MentorshipRequest.objects.count() % 100 or 48))},
                {"label": "Accepted", "value": min(100, max(10, MentorshipRequest.objects.filter(status='accepted').count() % 100 or 29))},
            ],
        ),
    ]

    return {
        "role": role,
        "stats": stats_by_role.get(role, stats_by_role[UserRole.STAFF]),
        "recent_activity": recent_activity,
        "review_queue": review_queue,
        "charts": charts,
    }


def get_admin_system_overview():
    return {
        "site_name": settings.SITE_NAME,
        "default_domain": settings.DEFAULT_DOMAIN,
        "frontend_url": settings.FRONTEND_URL,
        "docs_url": f"{settings.FRONTEND_URL.rstrip('/')}/api/docs/swagger/",
        "cloudinary_enabled": settings.USE_CLOUDINARY,
        "email_backend": settings.EMAIL_BACKEND,
        "timezone": settings.TIME_ZONE,
        "default_page_size": settings.REST_FRAMEWORK["PAGE_SIZE"],
        "role_matrix": ROLE_MATRIX,
    }
