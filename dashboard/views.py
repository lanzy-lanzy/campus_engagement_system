from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Permission, Role, User
from interactions.models import Report
from posts.models import Post


@login_required
def index(request):
    if not request.user.is_campus_admin:
        return render(request, "dashboard/index.html")
    posts_count = Post.objects.count()
    users_count = User.objects.count()
    reports_count = Report.objects.filter(status=Report.STATUS_OPEN).count()
    return render(request, "dashboard/index.html", {
        "posts_count": posts_count,
        "users_count": users_count,
        "reports_count": reports_count,
    })


@login_required
def moderation(request):
    if not request.user.is_campus_admin:
        return render(request, "dashboard/moderation.html")
    reports = Report.objects.select_related("post", "reporter").order_by("-created_at")
    return render(request, "dashboard/moderation.html", {"reports": reports})


@login_required
def user_list(request):
    if not request.user.is_campus_admin:
        raise PermissionDenied("You don't have permission to manage users")

    search = request.GET.get("search", "")
    role_filter = request.GET.get("role", "")
    status_filter = request.GET.get("status", "")

    users = User.objects.all().select_related()

    if search:
        users = users.filter(
            Q(username__icontains=search)
            | Q(email__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(student_id__icontains=search)
        )

    if role_filter:
        users = users.filter(role=role_filter)

    if status_filter == "active":
        users = users.filter(is_active=True)
    elif status_filter == "inactive":
        users = users.filter(is_active=False)

    roles = User.ROLE_CHOICES

    return render(request, "dashboard/users.html", {
        "users": users,
        "roles": roles,
        "search": search,
        "role_filter": role_filter,
        "status_filter": status_filter,
    })


@login_required
def user_create(request):
    if not request.user.is_campus_admin:
        raise PermissionDenied("You don't have permission to manage users")

    if request.method != "POST":
        return render(request, "dashboard/user_edit.html", {
            "user_obj": None,
            "roles": User.ROLE_CHOICES,
        })

    email = request.POST.get("email")
    username = request.POST.get("username")
    password = request.POST.get("password", "ChangeMe123!")
    first_name = request.POST.get("first_name", "")
    last_name = request.POST.get("last_name", "")
    role = request.POST.get("role", User.ROLE_STUDENT)
    department = request.POST.get("department", "")
    student_id = request.POST.get("student_id", "")

    if User.objects.filter(email=email).exists():
        messages.error(request, "Email already exists")
        return redirect("dashboard:users")

    user = User.objects.create_user(
        email=email,
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        role=role,
        department=department,
        student_id=student_id,
    )
    messages.success(request, f"User {user.username} created successfully")
    return redirect("dashboard:user_edit", user_id=user.pk)


@login_required
def user_edit(request, user_id):
    if not request.user.is_campus_admin:
        raise PermissionDenied("You don't have permission to manage users")

    user_obj = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        user_obj.first_name = request.POST.get("first_name", "")
        user_obj.last_name = request.POST.get("last_name", "")
        user_obj.department = request.POST.get("department", "")
        user_obj.student_id = request.POST.get("student_id", "")
        user_obj.bio = request.POST.get("bio", "")

        new_role = request.POST.get("role")
        if new_role and new_role != user_obj.role:
            user_obj.role = new_role

        user_obj.save()
        messages.success(request, f"User {user_obj.username} updated successfully")
        return redirect("dashboard:users")

    return render(request, "dashboard/user_edit.html", {
        "user_obj": user_obj,
        "roles": User.ROLE_CHOICES,
    })


@login_required
def user_delete(request, user_id):
    if not request.user.is_campus_admin:
        raise PermissionDenied("You don't have permission to manage users")

    user_obj = get_object_or_404(User, pk=user_id)

    if request.user == user_obj:
        messages.error(request, "You cannot delete your own account")
        return redirect("dashboard:users")

    username = user_obj.username
    user_obj.delete()
    messages.success(request, f"User {username} deleted successfully")
    return redirect("dashboard:users")


@login_required
def user_toggle_active(request, user_id):
    if not request.user.is_campus_admin:
        raise PermissionDenied("You don't have permission to manage users")

    user_obj = get_object_or_404(User, pk=user_id)

    if request.user == user_obj:
        messages.error(request, "You cannot toggle your own account")
        return redirect("dashboard:users")

    user_obj.is_active = not user_obj.is_active
    user_obj.save()

    status = "activated" if user_obj.is_active else "deactivated"
    messages.success(request, f"User {user_obj.username} {status}")
    return redirect("dashboard:users")


@login_required
def post_list(request):
    if not request.user.is_campus_admin:
        raise PermissionDenied("You don't have permission to moderate content")

    search = request.GET.get("search", "")
    category_filter = request.GET.get("category", "")
    status_filter = request.GET.get("status", "")
    admin_status_filter = request.GET.get("admin_status", "")

    posts = Post.objects.all().select_related("author")

    if search:
        posts = posts.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
        )

    if category_filter:
        posts = posts.filter(category=category_filter)

    if status_filter:
        posts = posts.filter(status=status_filter)

    if admin_status_filter:
        posts = posts.filter(admin_status=admin_status_filter)

    categories = Post.CATEGORY_CHOICES
    statuses = Post.STATUS_CHOICES
    admin_statuses = Post.ADMIN_STATUS_CHOICES

    return render(request, "dashboard/posts.html", {
        "posts": posts,
        "categories": categories,
        "statuses": statuses,
        "admin_statuses": admin_statuses,
        "search": search,
        "category_filter": category_filter,
        "status_filter": status_filter,
        "admin_status_filter": admin_status_filter,
    })


@login_required
def post_edit(request, post_id):
    if not request.user.is_campus_admin:
        raise PermissionDenied("You don't have permission to moderate content")

    post = get_object_or_404(Post, pk=post_id)

    if request.method == "POST":
        post.title = request.POST.get("title", post.title)
        post.description = request.POST.get("description", post.description)
        post.category = request.POST.get("category", post.category)
        post.status = request.POST.get("status", post.status)
        post.admin_status = request.POST.get("admin_status", post.admin_status)
        post.save()
        messages.success(request, f"Post '{post.title}' updated successfully")
        return redirect("dashboard:posts")

    return render(request, "dashboard/post_edit.html", {
        "post": post,
        "categories": Post.CATEGORY_CHOICES,
        "statuses": Post.STATUS_CHOICES,
        "admin_statuses": Post.ADMIN_STATUS_CHOICES,
    })


@login_required
def post_delete(request, post_id):
    if not request.user.is_campus_admin:
        raise PermissionDenied("You don't have permission to moderate content")

    post = get_object_or_404(Post, pk=post_id)
    title = post.title
    post.delete()
    messages.success(request, f"Post '{title}' deleted successfully")
    return redirect("dashboard:posts")


@login_required
def post_status(request, post_id):
    if not request.user.is_campus_admin:
        raise PermissionDenied("You don't have permission to moderate content")

    post = get_object_or_404(Post, pk=post_id)
    new_status = request.POST.get("status")

    if new_status in [s for s, l in Post.STATUS_CHOICES]:
        post.status = new_status
        post.save()
        messages.success(request, f"Post status updated to {post.get_status_display()}")
    else:
        messages.error(request, "Invalid status")

    return redirect("dashboard:post_edit", post_id=post.pk)


@login_required
def analytics(request):
    if not request.user.is_campus_admin:
        raise PermissionDenied("You don't have permission to view analytics")

    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta

    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)

    total_users = User.objects.count()
    total_posts = Post.objects.count()
    total_reports = Report.objects.count()

    new_users_30d = User.objects.filter(date_joined__gte=thirty_days_ago).count()
    new_posts_30d = Post.objects.filter(created_at__gte=thirty_days_ago).count()

    posts_by_category = list(
        Post.objects.values("category")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    posts_by_admin_status = list(
        Post.objects.values("admin_status")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    open_reports = Report.objects.filter(status=Report.STATUS_OPEN).count()
    resolved_reports = Report.objects.filter(status=Report.STATUS_RESOLVED).count()

    return render(request, "dashboard/analytics.html", {
        "total_users": total_users,
        "total_posts": total_posts,
        "total_reports": total_reports,
        "new_users_30d": new_users_30d,
        "new_posts_30d": new_posts_30d,
        "posts_by_category": posts_by_category,
        "posts_by_admin_status": posts_by_admin_status,
        "open_reports": open_reports,
        "resolved_reports": resolved_reports,
    })


@login_required
def settings(request):
    if not request.user.is_campus_admin:
        raise PermissionDenied("You don't have permission to manage settings")

    permissions = Permission.objects.all()
    roles = Role.objects.all().prefetch_related("permissions")

    return render(request, "dashboard/settings.html", {
        "permissions": permissions,
        "roles": roles,
    })