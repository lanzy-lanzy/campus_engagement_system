from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone


class Notification(models.Model):
    KIND_MENTION_POST = "mention_post"
    KIND_MENTION_COMMENT = "mention_comment"
    KIND_REACTION_POST = "reaction_post"
    KIND_COMMENT_POST = "comment_post"
    KIND_SHARE_POST = "share_post"
    KIND_FRIEND_REQUEST = "friend_request"
    KIND_FRIEND_ACCEPTED = "friend_accepted"

    KIND_CHOICES = (
        (KIND_MENTION_POST, "Mentioned in post"),
        (KIND_MENTION_COMMENT, "Mentioned in comment"),
        (KIND_REACTION_POST, "Reacted to post"),
        (KIND_COMMENT_POST, "Commented on post"),
        (KIND_SHARE_POST, "Shared post"),
        (KIND_FRIEND_REQUEST, "Friend request"),
        (KIND_FRIEND_ACCEPTED, "Friend accepted"),
    )

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_notifications", blank=True, null=True)
    kind = models.CharField(max_length=30, choices=KIND_CHOICES)
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="notifications", blank=True, null=True)
    comment = models.ForeignKey("interactions.Comment", on_delete=models.CASCADE, related_name="notifications", blank=True, null=True)
    read_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["recipient", "actor", "kind", "post", "comment"],
                name="unique_notification_event",
            )
        ]

    def __str__(self):
        return self.message

    @property
    def is_unread(self):
        return self.read_at is None

    @property
    def message(self):
        actor_name = self.actor.username if self.actor else "Someone"
        messages = {
            self.KIND_MENTION_POST: f"{actor_name} mentioned you in a post",
            self.KIND_MENTION_COMMENT: f"{actor_name} mentioned you in a comment",
            self.KIND_REACTION_POST: f"{actor_name} reacted to your post",
            self.KIND_COMMENT_POST: f"{actor_name} commented on your post",
            self.KIND_SHARE_POST: f"{actor_name} shared your post",
            self.KIND_FRIEND_REQUEST: f"{actor_name} sent you a friend request",
            self.KIND_FRIEND_ACCEPTED: f"{actor_name} accepted your friend request",
        }
        return messages.get(self.kind, "New notification")

    def mark_read(self):
        if not self.read_at:
            self.read_at = timezone.now()
            self.save(update_fields=["read_at"])

    def target_url(self):
        if self.kind in (self.KIND_FRIEND_REQUEST, self.KIND_FRIEND_ACCEPTED):
            if self.actor_id:
                return f"{reverse('accounts:profile')}#user-{self.actor_id}"
        if self.post_id:
            return f"{reverse('posts:feed')}#post-{self.post_id}"
        return reverse("notifications:inbox")


class Mention(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mentions")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_mentions")
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="mentions", blank=True, null=True)
    comment = models.ForeignKey("interactions.Comment", on_delete=models.CASCADE, related_name="mentions", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(post__isnull=False, comment__isnull=True)
                    | Q(post__isnull=True, comment__isnull=False)
                ),
                name="mention_has_exactly_one_target",
            ),
            models.UniqueConstraint(
                fields=["recipient", "post"],
                condition=Q(comment__isnull=True),
                name="unique_post_mention_recipient",
            ),
            models.UniqueConstraint(
                fields=["recipient", "comment"],
                condition=Q(comment__isnull=False),
                name="unique_comment_mention_recipient",
            ),
        ]

    def __str__(self):
        return f"@{self.recipient.username}"
