from django.conf import settings
from django.db import models


class Reaction(models.Model):
    KIND_LIKE = "like"
    KIND_LOVE = "love"
    KIND_WOW = "wow"
    KIND_SAD = "sad"
    KIND_ANGRY = "angry"
    KIND_HAHA = "haha"

    KIND_CHOICES = (
        (KIND_LIKE, "Like"),
        (KIND_LOVE, "Love"),
        (KIND_WOW, "Wow"),
        (KIND_SAD, "Sad"),
        (KIND_ANGRY, "Angry"),
        (KIND_HAHA, "Haha"),
    )

    REACTION_ICONS = {
        KIND_LIKE: "👍",
        KIND_LOVE: "❤️",
        KIND_WOW: "😮",
        KIND_SAD: "😢",
        KIND_ANGRY: "😠",
        KIND_HAHA: "😂",
    }

    REACTION_COLORS = {
        KIND_LIKE: "#1877f2",
        KIND_LOVE: "#e0245e",
        KIND_WOW: "#f7b928",
        KIND_SAD: "#f7b928",
        KIND_ANGRY: "#f57c00",
        KIND_HAHA: "#f7b928",
    }

    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reactions")
    comment = models.ForeignKey("interactions.Comment", on_delete=models.CASCADE, related_name="reactions", blank=True, null=True)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["post", "user", "kind"], name="unique_post_user_reaction_kind"),
            models.UniqueConstraint(fields=["comment", "user", "kind"], name="unique_comment_user_reaction_kind"),
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