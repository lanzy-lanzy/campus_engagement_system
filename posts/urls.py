from django.urls import path

from . import views

app_name = "posts"

urlpatterns = [
    path("", views.feed, name="feed"),
    path("posts/new/", views.create_post, name="create"),
    path("posts/<int:pk>/share/", views.share_post, name="share"),
    path("posts/<int:pk>/edit/", views.edit_post, name="edit"),
    path("posts/<int:pk>/delete/", views.delete_post, name="delete"),
]
