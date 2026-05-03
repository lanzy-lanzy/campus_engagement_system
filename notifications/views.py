from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from .models import Notification


@login_required
def inbox(request):
    notification_qs = Notification.objects.filter(recipient=request.user).select_related("actor", "post", "comment")
    notifications = list(notification_qs)
    unread_count = sum(1 for notification in notifications if notification.is_unread)
    actor_count = len({notification.actor_id for notification in notifications if notification.actor_id})
    post_notification_count = sum(1 for notification in notifications if notification.post_id)

    notification_qs.filter(read_at__isnull=True).update(read_at=timezone.now())
    return render(
        request,
        "notifications/inbox.html",
        {
            "notifications": notifications,
            "notification_stats": {
                "total": len(notifications),
                "unread": unread_count,
                "actors": actor_count,
                "posts": post_notification_count,
            },
        },
    )
