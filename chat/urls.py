from django.urls import path

from . import views

app_name = "chat"

urlpatterns = [
    path("", views.inbox, name="inbox"),
    path("with/<int:user_pk>/", views.start_conversation, name="start"),
    path("c/<int:pk>/", views.conversation_detail, name="conversation"),
    path("c/<int:pk>/send/", views.send_message, name="send"),
]
