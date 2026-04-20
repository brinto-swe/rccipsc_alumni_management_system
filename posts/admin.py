from django.contrib import admin

from posts.models import Comment, Post, PostMedia, Reaction, Report


class PostMediaInline(admin.TabularInline):
    model = PostMedia
    extra = 0


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["author", "visibility", "moderation_status", "is_published", "published_at"]
    search_fields = ["author__email", "author__profile__full_name", "content"]
    list_filter = ["visibility", "moderation_status", "is_published"]
    readonly_fields = ["created_at", "updated_at", "deleted_at"]
    inlines = [PostMediaInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["post", "user", "parent", "moderation_status", "created_at"]
    search_fields = ["post__content", "user__email", "content"]
    list_filter = ["moderation_status", "created_at"]
    readonly_fields = ["created_at", "updated_at", "deleted_at"]


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ["post", "user", "reaction_type", "created_at"]
    search_fields = ["post__content", "user__email"]
    list_filter = ["reaction_type", "created_at"]


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ["reporter", "status", "reviewed_by", "created_at"]
    search_fields = ["reporter__email", "reason", "resolution_note"]
    list_filter = ["status", "created_at"]
    readonly_fields = ["created_at", "updated_at", "reviewed_at"]
