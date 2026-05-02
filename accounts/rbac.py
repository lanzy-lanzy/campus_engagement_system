from functools import wraps

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Permission, Role, UserRole


def has_permission(user, permission_code):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.has_permission(permission_code)


def check_permission(user, permission_code):
    if not has_permission(user, permission_code):
        raise PermissionDenied


def permission_required(permission_code):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            check_permission(request.user, permission_code)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def assign_role(user, role_name):
    role = Role.objects.filter(name=role_name).first()
    if not role:
        return None
    user_role, created = UserRole.objects.get_or_create(user=user, role=role)
    return user_role


def remove_role(user, role_name):
    role = Role.objects.filter(name=role_name).first()
    if not role:
        return False
    deleted, _ = UserRole.objects.filter(user=user, role=role).delete()
    return deleted > 0


def create_default_roles():
    student_role, _ = Role.objects.get_or_create(
        name=Role.ROLE_STUDENT,
        defaults={"is_default": True}
    )
    moderator_role, _ = Role.objects.get_or_create(name=Role.ROLE_MODERATOR)
    admin_role, _ = Role.objects.get_or_create(name=Role.ROLE_ADMIN)

    perms_mapping = {
        Role.ROLE_STUDENT: [Permission.CODE_CREATE_POST, Permission.CODE_SEND_MESSAGE, Permission.CODE_MANAGE_FRIENDS],
        Role.ROLE_MODERATOR: [Permission.CODE_MODERATE_CONTENT, Permission.CODE_VIEW_DASHBOARD],
        Role.ROLE_ADMIN: [
            Permission.CODE_CREATE_POST, Permission.CODE_EDIT_POST, Permission.CODE_DELETE_POST,
            Permission.CODE_MODERATE_CONTENT, Permission.CODE_MANAGE_USERS, Permission.CODE_VIEW_DASHBOARD,
            Permission.CODE_SEND_MESSAGE, Permission.CODE_MANAGE_FRIENDS
        ],
    }

    for role_name, perm_codes in perms_mapping.items():
        role = Role.objects.filter(name=role_name).first()
        if role:
            perms = Permission.objects.filter(code__in=perm_codes)
            role.permissions.set(perms)

    return {
        Role.ROLE_STUDENT: student_role,
        Role.ROLE_MODERATOR: moderator_role,
        Role.ROLE_ADMIN: admin_role,
    }