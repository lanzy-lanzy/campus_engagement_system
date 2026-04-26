from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accounts.models import User
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