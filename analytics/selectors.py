"""Selectors for analytics aggregates."""

from decimal import Decimal

from events.models import EventRegistration
from mentorships.models import MentorshipRequest
from posts.models import Comment, Post, Reaction
from users.enums import AccountStatus, UserRole
from users.models import User


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
