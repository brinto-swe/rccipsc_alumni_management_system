"""Root URL configuration."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", include("common.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/docs/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("api/auth/", include("accounts.urls")),
    path("api/users/", include("users.urls")),
    path("api/profiles/", include("profiles.urls")),
    path("api/professions/", include("professions.urls")),
    path("api/directory/", include("directory.urls")),
    path("api/events/", include("events.urls")),
    path("api/posts/", include("posts.urls")),
    path("api/clubs/", include("clubs.urls")),
    path("api/teams/", include("teams.urls")),
    path("api/announcements/", include("announcements.urls")),
    path("api/mentorship/", include("mentorships.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/admin/", include("users.admin_urls")),
    path("api/admin/", include("events.admin_urls")),
    path("api/admin/", include("posts.admin_urls")),
    path("api/admin/", include("notifications.admin_urls")),
    path("api/admin/", include("analytics.admin_urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
