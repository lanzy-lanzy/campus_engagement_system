from django.urls import path

from . import views

app_name = "interactions"

urlpatterns = [
    path("posts/<int:post_id>/react/<str:kind>/", views.toggle_reaction, name="toggle_reaction"),
    path("posts/<int:post_id>/reaction-bar/", views.get_reaction_bar, name="get_reaction_bar"),
    path("posts/<int:post_id>/comments/", views.add_comment, name="add_comment"),
    path("comments/<int:comment_id>/delete/", views.delete_comment, name="delete_comment"),
    path("comments/<int:comment_id>/hide/", views.hide_comment, name="hide_comment"),
    path("comments/<int:comment_id>/react/<str:kind>/", views.toggle_comment_reaction, name="toggle_comment_reaction"),
    path("comments/<int:comment_id>/reply/", views.add_reply, name="add_reply"),
    path("posts/<int:post_id>/report/", views.report_post, name="report_post"),
    path("reports/<int:report_id>/<str:status>/", views.resolve_report, name="resolve_report"),
]