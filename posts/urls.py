from django.urls import path

from . import views

app_name = "posts"

urlpatterns = [
    path("", views.feed, name="feed"),
    path("posts/new/", views.create_post, name="create"),
    path("posts/new/modal/", views.create_post_modal, name="create_modal"),
    path("posts/<int:pk>/share/", views.share_post, name="share"),
    path("posts/<int:pk>/modal/", views.post_modal, name="modal"),
    path("posts/<int:pk>/edit/", views.edit_post, name="edit"),
    path("posts/<int:pk>/delete/", views.delete_post, name="delete"),
]
