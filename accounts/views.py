from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.models import Q

from accounts.models import Friendship
from accounts.forms import ProfileForm, StudentRegistrationForm
from notifications.services import notify_friend_request, notify_friend_accepted


def _display_name(user):
    return getattr(user, "username", "") or user.get_username()


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
    posts = request.user.posts.order_by("-created_at")
    return render(request, "accounts/profile.html", {"form": form, "posts": posts})


@login_required
def request_friend(request, user_pk):
    if request.method != "POST":
        raise Http404
    other_user = get_object_or_404(get_user_model(), pk=user_pk, is_active=True)
    if other_user == request.user:
        raise Http404
    friendship = Friendship.request(request.user, other_user)
    if friendship.status == Friendship.STATUS_PENDING and friendship.requester_id == request.user.pk:
        notify_friend_request(request.user, other_user)
    elif friendship.status == Friendship.STATUS_ACCEPTED and friendship.addressee_id == request.user.pk:
        notify_friend_accepted(other_user, request.user)
    return redirect(request.POST.get("next") or "chat:inbox")


@login_required
def search_friends(request):
    query = request.GET.get("q", "").strip()
    friends = set()
    for fs in Friendship.objects.filter(Q(requester=request.user, status=Friendship.STATUS_ACCEPTED) | Q(addressee=request.user, status=Friendship.STATUS_ACCEPTED)):
        friend = fs.addressee if fs.requester_id == request.user.pk else fs.requester
        display_name = _display_name(friend)
        department = friend.department or ""
        haystack = f"{friend.username} {display_name} {department}".lower()
        if not query or query.lower() in haystack:
            friends.add(friend)
    friends = sorted(friends, key=lambda u: u.username)[:10]
    return JsonResponse(
        [
            {
                "id": u.pk,
                "username": u.username,
                "display_name": _display_name(u),
                "department": u.department,
                "avatar_url": u.avatar.url if u.avatar else "",
            }
            for u in friends
        ],
        safe=False,
    )
