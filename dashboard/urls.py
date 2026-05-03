from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.index, name="index"),
    path("moderation/", views.moderation, name="moderation"),
    path("users/", views.user_list, name="users"),
    path("users/new/", views.user_create, name="user_create"),
    path("users/<int:user_id>/edit/", views.user_edit, name="user_edit"),
    path("users/<int:user_id>/delete/", views.user_delete, name="user_delete"),
    path("users/<int:user_id>/toggle/", views.user_toggle_active, name="user_toggle"),
    path("posts/", views.post_list, name="posts"),
    path("posts/<int:post_id>/edit/", views.post_edit, name="post_edit"),
    path("posts/<int:post_id>/delete/", views.post_delete, name="post_delete"),
    path("posts/<int:post_id>/status/", views.post_status, name="post_status"),
    path("analytics/", views.analytics, name="analytics"),
    path("settings/", views.settings, name="settings"),
]