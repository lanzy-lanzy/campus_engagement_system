from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CampusUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", User.ROLE_ADMIN)
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    ROLE_STUDENT = "student"
    ROLE_ADMIN = "admin"

    ROLE_CHOICES = (
        (ROLE_STUDENT, "Student"),
        (ROLE_ADMIN, "Admin"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    student_id = models.CharField(max_length=40, blank=True)
    department = models.CharField(max_length=120, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True)

    objects = CampusUserManager()

    @property
    def is_student(self):
        return self.role == self.ROLE_STUDENT

    @property
    def is_campus_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_staff or self.is_superuser
