# Phase 1 Campus Engagement MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the working Phase 1 MVP for the campus student feedback and engagement system.

**Architecture:** Replace the empty starter `core` app with four focused Django apps: `accounts`, `posts`, `interactions`, and `dashboard`. Use Django Templates, Tailwind CDN, HTMX partials, and Alpine.js for the responsive sidebar and modal state.

**Tech Stack:** Django 4.2 project currently present, Django ORM, SQLite development database, Django templates, Tailwind CSS CDN, HTMX, Alpine.js.

---

## Scope

This plan implements Phase 1 only:

- Student registration, login, logout, profile, and role redirects.
- Custom `User` model with student/admin roles.
- Post creation, edit, delete, image upload, categories, status, and feed sorting.
- Like and heart reactions through HTMX.
- Threaded comments through HTMX.
- Reports for posts and comments.
- Admin dashboard and moderation views.
- Mobile-first shell with sidebar, feed cards, modal forms, and partial templates.
- Django test coverage for core models, permissions, and HTMX endpoints.

Phase 2 features such as richer search, tag expansion, notification polling, and PostgreSQL environment configuration are not part of this plan. Phase 3 visual refinements beyond the MVP-quality UI shell are not part of this plan.

## Current Repository Notes

- The workspace is not a git repository. Commit steps are written as checkpoints. If git is initialized before execution, run the listed `git add` and `git commit` commands. If git is not initialized, record the checkpoint in the task log and continue.
- The current project has `core/urls.py` importing `home` from an empty `core/views.py`. Task 1 removes that routing dependency by making `posts` own the home feed.
- The existing SQLite database was created before the custom user model. Task 2 removes `db.sqlite3` and creates fresh migrations because changing `AUTH_USER_MODEL` after auth tables exist is not safe.

## File Structure

Create:

- `accounts/__init__.py`: package marker.
- `accounts/admin.py`: custom user admin registration.
- `accounts/apps.py`: app config.
- `accounts/forms.py`: registration and profile forms.
- `accounts/models.py`: custom user model.
- `accounts/tests.py`: account model and auth flow tests.
- `accounts/urls.py`: auth/profile routes.
- `accounts/views.py`: register, login redirect, profile.
- `accounts/migrations/__init__.py`: migration package marker.
- `posts/__init__.py`: package marker.
- `posts/admin.py`: post admin.
- `posts/apps.py`: app config.
- `posts/forms.py`: post form.
- `posts/models.py`: post model.
- `posts/tests.py`: post tests.
- `posts/urls.py`: feed and post routes.
- `posts/views.py`: feed, create, update, delete.
- `posts/migrations/__init__.py`: migration package marker.
- `interactions/__init__.py`: package marker.
- `interactions/admin.py`: comment, reaction, report admin.
- `interactions/apps.py`: app config.
- `interactions/forms.py`: comment and report forms.
- `interactions/models.py`: comment, reaction, report models.
- `interactions/tests.py`: interaction tests.
- `interactions/urls.py`: HTMX interaction routes.
- `interactions/views.py`: HTMX views.
- `interactions/migrations/__init__.py`: migration package marker.
- `dashboard/__init__.py`: package marker.
- `dashboard/apps.py`: app config.
- `dashboard/tests.py`: dashboard tests.
- `dashboard/urls.py`: admin dashboard routes.
- `dashboard/views.py`: metrics and moderation views.
- `templates/base.html`: app shell.
- `templates/accounts/login.html`: login page.
- `templates/accounts/register.html`: registration page.
- `templates/accounts/profile.html`: student profile.
- `templates/posts/feed.html`: student feed page.
- `templates/posts/post_form.html`: create/edit form page.
- `templates/posts/partials/post_card.html`: reusable feed card.
- `templates/posts/partials/post_list.html`: reusable feed list.
- `templates/interactions/partials/reaction_bar.html`: HTMX reaction counters.
- `templates/interactions/partials/comment_list.html`: HTMX comment thread.
- `templates/interactions/partials/comment_form.html`: HTMX comment form.
- `templates/interactions/partials/report_form.html`: report form partial.
- `templates/interactions/partials/inline_error.html`: compact HTMX error.
- `templates/dashboard/index.html`: admin dashboard.
- `templates/dashboard/moderation.html`: moderation queue.
- `templates/partials/messages.html`: Django messages.
- `templates/partials/sidebar.html`: responsive navigation.
- `templates/partials/pagination.html`: pagination controls.
- `static/css/app.css`: tiny custom CSS.
- `static/js/app.js`: tiny custom JS.

Modify:

- `campus_engagement_system/settings.py`: install apps, set custom user, configure templates/static/media/auth redirects.
- `campus_engagement_system/urls.py`: include app URLs and serve media in development.
- `ReadME.md`: replace generated spec prompt with setup and flow guide after Phase 1 works.

Remove or leave unused:

- `core/`: leave unused during Phase 1 or delete after all imports are gone. The safer first pass is to leave the folder but remove it from `INSTALLED_APPS`.

## Task 1: Project Settings and URL Skeleton

**Files:**
- Modify: `campus_engagement_system/settings.py`
- Modify: `campus_engagement_system/urls.py`
- Create: app package/config files for `accounts`, `posts`, `interactions`, `dashboard`

- [ ] **Step 1: Create the app directories**

Run:

```powershell
python manage.py startapp accounts
python manage.py startapp posts
python manage.py startapp interactions
python manage.py startapp dashboard
```

Expected: four new Django app directories exist.

- [ ] **Step 2: Update settings**

In `campus_engagement_system/settings.py`, make these changes:

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-9f@)cc4pi-3+d71rzksdcx877ldn#l*0!bqmur^v#kxa=yigp3"
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "posts",
    "interactions",
    "dashboard",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "campus_engagement_system.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "campus_engagement_system.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Manila"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "posts:feed"
LOGOUT_REDIRECT_URL = "accounts:login"
```

- [ ] **Step 3: Update project URLs**

In `campus_engagement_system/urls.py`, use:

```python
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("interactions/", include("interactions.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("", include("posts.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

- [ ] **Step 4: Add temporary URL files so `check` can import**

Create `accounts/urls.py`:

```python
from django.urls import path

app_name = "accounts"

urlpatterns = []
```

Create `posts/urls.py`:

```python
from django.urls import path

app_name = "posts"

urlpatterns = []
```

Create `interactions/urls.py`:

```python
from django.urls import path

app_name = "interactions"

urlpatterns = []
```

Create `dashboard/urls.py`:

```python
from django.urls import path

app_name = "dashboard"

urlpatterns = []
```

- [ ] **Step 5: Run Django system check**

Run:

```powershell
python manage.py check
```

Expected: `System check identified no issues`.

- [ ] **Step 6: Checkpoint**

If git is initialized:

```powershell
git add campus_engagement_system accounts posts interactions dashboard
git commit -m "chore: configure modular django apps"
```

Expected: commit succeeds.

## Task 2: Accounts Model, Forms, Views, and Tests

**Files:**
- Create: `accounts/models.py`
- Create: `accounts/forms.py`
- Create: `accounts/views.py`
- Modify: `accounts/admin.py`
- Modify: `accounts/urls.py`
- Create: `accounts/tests.py`
- Create: `templates/accounts/login.html`
- Create: `templates/accounts/register.html`
- Create: `templates/accounts/profile.html`

- [ ] **Step 1: Write failing account tests**

Create `accounts/tests.py`:

```python
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class UserModelTests(TestCase):
    def test_student_user_defaults_to_student_role(self):
        user = get_user_model().objects.create_user(
            username="ana",
            email="ana@example.com",
            password="StrongPass123",
        )

        self.assertEqual(user.role, "student")
        self.assertTrue(user.is_student)
        self.assertFalse(user.is_campus_admin)

    def test_superuser_is_admin_role(self):
        user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="StrongPass123",
        )

        self.assertEqual(user.role, "admin")
        self.assertTrue(user.is_campus_admin)


class AuthFlowTests(TestCase):
    def test_register_creates_student_and_redirects_to_feed(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "mika",
                "email": "mika@example.com",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
                "student_id": "2026-001",
                "department": "Engineering",
            },
        )

        self.assertRedirects(response, reverse("posts:feed"))
        user = get_user_model().objects.get(username="mika")
        self.assertEqual(user.role, "student")

    def test_admin_login_redirects_to_dashboard(self):
        user = get_user_model().objects.create_user(
            username="admin1",
            email="admin1@example.com",
            password="StrongPass123",
            role="admin",
            is_staff=True,
        )

        self.client.login(username=user.username, password="StrongPass123")
        response = self.client.get(reverse("accounts:post_login_redirect"))

        self.assertRedirects(response, reverse("dashboard:index"))
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
python manage.py test accounts
```

Expected: failures because `accounts.User`, auth routes, and `posts:feed` do not exist yet.

- [ ] **Step 3: Implement custom user model**

In `accounts/models.py`:

```python
from django.contrib.auth.models import AbstractUser
from django.db import models


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

    @property
    def is_student(self):
        return self.role == self.ROLE_STUDENT

    @property
    def is_campus_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_staff or self.is_superuser
```

- [ ] **Step 4: Add forms**

In `accounts/forms.py`:

```python
from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class StudentRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "student_id", "department", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.ROLE_STUDENT
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email", "student_id", "department", "avatar", "bio")
```

- [ ] **Step 5: Add account views**

In `accounts/views.py`:

```python
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

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
    posts = request.user.posts.order_by("-created_at")
    return render(request, "accounts/profile.html", {"form": form, "posts": posts})
```

- [ ] **Step 6: Wire account URLs**

In `accounts/urls.py`:

```python
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", views.register, name="register"),
    path("redirect/", views.post_login_redirect, name="post_login_redirect"),
    path("profile/", views.profile, name="profile"),
]
```

- [ ] **Step 7: Register user admin**

In `accounts/admin.py`:

```python
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
```

- [ ] **Step 8: Add minimal account templates**

Create `templates/accounts/login.html`:

```django
{% extends "base.html" %}
{% block title %}Login{% endblock %}
{% block content %}
<section class="mx-auto max-w-md">
  <h1 class="text-2xl font-semibold text-[#2C3E94]">Welcome back</h1>
  <form method="post" class="mt-6 space-y-4 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
    {% csrf_token %}
    {{ form.as_p }}
    <button class="w-full rounded-md bg-[#2C3E94] px-4 py-2 font-medium text-white">Login</button>
  </form>
  <p class="mt-4 text-sm text-slate-600">Need an account? <a class="text-[#2C3E94]" href="{% url 'accounts:register' %}">Register</a></p>
</section>
{% endblock %}
```

Create `templates/accounts/register.html`:

```django
{% extends "base.html" %}
{% block title %}Register{% endblock %}
{% block content %}
<section class="mx-auto max-w-xl">
  <h1 class="text-2xl font-semibold text-[#2C3E94]">Create student account</h1>
  <form method="post" class="mt-6 space-y-4 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
    {% csrf_token %}
    {{ form.as_p }}
    <button class="w-full rounded-md bg-[#2C3E94] px-4 py-2 font-medium text-white">Register</button>
  </form>
</section>
{% endblock %}
```

Create `templates/accounts/profile.html`:

```django
{% extends "base.html" %}
{% block title %}Profile{% endblock %}
{% block content %}
<section class="grid gap-6 lg:grid-cols-[320px_1fr]">
  <form method="post" enctype="multipart/form-data" class="space-y-4 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
    {% csrf_token %}
    <h1 class="text-xl font-semibold text-[#2C3E94]">Profile</h1>
    {{ form.as_p }}
    <button class="rounded-md bg-[#2C3E94] px-4 py-2 font-medium text-white">Save profile</button>
  </form>
  <div class="space-y-4">
    <h2 class="text-xl font-semibold text-slate-900">Your posts</h2>
    {% for post in posts %}
      {% include "posts/partials/post_card.html" %}
    {% empty %}
      <div class="rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center text-slate-500">No posts yet.</div>
    {% endfor %}
  </div>
</section>
{% endblock %}
```

- [ ] **Step 9: Run account tests**

Run:

```powershell
python manage.py test accounts
```

Expected: tests still fail until `posts:feed`, dashboard route, base template, and post relation exist.

- [ ] **Step 10: Checkpoint**

If git is initialized:

```powershell
git add accounts templates/accounts
git commit -m "feat: add student accounts"
```

Expected: commit succeeds.

## Task 3: Post Model, Form, Admin, and Feed Tests

**Files:**
- Create: `posts/models.py`
- Create: `posts/forms.py`
- Modify: `posts/admin.py`
- Create: `posts/tests.py`
- Modify: `posts/urls.py`
- Create: `posts/views.py`

- [ ] **Step 1: Write failing post tests**

Create `posts/tests.py`:

```python
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Post


class PostModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="student",
            password="StrongPass123",
        )

    def test_trending_score_counts_reactions_and_comments(self):
        post = Post.objects.create(
            author=self.user,
            title="Add study pods",
            description="Quiet spaces would help.",
            category=Post.CATEGORY_IMPROVEMENT,
        )

        self.assertEqual(post.trending_score, 0)


class PostViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="student",
            password="StrongPass123",
        )

    def test_student_can_create_post(self):
        self.client.login(username="student", password="StrongPass123")
        response = self.client.post(
            reverse("posts:create"),
            {
                "title": "More shaded benches",
                "description": "The courtyard needs shade.",
                "category": Post.CATEGORY_SUGGESTION,
            },
        )

        self.assertRedirects(response, reverse("posts:feed"))
        self.assertEqual(Post.objects.count(), 1)

    def test_student_cannot_edit_other_student_post(self):
        other = get_user_model().objects.create_user(username="other", password="StrongPass123")
        post = Post.objects.create(
            author=other,
            title="Library hours",
            description="Open earlier.",
            category=Post.CATEGORY_SUGGESTION,
        )
        self.client.login(username="student", password="StrongPass123")

        response = self.client.get(reverse("posts:edit", args=[post.pk]))

        self.assertEqual(response.status_code, 403)
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
python manage.py test posts
```

Expected: failures because `Post` and routes do not exist yet.

- [ ] **Step 3: Implement post model**

In `posts/models.py`:

```python
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

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=180)
    description = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to="posts/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_APPROVED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("posts:feed")

    @property
    def like_count(self):
        return self.reactions.filter(kind="like").count()

    @property
    def heart_count(self):
        return self.reactions.filter(kind="heart").count()

    @property
    def comment_count(self):
        return self.comments.filter(status="visible").count()

    @property
    def report_count(self):
        return self.reports.filter(status="open").count()

    @property
    def trending_score(self):
        return (self.like_count * 2) + (self.heart_count * 3) + self.comment_count
```

- [ ] **Step 4: Add post form**

In `posts/forms.py`:

```python
from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "description", "category", "image")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }
```

- [ ] **Step 5: Add post admin**

In `posts/admin.py`:

```python
from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "status", "created_at")
    list_filter = ("category", "status", "created_at")
    search_fields = ("title", "description", "author__username")
```

- [ ] **Step 6: Add post views**

In `posts/views.py`:

```python
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Post


@login_required
def feed(request):
    sort = request.GET.get("sort", "latest")
    posts = Post.objects.filter(status=Post.STATUS_APPROVED).select_related("author")

    if sort == "most_liked":
        posts = posts.annotate(likes=Count("reactions", filter=Q(reactions__kind="like"))).order_by("-likes", "-created_at")
    elif sort == "trending":
        posts = posts.annotate(
            likes=Count("reactions", filter=Q(reactions__kind="like")),
            hearts=Count("reactions", filter=Q(reactions__kind="heart")),
            comment_total=Count("comments"),
        ).order_by("-hearts", "-likes", "-comment_total", "-created_at")
    else:
        posts = posts.order_by("-created_at")

    context = {"posts": posts, "sort": sort, "form": PostForm()}
    template = "posts/partials/post_list.html" if request.headers.get("HX-Request") else "posts/feed.html"
    return render(request, template, context)


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("posts:feed")
    else:
        form = PostForm()
    return render(request, "posts/post_form.html", {"form": form, "mode": "Create"})


@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user and not request.user.is_campus_admin:
        raise PermissionDenied
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect("posts:feed")
    else:
        form = PostForm(instance=post)
    return render(request, "posts/post_form.html", {"form": form, "mode": "Edit", "post": post})


@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user and not request.user.is_campus_admin:
        raise PermissionDenied
    if request.method == "POST":
        post.delete()
        if request.headers.get("HX-Request"):
            return render(request, "posts/partials/post_list.html", {"posts": Post.objects.filter(status=Post.STATUS_APPROVED)})
        return redirect("posts:feed")
    return render(request, "posts/post_confirm_delete.html", {"post": post})
```

- [ ] **Step 7: Wire post URLs**

In `posts/urls.py`:

```python
from django.urls import path

from . import views

app_name = "posts"

urlpatterns = [
    path("", views.feed, name="feed"),
    path("posts/new/", views.create_post, name="create"),
    path("posts/<int:pk>/edit/", views.edit_post, name="edit"),
    path("posts/<int:pk>/delete/", views.delete_post, name="delete"),
]
```

- [ ] **Step 8: Run post tests**

Run:

```powershell
python manage.py test posts
```

Expected: template failures remain until shared templates are added.

- [ ] **Step 9: Checkpoint**

If git is initialized:

```powershell
git add posts
git commit -m "feat: add post model and feed views"
```

Expected: commit succeeds.

## Task 4: Interaction Models, Forms, Views, and HTMX Tests

**Files:**
- Create: `interactions/models.py`
- Create: `interactions/forms.py`
- Modify: `interactions/admin.py`
- Create: `interactions/views.py`
- Modify: `interactions/urls.py`
- Create: `interactions/tests.py`

- [ ] **Step 1: Write failing interaction tests**

Create `interactions/tests.py`:

```python
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from posts.models import Post

from .models import Comment, Reaction, Report


class InteractionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="student", password="StrongPass123")
        self.post = Post.objects.create(
            author=self.user,
            title="Improve Wi-Fi",
            description="Coverage is weak near the lab.",
            category=Post.CATEGORY_COMPLAINT,
        )

    def test_toggle_like_creates_and_removes_reaction(self):
        self.client.login(username="student", password="StrongPass123")

        response = self.client.post(reverse("interactions:toggle_reaction", args=[self.post.pk, "like"]), HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Reaction.objects.count(), 1)

        self.client.post(reverse("interactions:toggle_reaction", args=[self.post.pk, "like"]), HTTP_HX_REQUEST="true")
        self.assertEqual(Reaction.objects.count(), 0)

    def test_add_comment(self):
        self.client.login(username="student", password="StrongPass123")

        response = self.client.post(
            reverse("interactions:add_comment", args=[self.post.pk]),
            {"body": "I agree with this."},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), 1)

    def test_report_post(self):
        self.client.login(username="student", password="StrongPass123")

        response = self.client.post(
            reverse("interactions:report_post", args=[self.post.pk]),
            {"reason": Report.REASON_INAPPROPRIATE, "details": "Contains personal attacks."},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Report.objects.count(), 1)
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
python manage.py test interactions
```

Expected: failures because interaction models and URLs do not exist yet.

- [ ] **Step 3: Implement interaction models**

In `interactions/models.py`:

```python
from django.conf import settings
from django.db import models


class Reaction(models.Model):
    KIND_LIKE = "like"
    KIND_HEART = "heart"

    KIND_CHOICES = (
        (KIND_LIKE, "Like"),
        (KIND_HEART, "Heart"),
    )

    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reactions")
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["post", "user", "kind"], name="unique_post_user_reaction_kind")
        ]


class Comment(models.Model):
    STATUS_VISIBLE = "visible"
    STATUS_HIDDEN = "hidden"

    STATUS_CHOICES = (
        (STATUS_VISIBLE, "Visible"),
        (STATUS_HIDDEN, "Hidden"),
    )

    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="replies", blank=True, null=True)
    body = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_VISIBLE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"


class Report(models.Model):
    REASON_INAPPROPRIATE = "inappropriate"
    REASON_SPAM = "spam"
    REASON_HARASSMENT = "harassment"
    REASON_OTHER = "other"

    REASON_CHOICES = (
        (REASON_INAPPROPRIATE, "Inappropriate content"),
        (REASON_SPAM, "Spam"),
        (REASON_HARASSMENT, "Harassment"),
        (REASON_OTHER, "Other"),
    )

    STATUS_OPEN = "open"
    STATUS_RESOLVED = "resolved"
    STATUS_DISMISSED = "dismissed"

    STATUS_CHOICES = (
        (STATUS_OPEN, "Open"),
        (STATUS_RESOLVED, "Resolved"),
        (STATUS_DISMISSED, "Dismissed"),
    )

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports")
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="reports")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="reports", blank=True, null=True)
    reason = models.CharField(max_length=30, choices=REASON_CHOICES)
    details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name="reviewed_reports")
    reviewed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_reason_display()} report for {self.post}"
```

- [ ] **Step 4: Add forms**

In `interactions/forms.py`:

```python
from django import forms

from .models import Comment, Report


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("body", "parent")
        widgets = {
            "body": forms.Textarea(attrs={"rows": 2, "placeholder": "Write a comment"}),
            "parent": forms.HiddenInput(),
        }


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ("reason", "details")
        widgets = {
            "details": forms.Textarea(attrs={"rows": 3, "placeholder": "Add helpful context"}),
        }
```

- [ ] **Step 5: Add interaction views**

In `interactions/views.py`:

```python
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils import timezone

from posts.models import Post

from .forms import CommentForm, ReportForm
from .models import Comment, Reaction, Report


def _htmx_error(request, message, status=400):
    html = render_to_string("interactions/partials/inline_error.html", {"message": message}, request=request)
    return HttpResponse(html, status=status)


@login_required
def toggle_reaction(request, post_id, kind):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    if kind not in [Reaction.KIND_LIKE, Reaction.KIND_HEART]:
        return HttpResponseBadRequest("Unknown reaction")

    post = get_object_or_404(Post, pk=post_id, status=Post.STATUS_APPROVED)
    reaction, created = Reaction.objects.get_or_create(post=post, user=request.user, kind=kind)
    if not created:
        reaction.delete()
    return render(request, "interactions/partials/reaction_bar.html", {"post": post})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id, status=Post.STATUS_APPROVED)
    if request.method != "POST":
        form = CommentForm()
        return render(request, "interactions/partials/comment_form.html", {"post": post, "form": form})

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        form = CommentForm()
    comments = post.comments.filter(parent__isnull=True, status=Comment.STATUS_VISIBLE).select_related("author")
    return render(request, "interactions/partials/comment_list.html", {"post": post, "comments": comments, "form": form})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.author != request.user and not request.user.is_campus_admin:
        raise PermissionDenied
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    post = comment.post
    comment.delete()
    comments = post.comments.filter(parent__isnull=True, status=Comment.STATUS_VISIBLE).select_related("author")
    return render(request, "interactions/partials/comment_list.html", {"post": post, "comments": comments, "form": CommentForm()})


@login_required
def report_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method != "POST":
        return render(request, "interactions/partials/report_form.html", {"post": post, "form": ReportForm()})

    form = ReportForm(request.POST)
    if form.is_valid():
        report = form.save(commit=False)
        report.post = post
        report.reporter = request.user
        report.save()
        return render(request, "interactions/partials/inline_error.html", {"message": "Report submitted."})
    return render(request, "interactions/partials/report_form.html", {"post": post, "form": form}, status=400)


@login_required
def resolve_report(request, report_id, status):
    if not request.user.is_campus_admin:
        raise PermissionDenied
    if status not in [Report.STATUS_RESOLVED, Report.STATUS_DISMISSED]:
        return HttpResponseBadRequest("Unknown status")
    report = get_object_or_404(Report, pk=report_id)
    report.status = status
    report.reviewed_by = request.user
    report.reviewed_at = timezone.now()
    report.save(update_fields=["status", "reviewed_by", "reviewed_at"])
    return render(request, "dashboard/partials/report_row.html", {"report": report})
```

- [ ] **Step 6: Wire interaction URLs**

In `interactions/urls.py`:

```python
from django.urls import path

from . import views

app_name = "interactions"

urlpatterns = [
    path("posts/<int:post_id>/react/<str:kind>/", views.toggle_reaction, name="toggle_reaction"),
    path("posts/<int:post_id>/comments/", views.add_comment, name="add_comment"),
    path("comments/<int:comment_id>/delete/", views.delete_comment, name="delete_comment"),
    path("posts/<int:post_id>/report/", views.report_post, name="report_post"),
    path("reports/<int:report_id>/<str:status>/", views.resolve_report, name="resolve_report"),
]
```

- [ ] **Step 7: Add interaction admin**

In `interactions/admin.py`:

```python
from django.contrib import admin

from .models import Comment, Reaction, Report


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("body", "author__username", "post__title")


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ("post", "user", "kind", "created_at")
    list_filter = ("kind", "created_at")


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("post", "comment", "reporter", "reason", "status", "created_at")
    list_filter = ("reason", "status", "created_at")
    search_fields = ("post__title", "details", "reporter__username")
```

- [ ] **Step 8: Run interaction tests**

Run:

```powershell
python manage.py test interactions
```

Expected: template failures remain until partial templates are added.

- [ ] **Step 9: Checkpoint**

If git is initialized:

```powershell
git add interactions
git commit -m "feat: add htmx interactions"
```

Expected: commit succeeds.

## Task 5: Shared Templates, Feed UI, and HTMX Partials

**Files:**
- Create: `templates/base.html`
- Create: `templates/partials/messages.html`
- Create: `templates/partials/sidebar.html`
- Create: `templates/posts/feed.html`
- Create: `templates/posts/post_form.html`
- Create: `templates/posts/post_confirm_delete.html`
- Create: `templates/posts/partials/post_card.html`
- Create: `templates/posts/partials/post_list.html`
- Create: `templates/interactions/partials/reaction_bar.html`
- Create: `templates/interactions/partials/comment_list.html`
- Create: `templates/interactions/partials/comment_form.html`
- Create: `templates/interactions/partials/report_form.html`
- Create: `templates/interactions/partials/inline_error.html`
- Create: `static/css/app.css`
- Create: `static/js/app.js`

- [ ] **Step 1: Create base shell**

Create `templates/base.html`:

```django
{% load static %}
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}Campus Voice{% endblock %}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/htmx.org@1.9.12"></script>
  <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
  <link rel="stylesheet" href="{% static 'css/app.css' %}">
</head>
<body class="bg-[#FDFEFE] text-slate-900" x-data="{ sidebarOpen: false, postModal: false }">
  <div class="min-h-screen lg:grid lg:grid-cols-[260px_1fr]">
    {% include "partials/sidebar.html" %}
    <main class="min-w-0 px-4 py-5 sm:px-6 lg:px-8">
      {% include "partials/messages.html" %}
      {% block content %}{% endblock %}
    </main>
  </div>
  <script src="{% static 'js/app.js' %}"></script>
</body>
</html>
```

- [ ] **Step 2: Create sidebar**

Create `templates/partials/sidebar.html`:

```django
<button type="button" class="fixed left-4 top-4 z-40 rounded-md bg-[#2C3E94] px-3 py-2 text-sm font-medium text-white lg:hidden" @click="sidebarOpen = true">Menu</button>
<aside class="fixed inset-y-0 left-0 z-50 w-72 -translate-x-full border-r border-slate-200 bg-white px-5 py-6 shadow-xl transition lg:static lg:w-auto lg:translate-x-0 lg:shadow-none" :class="{ 'translate-x-0': sidebarOpen }">
  <div class="flex items-center justify-between">
    <a href="{% url 'posts:feed' %}" class="text-xl font-bold text-[#2C3E94]">Campus Voice</a>
    <button class="lg:hidden" type="button" @click="sidebarOpen = false">Close</button>
  </div>
  {% if user.is_authenticated %}
    <nav class="mt-8 space-y-2 text-sm font-medium">
      <a class="block rounded-md px-3 py-2 text-slate-700 hover:bg-sky-50 hover:text-[#2C3E94]" href="{% url 'posts:feed' %}">Feed</a>
      <a class="block rounded-md px-3 py-2 text-slate-700 hover:bg-sky-50 hover:text-[#2C3E94]" href="{% url 'posts:create' %}">Create Post</a>
      <a class="block rounded-md px-3 py-2 text-slate-700 hover:bg-sky-50 hover:text-[#2C3E94]" href="{% url 'accounts:profile' %}">Profile</a>
      {% if user.is_campus_admin %}
        <a class="block rounded-md px-3 py-2 text-slate-700 hover:bg-sky-50 hover:text-[#2C3E94]" href="{% url 'dashboard:index' %}">Dashboard</a>
        <a class="block rounded-md px-3 py-2 text-slate-700 hover:bg-sky-50 hover:text-[#2C3E94]" href="{% url 'dashboard:moderation' %}">Moderation</a>
      {% endif %}
    </nav>
    <form method="post" action="{% url 'accounts:logout' %}" class="mt-8">
      {% csrf_token %}
      <button class="rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-700">Logout</button>
    </form>
  {% else %}
    <nav class="mt-8 space-y-2 text-sm font-medium">
      <a class="block rounded-md px-3 py-2 text-slate-700 hover:bg-sky-50 hover:text-[#2C3E94]" href="{% url 'accounts:login' %}">Login</a>
      <a class="block rounded-md px-3 py-2 text-slate-700 hover:bg-sky-50 hover:text-[#2C3E94]" href="{% url 'accounts:register' %}">Register</a>
    </nav>
  {% endif %}
</aside>
```

- [ ] **Step 3: Create message partial**

Create `templates/partials/messages.html`:

```django
{% if messages %}
  <div class="mb-4 space-y-2">
    {% for message in messages %}
      <div class="rounded-md border border-sky-100 bg-sky-50 px-4 py-3 text-sm text-[#2C3E94]">{{ message }}</div>
    {% endfor %}
  </div>
{% endif %}
```

- [ ] **Step 4: Create feed and post templates**

Create `templates/posts/feed.html`:

```django
{% extends "base.html" %}
{% block title %}Feed{% endblock %}
{% block content %}
<header class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
  <div>
    <h1 class="text-2xl font-semibold text-[#2C3E94]">Student Feed</h1>
    <p class="text-sm text-slate-500">Ideas, concerns, and improvements from the campus community.</p>
  </div>
  <a href="{% url 'posts:create' %}" class="inline-flex items-center justify-center rounded-md bg-[#2C3E94] px-4 py-2 text-sm font-semibold text-white">New Post</a>
</header>
<div class="mb-5 flex flex-wrap gap-2">
  <a class="rounded-md border px-3 py-2 text-sm {% if sort == 'latest' %}bg-[#2C3E94] text-white{% endif %}" href="?sort=latest" hx-get="?sort=latest" hx-target="#post-list">Latest</a>
  <a class="rounded-md border px-3 py-2 text-sm {% if sort == 'most_liked' %}bg-[#2C3E94] text-white{% endif %}" href="?sort=most_liked" hx-get="?sort=most_liked" hx-target="#post-list">Most Liked</a>
  <a class="rounded-md border px-3 py-2 text-sm {% if sort == 'trending' %}bg-[#2C3E94] text-white{% endif %}" href="?sort=trending" hx-get="?sort=trending" hx-target="#post-list">Trending</a>
</div>
{% include "posts/partials/post_list.html" %}
{% endblock %}
```

Create `templates/posts/post_form.html`:

```django
{% extends "base.html" %}
{% block title %}{{ mode }} Post{% endblock %}
{% block content %}
<section class="mx-auto max-w-2xl">
  <h1 class="text-2xl font-semibold text-[#2C3E94]">{{ mode }} Post</h1>
  <form method="post" enctype="multipart/form-data" class="mt-6 space-y-4 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
    {% csrf_token %}
    {{ form.as_p }}
    <button class="rounded-md bg-[#2C3E94] px-4 py-2 font-medium text-white">Save</button>
    <a href="{% url 'posts:feed' %}" class="ml-2 text-sm text-slate-500">Cancel</a>
  </form>
</section>
{% endblock %}
```

Create `templates/posts/post_confirm_delete.html`:

```django
{% extends "base.html" %}
{% block title %}Delete Post{% endblock %}
{% block content %}
<section class="mx-auto max-w-lg rounded-lg border border-red-200 bg-white p-6 shadow-sm">
  <h1 class="text-xl font-semibold text-red-700">Delete post?</h1>
  <p class="mt-2 text-sm text-slate-600">{{ post.title }}</p>
  <form method="post" class="mt-6">
    {% csrf_token %}
    <button class="rounded-md bg-red-600 px-4 py-2 font-medium text-white">Delete</button>
    <a href="{% url 'posts:feed' %}" class="ml-2 text-sm text-slate-500">Cancel</a>
  </form>
</section>
{% endblock %}
```

- [ ] **Step 5: Create post card partials**

Create `templates/posts/partials/post_list.html`:

```django
<div id="post-list" class="space-y-4">
  {% for post in posts %}
    {% include "posts/partials/post_card.html" %}
  {% empty %}
    <div class="rounded-lg border border-dashed border-slate-300 bg-white p-10 text-center text-slate-500">No posts to show yet.</div>
  {% endfor %}
</div>
```

Create `templates/posts/partials/post_card.html`:

```django
<article id="post-{{ post.pk }}" class="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
  <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
    <div>
      <div class="mb-2 flex flex-wrap items-center gap-2 text-xs">
        <span class="rounded-full bg-sky-50 px-2 py-1 font-medium text-[#2C3E94]">{{ post.get_category_display }}</span>
        <span class="text-slate-400">{{ post.created_at|timesince }} ago</span>
      </div>
      <h2 class="text-lg font-semibold text-slate-950">{{ post.title }}</h2>
      <p class="mt-2 whitespace-pre-line text-sm leading-6 text-slate-600">{{ post.description }}</p>
    </div>
    {% if post.image %}
      <img src="{{ post.image.url }}" alt="" class="h-28 w-28 rounded-md object-cover">
    {% endif %}
  </div>
  <div class="mt-4 flex items-center justify-between border-t border-slate-100 pt-4">
    <div class="text-sm text-slate-500">By {{ post.author.get_full_name|default:post.author.username }}</div>
    <div class="flex items-center gap-2 text-sm">
      {% if post.author == user or user.is_campus_admin %}
        <a class="text-[#2C3E94]" href="{% url 'posts:edit' post.pk %}">Edit</a>
        <form method="post" action="{% url 'posts:delete' post.pk %}" hx-post="{% url 'posts:delete' post.pk %}" hx-target="#post-list" class="inline">
          {% csrf_token %}
          <button class="text-red-600">Delete</button>
        </form>
      {% endif %}
    </div>
  </div>
  <div class="mt-4">
    {% include "interactions/partials/reaction_bar.html" %}
  </div>
  <div class="mt-4">
    {% include "interactions/partials/comment_list.html" with comments=post.comments.all form=None %}
  </div>
</article>
```

- [ ] **Step 6: Create interaction partials**

Create `templates/interactions/partials/reaction_bar.html`:

```django
<div id="reactions-{{ post.pk }}" class="flex flex-wrap items-center gap-2">
  <form method="post" action="{% url 'interactions:toggle_reaction' post.pk 'like' %}" hx-post="{% url 'interactions:toggle_reaction' post.pk 'like' %}" hx-target="#reactions-{{ post.pk }}" hx-swap="outerHTML">
    {% csrf_token %}
    <button class="rounded-md border border-slate-200 px-3 py-1.5 text-sm hover:bg-sky-50">Like {{ post.like_count }}</button>
  </form>
  <form method="post" action="{% url 'interactions:toggle_reaction' post.pk 'heart' %}" hx-post="{% url 'interactions:toggle_reaction' post.pk 'heart' %}" hx-target="#reactions-{{ post.pk }}" hx-swap="outerHTML">
    {% csrf_token %}
    <button class="rounded-md border border-slate-200 px-3 py-1.5 text-sm hover:bg-sky-50">Heart {{ post.heart_count }}</button>
  </form>
  <button class="rounded-md border border-slate-200 px-3 py-1.5 text-sm text-slate-600">{{ post.comment_count }} comments</button>
  <button class="rounded-md border border-slate-200 px-3 py-1.5 text-sm text-slate-600" hx-get="{% url 'interactions:report_post' post.pk %}" hx-target="#report-{{ post.pk }}">Report</button>
  <div id="report-{{ post.pk }}"></div>
</div>
```

Create `templates/interactions/partials/comment_list.html`:

```django
<div id="comments-{{ post.pk }}" class="space-y-3">
  {% for comment in comments %}
    {% if comment.status == "visible" and not comment.parent_id %}
      <div class="rounded-md bg-slate-50 p-3 text-sm">
        <div class="font-medium text-slate-800">{{ comment.author.username }}</div>
        <p class="mt-1 text-slate-600">{{ comment.body }}</p>
      </div>
    {% endif %}
  {% endfor %}
  {% include "interactions/partials/comment_form.html" %}
</div>
```

Create `templates/interactions/partials/comment_form.html`:

```django
<form method="post" action="{% url 'interactions:add_comment' post.pk %}" hx-post="{% url 'interactions:add_comment' post.pk %}" hx-target="#comments-{{ post.pk }}" hx-swap="outerHTML" class="mt-3 flex gap-2">
  {% csrf_token %}
  <textarea name="body" rows="1" class="min-h-10 flex-1 rounded-md border border-slate-200 px-3 py-2 text-sm" placeholder="Write a comment"></textarea>
  <button class="rounded-md bg-[#2C3E94] px-3 py-2 text-sm font-medium text-white">Send</button>
</form>
```

Create `templates/interactions/partials/report_form.html`:

```django
<form method="post" action="{% url 'interactions:report_post' post.pk %}" hx-post="{% url 'interactions:report_post' post.pk %}" hx-target="#report-{{ post.pk }}" class="mt-3 space-y-2 rounded-md border border-slate-200 bg-slate-50 p-3">
  {% csrf_token %}
  {{ form.as_p }}
  <button class="rounded-md bg-[#2C3E94] px-3 py-2 text-sm font-medium text-white">Submit report</button>
</form>
```

Create `templates/interactions/partials/inline_error.html`:

```django
<div class="rounded-md border border-sky-100 bg-sky-50 px-3 py-2 text-sm text-[#2C3E94]">{{ message }}</div>
```

- [ ] **Step 7: Add small static files**

Create `static/css/app.css`:

```css
input,
select,
textarea {
  width: 100%;
  border: 1px solid #cbd5e1;
  border-radius: 0.375rem;
  padding: 0.625rem 0.75rem;
}

label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #334155;
  margin-bottom: 0.25rem;
}

.errorlist {
  color: #b91c1c;
  font-size: 0.875rem;
}
```

Create `static/js/app.js`:

```javascript
document.body.addEventListener("htmx:configRequest", (event) => {
  const tokenInput = document.querySelector("input[name='csrfmiddlewaretoken']");
  if (tokenInput) {
    event.detail.headers["X-CSRFToken"] = tokenInput.value;
  }
});
```

- [ ] **Step 8: Run template-backed tests**

Run:

```powershell
python manage.py test accounts posts interactions
```

Expected: model and route tests pass or expose specific template/context defects to fix before continuing.

- [ ] **Step 9: Checkpoint**

If git is initialized:

```powershell
git add templates static
git commit -m "feat: add mvp templates and htmx partials"
```

Expected: commit succeeds.

## Task 6: Dashboard Views, Moderation, and Tests

**Files:**
- Create: `dashboard/views.py`
- Modify: `dashboard/urls.py`
- Create: `dashboard/tests.py`
- Create: `templates/dashboard/index.html`
- Create: `templates/dashboard/moderation.html`
- Create: `templates/dashboard/partials/report_row.html`

- [ ] **Step 1: Write failing dashboard tests**

Create `dashboard/tests.py`:

```python
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from interactions.models import Report
from posts.models import Post


class DashboardTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.student = User.objects.create_user(username="student", password="StrongPass123")
        self.admin = User.objects.create_user(username="admin", password="StrongPass123", role="admin", is_staff=True)
        self.post = Post.objects.create(
            author=self.student,
            title="Campus lighting",
            description="Paths need more light.",
            category=Post.CATEGORY_COMPLAINT,
        )

    def test_student_cannot_access_dashboard(self):
        self.client.login(username="student", password="StrongPass123")
        response = self.client.get(reverse("dashboard:index"))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_access_dashboard(self):
        self.client.login(username="admin", password="StrongPass123")
        response = self.client.get(reverse("dashboard:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Total Posts")

    def test_admin_can_view_reports(self):
        Report.objects.create(
            reporter=self.student,
            post=self.post,
            reason=Report.REASON_INAPPROPRIATE,
            details="Needs review.",
        )
        self.client.login(username="admin", password="StrongPass123")
        response = self.client.get(reverse("dashboard:moderation"))
        self.assertContains(response, "Needs review.")
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
python manage.py test dashboard
```

Expected: failures because dashboard views and templates do not exist yet.

- [ ] **Step 3: Add dashboard views**

In `dashboard/views.py`:

```python
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import render

from accounts.models import User
from interactions.models import Comment, Report
from posts.models import Post


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        if not request.user.is_campus_admin:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@admin_required
def index(request):
    total_posts = Post.objects.count()
    total_comments = Comment.objects.count()
    open_reports = Report.objects.filter(status=Report.STATUS_OPEN).count()
    active_students = User.objects.filter(role=User.ROLE_STUDENT).annotate(post_total=Count("posts")).order_by("-post_total")[:5]
    most_reported_posts = Post.objects.annotate(report_total=Count("reports")).order_by("-report_total", "-created_at")[:5]
    context = {
        "total_posts": total_posts,
        "total_comments": total_comments,
        "open_reports": open_reports,
        "active_students": active_students,
        "most_reported_posts": most_reported_posts,
    }
    return render(request, "dashboard/index.html", context)


@login_required
@admin_required
def moderation(request):
    reports = Report.objects.select_related("post", "comment", "reporter").order_by("-created_at")
    posts = Post.objects.select_related("author").order_by("-created_at")[:50]
    comments = Comment.objects.select_related("author", "post").order_by("-created_at")[:50]
    return render(request, "dashboard/moderation.html", {"reports": reports, "posts": posts, "comments": comments})
```

- [ ] **Step 4: Wire dashboard URLs**

In `dashboard/urls.py`:

```python
from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.index, name="index"),
    path("moderation/", views.moderation, name="moderation"),
]
```

- [ ] **Step 5: Add dashboard templates**

Create `templates/dashboard/index.html`:

```django
{% extends "base.html" %}
{% block title %}Admin Dashboard{% endblock %}
{% block content %}
<header class="mb-6">
  <h1 class="text-2xl font-semibold text-[#2C3E94]">Admin Dashboard</h1>
  <p class="text-sm text-slate-500">Engagement and moderation overview.</p>
</header>
<section class="grid gap-4 sm:grid-cols-3">
  <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"><div class="text-sm text-slate-500">Total Posts</div><div class="mt-2 text-3xl font-semibold">{{ total_posts }}</div></div>
  <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"><div class="text-sm text-slate-500">Comments</div><div class="mt-2 text-3xl font-semibold">{{ total_comments }}</div></div>
  <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"><div class="text-sm text-slate-500">Open Reports</div><div class="mt-2 text-3xl font-semibold">{{ open_reports }}</div></div>
</section>
<section class="mt-6 grid gap-6 lg:grid-cols-2">
  <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
    <h2 class="font-semibold text-slate-900">Most Active Students</h2>
    <div class="mt-4 space-y-3">
      {% for student in active_students %}
        <div class="flex justify-between text-sm"><span>{{ student.username }}</span><span>{{ student.post_total }} posts</span></div>
      {% empty %}
        <p class="text-sm text-slate-500">No activity yet.</p>
      {% endfor %}
    </div>
  </div>
  <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
    <h2 class="font-semibold text-slate-900">Most Reported Issues</h2>
    <div class="mt-4 space-y-3">
      {% for post in most_reported_posts %}
        <div class="flex justify-between gap-4 text-sm"><span>{{ post.title }}</span><span>{{ post.report_total }} reports</span></div>
      {% empty %}
        <p class="text-sm text-slate-500">No reports yet.</p>
      {% endfor %}
    </div>
  </div>
</section>
{% endblock %}
```

Create `templates/dashboard/moderation.html`:

```django
{% extends "base.html" %}
{% block title %}Moderation{% endblock %}
{% block content %}
<header class="mb-6">
  <h1 class="text-2xl font-semibold text-[#2C3E94]">Moderation</h1>
  <p class="text-sm text-slate-500">Review flagged content and recent campus posts.</p>
</header>
<section class="rounded-lg border border-slate-200 bg-white shadow-sm">
  <div class="border-b border-slate-200 p-4 font-semibold">Reports</div>
  <div class="divide-y divide-slate-100">
    {% for report in reports %}
      {% include "dashboard/partials/report_row.html" %}
    {% empty %}
      <div class="p-6 text-sm text-slate-500">No reports yet.</div>
    {% endfor %}
  </div>
</section>
{% endblock %}
```

Create `templates/dashboard/partials/report_row.html`:

```django
<div id="report-{{ report.pk }}" class="grid gap-3 p-4 text-sm lg:grid-cols-[1fr_auto]">
  <div>
    <div class="font-medium text-slate-900">{{ report.post.title }}</div>
    <div class="text-slate-500">{{ report.get_reason_display }} by {{ report.reporter.username }}</div>
    <p class="mt-1 text-slate-600">{{ report.details }}</p>
    <div class="mt-1 text-xs uppercase tracking-wide text-slate-400">{{ report.status }}</div>
  </div>
  {% if report.status == "open" %}
    <div class="flex items-center gap-2">
      <form method="post" action="{% url 'interactions:resolve_report' report.pk 'resolved' %}" hx-post="{% url 'interactions:resolve_report' report.pk 'resolved' %}" hx-target="#report-{{ report.pk }}" hx-swap="outerHTML">
        {% csrf_token %}
        <button class="rounded-md bg-[#2C3E94] px-3 py-2 text-white">Resolve</button>
      </form>
      <form method="post" action="{% url 'interactions:resolve_report' report.pk 'dismissed' %}" hx-post="{% url 'interactions:resolve_report' report.pk 'dismissed' %}" hx-target="#report-{{ report.pk }}" hx-swap="outerHTML">
        {% csrf_token %}
        <button class="rounded-md border border-slate-300 px-3 py-2">Dismiss</button>
      </form>
    </div>
  {% endif %}
</div>
```

- [ ] **Step 6: Run dashboard tests**

Run:

```powershell
python manage.py test dashboard
```

Expected: dashboard tests pass or expose specific permission/template defects to fix.

- [ ] **Step 7: Checkpoint**

If git is initialized:

```powershell
git add dashboard templates/dashboard
git commit -m "feat: add admin dashboard"
```

Expected: commit succeeds.

## Task 7: Migrations, Database Reset, and End-to-End Verification

**Files:**
- Create: `accounts/migrations/0001_initial.py`
- Create: `posts/migrations/0001_initial.py`
- Create: `interactions/migrations/0001_initial.py`
- Modify: `db.sqlite3`

- [ ] **Step 1: Remove the old SQLite database**

Run:

```powershell
Remove-Item -LiteralPath .\db.sqlite3
```

Expected: `db.sqlite3` is removed. This is required because the custom user model must exist before auth tables are created.

- [ ] **Step 2: Create migrations**

Run:

```powershell
python manage.py makemigrations accounts posts interactions
```

Expected: initial migrations are created for `accounts`, `posts`, and `interactions`.

- [ ] **Step 3: Apply migrations**

Run:

```powershell
python manage.py migrate
```

Expected: all migrations apply cleanly and a new `db.sqlite3` exists.

- [ ] **Step 4: Create admin user**

Run:

```powershell
python manage.py createsuperuser
```

Expected: interactive prompt creates a user. Use `campus_admin` as the username for this smoke-test account. After creation, set role in Django shell if needed:

```powershell
python manage.py shell
```

Then run:

```python
from django.contrib.auth import get_user_model
user = get_user_model().objects.get(username="campus_admin")
user.role = "admin"
user.is_staff = True
user.is_superuser = True
user.save()
```

- [ ] **Step 5: Run full test suite**

Run:

```powershell
python manage.py test
```

Expected: all tests pass.

- [ ] **Step 6: Run system check**

Run:

```powershell
python manage.py check
```

Expected: `System check identified no issues`.

- [ ] **Step 7: Run local server**

Run:

```powershell
python manage.py runserver
```

Expected: server starts at `http://127.0.0.1:8000/`.

- [ ] **Step 8: Manual browser smoke test**

In the browser:

1. Open `http://127.0.0.1:8000/accounts/register/`.
2. Register a student account.
3. Confirm redirect to feed.
4. Create a post.
5. Like and heart the post.
6. Add a comment.
7. Report the post.
8. Log out.
9. Log in as admin.
10. Open `/dashboard/`.
11. Open `/dashboard/moderation/`.
12. Resolve the report.

Expected: every page loads, HTMX interactions update in place, and the admin dashboard shows the created engagement.

- [ ] **Step 9: Checkpoint**

If git is initialized:

```powershell
git add accounts posts interactions dashboard templates static campus_engagement_system db.sqlite3
git commit -m "feat: complete phase 1 campus engagement mvp"
```

Expected: commit succeeds.

## Task 8: README Setup Guide

**Files:**
- Modify: `ReadME.md`

- [ ] **Step 1: Replace README with setup guide**

Use this structure in `ReadME.md`:

```markdown
# Campus Engagement System

A Django-based student feedback and engagement system where students share ideas, raise campus concerns, react, comment, and report content while admins monitor engagement and moderate reports.

## Tech Stack

- Django
- Django ORM
- SQLite for development
- Django Templates
- Tailwind CSS CDN
- HTMX
- Alpine.js

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install django pillow
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Apps

- `accounts`: custom users, registration, login, profile, role redirects.
- `posts`: feed, post creation, post editing, post deletion, sorting.
- `interactions`: reactions, comments, reports, HTMX partial updates.
- `dashboard`: admin metrics and moderation.

## Phase 1 Flow

1. Student registers and lands on the feed.
2. Student creates an idea or concern.
3. Students react and comment through HTMX.
4. Students report content.
5. Admin reviews dashboard metrics and resolves reports.

## Tests

```powershell
python manage.py test
python manage.py check
```
```

- [ ] **Step 2: Run README command sanity check**

Run:

```powershell
python manage.py check
```

Expected: `System check identified no issues`.

- [ ] **Step 3: Checkpoint**

If git is initialized:

```powershell
git add ReadME.md
git commit -m "docs: add phase 1 setup guide"
```

Expected: commit succeeds.

## Self-Review Checklist

- Phase 1 spec coverage: accounts, posts, interactions, dashboard, templates, tests, migrations, and README are covered.
- No Phase 2 feature is required to complete Phase 1.
- No Phase 3-only polish is required to complete Phase 1.
- All routes referenced by tests are defined by the plan.
- All model relations referenced by templates are defined by the plan.
- The old SQLite database reset is explicit because a custom user model is introduced.
- HTMX partials return HTML and keep CSRF protection through forms.
- Admin-only views raise `403` for non-admin users.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-26-phase-1-campus-engagement-mvp.md`. Two execution options:

1. **Subagent-Driven (recommended)** - dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** - execute tasks in this session using executing-plans, batch execution with checkpoints.
