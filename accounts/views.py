from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProfileForm, StudentRegistrationForm


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:post_login_redirect")
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("posts:feed")
    else:
        form = StudentRegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def post_login_redirect(request):
    if request.user.is_campus_admin:
        return redirect("dashboard:index")
    return redirect("posts:feed")


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)
    posts_manager = getattr(request.user, "posts", None)
    posts = posts_manager.order_by("-created_at") if posts_manager is not None else []
    return render(request, "accounts/profile.html", {"form": form, "posts": posts})
