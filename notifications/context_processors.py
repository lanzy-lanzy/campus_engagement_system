def navigation_badges(request):
    if not request.user.is_authenticated:
        return {"unread_message_count": 0, "unread_notification_count": 0}

    from chat.models import Message
    from notifications.models import Notification

    unread_message_count = Message.objects.filter(
        conversation__participants=request.user,
        read_at__isnull=True,
    ).exclude(sender=request.user).count()
    unread_notification_count = Notification.objects.filter(recipient=request.user, read_at__isnull=True).count()
    return {
        "unread_message_count": unread_message_count,
        "unread_notification_count": unread_notification_count,
    }
