from django.conf import settings
from django.db import models
from django.urls import reverse


class PostTag(models.Model):
    name = models.SlugField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return f"#{self.name}"


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
    shared_from = models.ForeignKey("self", on_delete=models.SET_NULL, related_name="shares", blank=True, null=True)
    tags = models.ManyToManyField(PostTag, related_name="posts", blank=True)
    shared_at = models.DateTimeField(blank=True, null=True)
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
        return self.reactions.filter(comment__isnull=True).count()

    def get_reaction_counts(self):
        from interactions.models import Reaction
        counts = {}
        for kind, label in Reaction.KIND_CHOICES:
            counts[kind] = self.reactions.filter(kind=kind, comment__isnull=True).count()
        return counts

    def get_user_reaction(self, user):
        if not user or not user.is_authenticated:
            return None
        reaction = self.reactions.filter(user=user, comment__isnull=True).first()
        return reaction.kind if reaction else None

    def user_has_reaction(self, user, kind):
        if not user or not user.is_authenticated:
            return False
        return self.reactions.filter(kind=kind, user=user, comment__isnull=True).exists()

    def user_reacted(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.reactions.filter(user=user, comment__isnull=True).exists()

    @property
    def is_shared_post(self):
        return self.shared_from_id is not None

    @property
    def share_source(self):
        return self.shared_from or self

    @property
    def share_count(self):
        return self.shares.filter(status=self.STATUS_APPROVED).count()

    @property
    def comment_count(self):
        return self.comments.filter(status="visible", parent__isnull=True).count()

    @property
    def report_count(self):
        return self.reports.filter(status="open").count()

    @property
    def trending_score(self):
        return self.reaction_count + (self.comment_count * 2)


class PostAttachment(models.Model):
    TYPE_IMAGE = "image"
    TYPE_VIDEO = "video"

    MEDIA_CHOICES = (
        (TYPE_IMAGE, "Image"),
        (TYPE_VIDEO, "Video"),
    )

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="posts/attachments/")
    media_type = models.CharField(max_length=10, choices=MEDIA_CHOICES)
    position = models.PositiveSmallIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("position", "id")

    def __str__(self):
        return f"{self.get_media_type_display()} for {self.post_id}"
