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

    ADMIN_STATUS_NONE = "none"
    ADMIN_STATUS_REVIEW = "under_review"
    ADMIN_STATUS_PLANNED = "planned"
    ADMIN_STATUS_PROGRESS = "in_progress"
    ADMIN_STATUS_COMPLETED = "completed"

    ADMIN_STATUS_CHOICES = (
        (ADMIN_STATUS_NONE, "No Status"),
        (ADMIN_STATUS_REVIEW, "Under Review"),
        (ADMIN_STATUS_PLANNED, "Planned"),
        (ADMIN_STATUS_PROGRESS, "In Progress"),
        (ADMIN_STATUS_COMPLETED, "Completed"),
    )

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=180)
    description = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to="posts/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_APPROVED)
    admin_status = models.CharField(max_length=20, choices=ADMIN_STATUS_CHOICES, default=ADMIN_STATUS_NONE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("posts:feed")

    @property
    def reaction_count(self):
        return self.reactions.count()

    def get_reaction_counts(self):
        from interactions.models import Reaction
        counts = {}
        for kind, label in Reaction.KIND_CHOICES:
            counts[kind] = self.reactions.filter(kind=kind).count()
        return counts

    def get_user_reaction(self, user):
        if not user or not user.is_authenticated:
            return None
        reaction = self.reactions.filter(user=user).first()
        return reaction.kind if reaction else None

    def user_has_reaction(self, user, kind):
        if not user or not user.is_authenticated:
            return False
        return self.reactions.filter(kind=kind, user=user).exists()

    def user_reacted(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.reactions.filter(user=user).exists()

    @property
    def comment_count(self):
        return self.comments.filter(status="visible", parent__isnull=True).count()

    @property
    def report_count(self):
        return self.reports.filter(status="open").count()

    @property
    def trending_score(self):
        return self.reaction_count + (self.comment_count * 2)