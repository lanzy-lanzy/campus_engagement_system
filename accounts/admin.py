from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Campus Profile", {"fields": ("role", "student_id", "department", "avatar", "bio")}),
    )
    list_display = ("username", "email", "role", "student_id", "department", "is_staff")
    list_filter = UserAdmin.list_filter + ("role", "department")