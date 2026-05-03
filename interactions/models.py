from django.conf import settings
from django.db import models
from django.db.models import Q


class Reaction(models.Model):
    KIND_LIKE = "like"
    KIND_LOVE = "love"
    KIND_CARE = "care"
    KIND_WOW = "wow"
    KIND_SAD = "sad"
    KIND_ANGRY = "angry"
    KIND_HAHA = "haha"

    KIND_CHOICES = (
        (KIND_LIKE, "Like"),
        (KIND_LOVE, "Love"),
        (KIND_CARE, "Care"),
        (KIND_WOW, "Wow"),
        (KIND_SAD, "Sad"),
        (KIND_ANGRY, "Angry"),
        (KIND_HAHA, "Haha"),
    )

    REACTION_ICONS = {
        KIND_LIKE: '<img src="/static/emoji/like.png" class="w-6 h-6" alt="like">',
        KIND_LOVE: '<img src="/static/emoji/love.png" class="w-6 h-6" alt="love">',
        KIND_CARE: '<img src="/static/emoji/care.png" class="w-6 h-6" alt="care">',
        KIND_WOW: '<img src="/static/emoji/wow.png" class="w-6 h-6" alt="wow">',
        KIND_SAD: '<img src="/static/emoji/sad.png" class="w-6 h-6" alt="sad">',
        KIND_ANGRY: '<img src="/static/emoji/angry.png" class="w-6 h-6" alt="angry">',
        KIND_HAHA: '<img src="/static/emoji/haha.png" class="w-6 h-6" alt="haha">',
    }

    REACTION_COLORS = {
        KIND_LIKE: "#1877f2",
        KIND_LOVE: "#e0245e",
        KIND_CARE: "#f7b928",
        KIND_WOW: "#f7b928",
        KIND_SAD: "#f7b928",
        KIND_ANGRY: "#f57c00",
        KIND_HAHA: "#f7b928",
    }

    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="reactions", blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reactions")
    comment = models.ForeignKey("interactions.Comment", on_delete=models.CASCADE, related_name="reactions", blank=True, null=True)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(post__isnull=False, comment__isnull=True)
                    | Q(post__isnull=True, comment__isnull=False)
                ),
                name="reaction_has_exactly_one_target",
            ),
            models.UniqueConstraint(
                fields=["post", "user"],
                condition=Q(comment__isnull=True),
                name="unique_post_user_reaction",
            ),
            models.UniqueConstraint(
                fields=["comment", "user"],
                condition=Q(comment__isnull=False),
                name="unique_comment_user_reaction",
            ),
        ]


class Comment(models.Model):
    STATUS_VISIBLE = "visible"
    STATUS_HIDDEN = "hidden"

    STATUS_CHOICES = (
        (STATUS_VISIBLE, "Visible"),
        (STATUS_HIDDEN, "Hidden"),
    )

    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="replies", blank=True, null=True)
    body = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_VISIBLE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"


class Report(models.Model):
    REASON_INAPPROPRIATE = "inappropriate"
    REASON_SPAM = "spam"
    REASON_HARASSMENT = "harassment"
    REASON_OTHER = "other"

    REASON_CHOICES = (
        (REASON_INAPPROPRIATE, "Inappropriate content"),
        (REASON_SPAM, "Spam"),
        (REASON_HARASSMENT, "Harassment"),
        (REASON_OTHER, "Other"),
    )

    STATUS_OPEN = "open"
    STATUS_RESOLVED = "resolved"
    STATUS_DISMISSED = "dismissed"

    STATUS_CHOICES = (
        (STATUS_OPEN, "Open"),
        (STATUS_RESOLVED, "Resolved"),
        (STATUS_DISMISSED, "Dismissed"),
    )

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports")
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="reports")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="reports", blank=True, null=True)
    reason = models.CharField(max_length=30, choices=REASON_CHOICES)
    details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name="reviewed_reports")
    reviewed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_reason_display()} report for {self.post}"
