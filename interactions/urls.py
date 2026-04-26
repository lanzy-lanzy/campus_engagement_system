from django.urls import path

from . import views

app_name = "interactions"

urlpatterns = [
    path("posts/<int:post_id>/react/<str:kind>/", views.toggle_reaction, name="toggle_reaction"),
    path("posts/<int:post_id>/comments/", views.add_comment, name="add_comment"),
    path("comments/<int:comment_id>/delete/", views.delete_comment, name="delete_comment"),
    path("posts/<int:post_id>/report/", views.report_post, name="report_post"),
    path("reports/<int:report_id>/<str:status>/", views.resolve_report, name="resolve_report"),
]