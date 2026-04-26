from django.contrib import admin

from .models import Comment, Reaction, Report


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("body", "author__username", "post__title")


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ("post", "user", "kind", "created_at")
    list_filter = ("kind", "created_at")


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("post", "comment", "reporter", "reason", "status", "created_at")
    list_filter = ("reason", "status", "created_at")
    search_fields = ("post__title", "details", "reporter__username")