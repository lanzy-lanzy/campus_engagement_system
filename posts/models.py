from django.conf import settings
from django.db import models
from django.urls import reverse


class Post(models.Model):
    CATEGORY_SUGGESTION = "suggestion"
    CATEGORY_COMPLAINT = "complaint"
    CATEGORY_IMPROVEMENT = "improvement"
    CATEGORY_EVENT = "event_idea"

    CATEGORY_CHOICES = (
        (CATEGORY_SUGGESTION, "Suggestion"),
        (CATEGORY_COMPLAINT, "Complaint"),
        (CATEGORY_IMPROVEMENT, "Improvement"),
        (CATEGORY_EVENT, "Event Idea"),
    )

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REMOVED = "removed"

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REMOVED, "Removed"),
    )

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=180)
    description = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to="posts/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_APPROVED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("posts:feed")

    @property
    def like_count(self):
        return self.reactions.filter(kind="like").count()

    @property
    def heart_count(self):
        return self.reactions.filter(kind="heart").count()

    @property
    def comment_count(self):
        return self.comments.filter(status="visible").count()

    @property
    def report_count(self):
        return self.reports.filter(status="open").count()

    @property
    def trending_score(self):
        return (self.like_count * 2) + (self.heart_count * 3) + self.comment_count