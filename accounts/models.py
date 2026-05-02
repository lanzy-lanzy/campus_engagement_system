from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.db import models
from django.db.models import Q


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        extra_fields.setdefault("role", User.ROLE_STUDENT)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.ROLE_ADMIN)
        return self.create_user(email, password, **extra_fields)


class Permission(models.Model):
    CODE_CREATE_POST = "create_post"
    CODE_EDIT_POST = "edit_post"
    CODE_DELETE_POST = "delete_post"
    CODE_MODERATE_CONTENT = "moderate_content"
    CODE_MANAGE_USERS = "manage_users"
    CODE_VIEW_DASHBOARD = "view_dashboard"
    CODE_SEND_MESSAGE = "send_message"
    CODE_MANAGE_FRIENDS = "manage_friends"

    CODE_CHOICES = [
        (CODE_CREATE_POST, "Create Post"),
        (CODE_EDIT_POST, "Edit Post"),
        (CODE_DELETE_POST, "Delete Post"),
        (CODE_MODERATE_CONTENT, "Moderate Content"),
        (CODE_MANAGE_USERS, "Manage Users"),
        (CODE_VIEW_DASHBOARD, "View Dashboard"),
        (CODE_SEND_MESSAGE, "Send Message"),
        (CODE_MANAGE_FRIENDS, "Manage Friends"),
    ]

    code = models.CharField(max_length=50, unique=True, choices=CODE_CHOICES)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("code",)

    def __str__(self):
        return self.code


class Role(models.Model):
    ROLE_STUDENT = "student"
    ROLE_MODERATOR = "moderator"
    ROLE_ADMIN = "admin"

    ROLE_CHOICES = [
        (ROLE_STUDENT, "Student"),
        (ROLE_MODERATOR, "Moderator"),
        (ROLE_ADMIN, "Admin"),
    ]

    name = models.CharField(max_length=50, unique=True, choices=ROLE_CHOICES)
    permissions = models.ManyToManyField(Permission, related_name="roles")
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def has_permission(self, permission_code):
        return self.permissions.filter(code=permission_code).exists()


class UserRole(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_roles")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="user_roles")
    assigned_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ("user", "role")

    def __str__(self):
        return f"{self.user} - {self.role}"


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_STUDENT = "student"
    ROLE_ADMIN = "admin"

    ROLE_CHOICES = (
        (ROLE_STUDENT, "Student"),
        (ROLE_ADMIN, "Admin"),
    )

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    student_id = models.CharField(max_length=40, blank=True)
    department = models.CharField(max_length=120, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    @property
    def is_student(self):
        return self.role == self.ROLE_STUDENT

    @property
    def is_campus_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_staff or self.is_superuser

    def get_all_permissions(self):
        if self.is_superuser:
            return set(Permission.objects.values_list("code", flat=True))
        perms = set()
        for ur in self.user_roles.select_related("role").all():
            for perm in ur.role.permissions.values_list("code", flat=True):
                perms.add(perm)
        return perms

    def has_permission(self, permission_code):
        if self.is_superuser:
            return True
        return permission_code in self.get_all_permissions()


class Friendship(models.Model):
    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_ACCEPTED, "Accepted"),
    )

    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_friendships")
    addressee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_friendships")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=~Q(requester=models.F("addressee")), name="friendship_no_self_request"),
            models.UniqueConstraint(fields=["requester", "addressee"], name="unique_friendship_direction"),
        ]

    def __str__(self):
        return f"{self.requester} -> {self.addressee} ({self.status})"

    @classmethod
    def between(cls, user, other_user):
        return cls.objects.filter(
            Q(requester=user, addressee=other_user) | Q(requester=other_user, addressee=user)
        ).first()

    @classmethod
    def are_friends(cls, user, other_user):
        if not user or not other_user or user.pk == other_user.pk:
            return False
        return cls.objects.filter(
            Q(requester=user, addressee=other_user) | Q(requester=other_user, addressee=user),
            status=cls.STATUS_ACCEPTED,
        ).exists()

    @classmethod
    def status_for(cls, user, other_user):
        friendship = cls.between(user, other_user)
        if not friendship:
            return "none"
        if friendship.status == cls.STATUS_ACCEPTED:
            return "friends"
        if friendship.requester_id == user.pk:
            return "pending_sent"
        return "pending_received"

    @classmethod
    def request(cls, requester, addressee):
        friendship = cls.between(requester, addressee)
        if friendship:
            if friendship.status == cls.STATUS_PENDING and friendship.addressee_id == requester.pk:
                friendship.status = cls.STATUS_ACCEPTED
                friendship.save(update_fields=["status", "updated_at"])
            return friendship
        return cls.objects.create(requester=requester, addressee=addressee)
