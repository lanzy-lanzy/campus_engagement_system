# Admin Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a comprehensive admin dashboard with 4 main sections: User Management, Content Management, Analytics, and System Settings. Admins should be able to view, search, filter, edit, and manage users and content with full control.

**Architecture:** Extend the existing `dashboard` app. Add new views and templates. Use Django's HTMX pattern for partial updates. Reuse existing permissions system (manage_users, moderate_content, view_dashboard) and create new ones as needed.

**Tech Stack:** Django views/templates/tests, HTMX, Alpine.js, Tailwind utility classes, `python manage.py test`.

---

## File Structure

- Modify: `dashboard/views.py` - Add user management, content management, analytics, and settings views
- Modify: `dashboard/urls.py` - Add new routes for each section
- Modify: `accounts/models.py` - Add CODE_BULK_ACTIONS permission if needed
- Create: `templates/dashboard/users.html` - User management list view
- Create: `templates/dashboard/user_edit.html` - User edit/create form
- Create: `templates/dashboard/posts.html` - Content management list view
- Create: `templates/dashboard/post_edit.html` - Post edit form with admin status controls
- Create: `templates/dashboard/analytics.html` - Analytics dashboard view
- Create: `templates/dashboard/settings.html` - System settings view
- Modify: `templates/partials/sidebar.html` - Add navigation links to new sections
- Modify: `dashboard/tests.py` - Add tests for admin views

---

### Task 1: User Management Views

**Files:**
- Modify: `dashboard/views.py`
- Modify: `dashboard/urls.py`
- Create: `templates/dashboard/users.html`
- Create: `templates/dashboard/user_edit.html`

- [ ] **Step 1: Write failing user list test**

Add to `dashboard/tests.py`:

```python
def test_admin_can_view_user_list(self):
    user = get_user_model().objects.create_user(
        email="admin@test.com", username="admin", password="Pass123"
    )
    user.role = User.ROLE_ADMIN
    user.save()
    get_user_model().objects.create_user(
        email="student@test.com", username="student", password="Pass123"
    )
    self.client.login(email="admin@test.com", password="Pass123")

    response = self.client.get(reverse("dashboard:users"))

    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "admin")
    self.assertContains(response, "student")
    self.assertContains(response, "Search")
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```powershell
python manage.py test dashboard.tests.DashboardViewTests.test_admin_can_view_user_list
```

Expected: FAIL - no users URL exists yet.

- [ ] **Step 3: Add user management URLs**

In `dashboard/urls.py`, add:

```python
path("users/", views.user_list, name="users"),
path("users/new/", views.user_create, name="user_create"),
path("users/<int:user_id>/edit/", views.user_edit, name="user_edit"),
path("users/<int:user_id>/delete/", views.user_delete, name="user_delete"),
path("users/<int:user_id>/toggle/", views.user_toggle_active, name="user_toggle"),
```

- [ ] **Step 4: Add user management views**

In `dashboard/views.py`, add after existing views:

```python
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied

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
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(student_id__icontains=search)
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
```

- [ ] **Step 5: Create user list template**

Create `templates/dashboard/users.html`:

```django
{% extends "base.html" %}
{% block title %}Users - Admin Dashboard{% endblock %}
{% block content %}
<div class="animate-fade-in mb-5">
  <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
    <div>
      <h1 class="text-2xl font-extrabold text-[#1c1e21] mb-1">User Management</h1>
      <p class="text-[15px] text-[#65676b]">Manage campus users and roles</p>
    </div>
    <a href="{% url 'dashboard:user_create' %}" class="btn-fb btn-primary-fb">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
      Add User
    </a>
  </div>
</div>

<form method="get" class="cv-card p-4 mb-5 flex flex-wrap gap-3 items-center">
  <div class="flex-1 min-w-[200px]">
    <input type="text" name="search" value="{{ search }}" placeholder="Search users..." class="cv-input w-full">
  </div>
  <select name="role" class="cv-select">
    <option value="">All Roles</option>
    {% for value, label in roles %}
    <option value="{{ value }}" {% if role_filter == value %}selected{% endif %}>{{ label }}</option>
    {% endfor %}
  </select>
  <select name="status" class="cv-select">
    <option value="">All Status</option>
    <option value="active" {% if status_filter == "active" %}selected{% endif %}>Active</option>
    <option value="inactive" {% if status_filter == "inactive" %}selected{% endif %}>Inactive</option>
  </select>
  <button type="submit" class="btn-fb btn-secondary-fb">Filter</button>
  <a href="{% url 'dashboard:users' %}" class="btn-fb btn-secondary-fb">Clear</a>
</form>

<div class="cv-card overflow-hidden">
  <table class="w-full">
    <thead class="bg-[#f0f2f5]">
      <tr>
        <th class="cv-th text-left">User</th>
        <th class="cv-th text-left">Role</th>
        <th class="cv-th text-left">Department</th>
        <th class="cv-th text-left">Status</th>
        <th class="cv-th text-left">Joined</th>
        <th class="cv-th text-right">Actions</th>
      </tr>
    </thead>
    <tbody>
      {% for user in users %}
      <tr class="border-t border-[#ddd]">
        <td class="cv-td">
          <div class="flex items-center gap-3">
            <div class="cv-avatar-placeholder w-10 h-10">{{ user.username|upper|slice:":1" }}</div>
            <div>
              <div class="font-semibold text-[#050505]">{{ user.get_full_name|default:user.username }}</div>
              <div class="text-[13px] text-[#65676b]">{{ user.email }}</div>
            </div>
          </div>
        </td>
        <td class="cv-td">
          <span class="cv-chip{% if user.role == 'admin' %} bg-purple-100 text-purple-700{% elif user.role == 'moderator' %} bg-blue-100 text-blue-700{% else %} bg-gray-100 text-gray-700{% endif %}">
            {{ user.get_role_display }}
          </span>
        </td>
        <td class="cv-td text-[14px]">{{ user.department|default:"-" }}</td>
        <td class="cv-td">
          {% if user.is_active %}
          <span class="cv-chip bg-green-100 text-green-700">Active</span>
          {% else %}
          <span class="cv-chip bg-red-100 text-red-700">Inactive</span>
          {% endif %}
        </td>
        <td class="cv-td text-[14px] text-[#65676b]">{{ user.date_joined|date:"M d, Y" }}</td>
        <td class="cv-td text-right">
          <div class="flex gap-2 justify-end">
            <a href="{% url 'dashboard:user_edit' user.pk %}" class="text-[#1877f2] hover:underline text-sm">Edit</a>
            <form method="post" action="{% url 'dashboard:user_toggle' user.pk %}">
              {% csrf_token %}
              <button type="submit" class="text-[14px] hover:underline {% if user.is_active %}text-red-600{% else %}text-green-600{% endif %}">
                {% if user.is_active %}Deactivate{% else %}Activate{% endif %}
              </button>
            </form>
          </div>
        </td>
      </tr>
      {% empty %}
      <tr>
        <td colspan="6" class="cv-td text-center py-8 text-[#65676b]">No users found</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% endblock %}
```

- [ ] **Step 6: Create user edit template**

Create `templates/dashboard/user_edit.html`:

```django
{% extends "base.html" %}
{% block title %}{% if user_obj %}Edit User{% else %}Add User{% endif %} - Admin Dashboard{% endblock %}
{% block content %}
<div class="animate-fade-in mb-5">
  <h1 class="text-2xl font-extrabold text-[#1c1e21] mb-1">{% if user_obj %}Edit User{% else %}Add New User{% endif %}</h1>
  <p class="text-[15px] text-[#65676b]">{% if user_obj %}Update user details{% else %}Create a new user account{% endif %}</p>
</div>

<div class="cv-card p-6 max-w-2xl">
  <form method="post" class="space-y-4">
    {% csrf_token %}
    
    <div>
      <label class="cv-label">Email</label>
      <input type="email" name="email" value="{{ user_obj.email|default:"" }}" class="cv-input w-full" {% if user_obj %}readonly{% endif %} required>
    </div>
    
    <div>
      <label class="cv-label">Username</label>
      <input type="text" name="username" value="{{ user_obj.username|default:"" }}" class="cv-input w-full" {% if user_obj %}readonly{% endif %} required>
    </div>
    
    {% if not user_obj %}
    <div>
      <label class="cv-label">Password</label>
      <input type="password" name="password" class="cv-input w-full" required>
    </div>
    {% endif %}
    
    <div class="grid grid-cols-2 gap-4">
      <div>
        <label class="cv-label">First Name</label>
        <input type="text" name="first_name" value="{{ user_obj.first_name|default:"" }}" class="cv-input w-full">
      </div>
      <div>
        <label class="cv-label">Last Name</label>
        <input type="text" name="last_name" value="{{ user_obj.last_name|default:"" }}" class="cv-input w-full">
      </div>
    </div>
    
    <div>
      <label class="cv-label">Role</label>
      <select name="role" class="cv-select w-full">
        {% for value, label in roles %}
        <option value="{{ value }}" {% if user_obj.role == value %}selected{% endif %}>{{ label }}</option>
        {% endfor %}
      </select>
    </div>
    
    <div>
      <label class="cv-label">Department</label>
      <input type="text" name="department" value="{{ user_obj.department|default:"" }}" class="cv-input w-full">
    </div>
    
    <div>
      <label class="cv-label">Student ID</label>
      <input type="text" name="student_id" value="{{ user_obj.student_id|default:"" }}" class="cv-input w-full">
    </div>
    
    <div>
      <label class="cv-label">Bio</label>
      <textarea name="bio" rows="3" class="cv-textarea w-full">{{ user_obj.bio|default:"" }}</textarea>
    </div>
    
    <div class="flex gap-3 pt-4">
      <button type="submit" class="btn-fb btn-primary-fb">{% if user_obj %}Save Changes{% else %}Create User{% endif %}</button>
      <a href="{% url 'dashboard:users' %}" class="btn-fb btn-secondary-fb">Cancel</a>
    </div>
  </form>
</div>
{% endblock %}
```

- [ ] **Step 7: Run user management tests**

Run all new tests:

```powershell
python manage.py test dashboard.tests.DashboardViewTests.test_admin_can_view_user_list
```

Expected: PASS.

---

### Task 2: Content Management Views

**Files:**
- Modify: `dashboard/views.py`
- Modify: `dashboard/urls.py`
- Create: `templates/dashboard/posts.html`
- Create: `templates/dashboard/post_edit.html`

- [ ] **Step 1: Write failing content list test**

Add to `dashboard/tests.py`:

```python
def test_admin_can_view_post_list(self):
    user = get_user_model().objects.create_user(
        email="admin@test.com", username="admin", password="Pass123"
    )
    user.role = User.ROLE_ADMIN
    user.save()
    Post.objects.create(
        author=user, title="Test Post", description="Test", category=Post.CATEGORY_SUGGESTION
    )
    self.client.login(email="admin@test.com", password="Pass123")

    response = self.client.get(reverse("dashboard:posts"))

    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "Test Post")
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```powershell
python manage.py test dashboard.tests.DashboardViewTests.test_admin_can_view_post_list
```

Expected: FAIL - no posts URL exists.

- [ ] **Step 3: Add content management URLs**

In `dashboard/urls.py`, add:

```python
path("posts/", views.post_list, name="posts"),
path("posts/<int:post_id>/edit/", views.post_edit, name="post_edit"),
path("posts/<int:post_id>/delete/", views.post_delete, name="post_delete"),
path("posts/<int:post_id>/status/", views.post_status, name="post_status"),
```

- [ ] **Step 4: Add content management views**

In `dashboard/views.py`, add:

```python
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
            Q(title__icontains=search) |
            Q(description__icontains=search)
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
```

- [ ] **Step 5: Create post list template**

Create `templates/dashboard/posts.html`:

```django
{% extends "base.html" %}
{% block title %}Content - Admin Dashboard{% endblock %}
{% block content %}
<div class="animate-fade-in mb-5">
  <h1 class="text-2xl font-extrabold text-[#1c1e21] mb-1">Content Management</h1>
  <p class="text-[15px] text-[#65676b]">Manage posts and moderation status</p>
</div>

<form method="get" class="cv-card p-4 mb-5 flex flex-wrap gap-3 items-center">
  <div class="flex-1 min-w-[200px]">
    <input type="text" name="search" value="{{ search }}" placeholder="Search posts..." class="cv-input w-full">
  </div>
  <select name="category" class="cv-select">
    <option value="">All Categories</option>
    {% for value, label in categories %}
    <option value="{{ value }}" {% if category_filter == value %}selected{% endif %}>{{ label }}</option>
    {% endfor %}
  </select>
  <select name="status" class="cv-select">
    <option value="">All Statuses</option>
    {% for value, label in statuses %}
    <option value="{{ value }}" {% if status_filter == value %}selected{% endif %}>{{ label }}</option>
    {% endfor %}
  </select>
  <select name="admin_status" class="cv-select">
    <option value="">All Admin Status</option>
    {% for value, label in admin_statuses %}
    <option value="{{ value }}" {% if admin_status_filter == value %}selected{% endif %}>{{ label }}</option>
    {% endfor %}
  </select>
  <button type="submit" class="btn-fb btn-secondary-fb">Filter</button>
  <a href="{% url 'dashboard:posts' %}" class="btn-fb btn-secondary-fb">Clear</a>
</form>

<div class="cv-card overflow-hidden">
  <table class="w-full">
    <thead class="bg-[#f0f2f5]">
      <tr>
        <th class="cv-th text-left">Title</th>
        <th class="cv-th text-left">Author</th>
        <th class="cv-th text-left">Category</th>
        <th class="cv-th text-left">Status</th>
        <th class="cv-th text-left">Admin Status</th>
        <th class="cv-th text-left">Created</th>
        <th class="cv-th text-right">Actions</th>
      </tr>
    </thead>
    <tbody>
      {% for post in posts %}
      <tr class="border-t border-[#ddd]">
        <td class="cv-td">
          <div class="font-semibold text-[#050505] max-w-[300px] truncate">{{ post.title }}</div>
        </td>
        <td class="cv-td text-[14px]">{{ post.author.username }}</td>
        <td class="cv-td">
          <span class="cv-chip bg-gray-100 text-gray-700">{{ post.get_category_display }}</span>
        </td>
        <td class="cv-td">
          <span class="cv-chip{% if post.status == 'approved' %} bg-green-100 text-green-700{% elif post.status == 'pending' %} bg-yellow-100 text-yellow-700{% else %} bg-red-100 text-red-700{% endif %}">
            {{ post.get_status_display }}
          </span>
        </td>
        <td class="cv-td">
          <span class="cv-chip{% if post.admin_status == 'none' %} bg-gray-100 text-gray-700{% elif post.admin_status == 'completed' %} bg-green-100 text-green-700{% elif post.admin_status == 'in_progress' %} bg-blue-100 text-blue-700{% else %} bg-yellow-100 text-yellow-700{% endif %}">
            {{ post.get_admin_status_display }}
          </span>
        </td>
        <td class="cv-td text-[14px] text-[#65676b]">{{ post.created_at|date:"M d, Y" }}</td>
        <td class="cv-td text-right">
          <div class="flex gap-2 justify-end">
            <a href="{% url 'dashboard:post_edit' post.pk %}" class="text-[#1877f2] hover:underline text-sm">Edit</a>
            <form method="post" action="{% url 'dashboard:post_delete' post.pk %}">
              {% csrf_token %}
              <button type="submit" class="text-red-600 hover:underline text-sm" onclick="return confirm('Delete this post?')">Delete</button>
            </form>
          </div>
        </td>
      </tr>
      {% empty %}
      <tr>
        <td colspan="7" class="cv-td text-center py-8 text-[#65676b]">No posts found</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% endblock %}
```

- [ ] **Step 6: Create post edit template**

Create `templates/dashboard/post_edit.html`:

```django
{% extends "base.html" %}
{% block title %}Edit Post - Admin Dashboard{% endblock %}
{% block content %}
<div class="animate-fade-in mb-5">
  <h1 class="text-2xl font-extrabold text-[#1c1e21] mb-1">Edit Post</h1>
  <p class="text-[15px] text-[#65676b]">Update post content and moderation status</p>
</div>

<div class="grid gap-6 lg:grid-cols-3">
  <div class="cv-card p-6 lg:col-span-2">
    <form method="post" class="space-y-4">
      {% csrf_token %}
      
      <div>
        <label class="cv-label">Title</label>
        <input type="text" name="title" value="{{ post.title }}" class="cv-input w-full" required>
      </div>
      
      <div>
        <label class="cv-label">Description</label>
        <textarea name="description" rows="6" class="cv-textarea w-full" required>{{ post.description }}</textarea>
      </div>
      
      <div>
        <label class="cv-label">Category</label>
        <select name="category" class="cv-select w-full">
          {% for value, label in categories %}
          <option value="{{ value }}" {% if post.category == value %}selected{% endif %}>{{ label }}</option>
          {% endfor %}
        </select>
      </div>
      
      <div>
        <label class="cv-label">Status</label>
        <select name="status" class="cv-select w-full">
          {% for value, label in statuses %}
          <option value="{{ value }}" {% if post.status == value %}selected{% endif %}>{{ label }}</option>
          {% endfor %}
        </select>
      </div>
      
      <div>
        <label class="cv-label">Admin Status</label>
        <select name="admin_status" class="cv-select w-full">
          {% for value, label in admin_statuses %}
          <option value="{{ value }}" {% if post.admin_status == value %}selected{% endif %}>{{ label }}</option>
          {% endfor %}
        </select>
      </div>
      
      <div class="flex gap-3 pt-4">
        <button type="submit" class="btn-fb btn-primary-fb">Save Changes</button>
        <a href="{% url 'dashboard:posts' %}" class="btn-fb btn-secondary-fb">Cancel</a>
      </div>
    </form>
  </div>
  
  <div class="cv-card p-6">
    <h3 class="text-[17px] font-bold text-[#1c1e21] mb-3">Post Info</h3>
    <dl class="space-y-3 text-sm">
      <div>
        <dt class="text-[#65676b]">Author</dt>
        <dd class="font-semibold">{{ post.author.username }}</dd>
      </div>
      <div>
        <dt class="text-[#65676b]">Created</dt>
        <dd>{{ post.created_at|date:"F d, Y g:i A" }}</dd>
      </div>
      <div>
        <dt class="text-[#65676b]">Updated</dt>
        <dd>{{ post.updated_at|date:"F d, Y g:i A" }}</dd>
      </div>
      <div>
        <dt class="text-[#65676b]">Reactions</dt>
        <dd>{{ post.reaction_count }}</dd>
      </div>
      <div>
        <dt class="text-[#65676b]">Comments</dt>
        <dd>{{ post.comment_count }}</dd>
      </div>
      <div>
        <dt class="text-[#65676b]">Reports</dt>
        <dd>{{ post.report_count }}</dd>
      </div>
    </dl>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 7: Run content management tests**

Run:

```powershell
python manage.py test dashboard.tests.DashboardViewTests.test_admin_can_view_post_list
```

Expected: PASS.

---

### Task 3: Analytics Dashboard

**Files:**
- Modify: `dashboard/views.py`
- Modify: `dashboard/urls.py`
- Create: `templates/dashboard/analytics.html`

- [ ] **Step 1: Add analytics URL and view**

In `dashboard/urls.py`:

```python
path("analytics/", views.analytics, name="analytics"),
```

In `dashboard/views.py`:

```python
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta

@login_required
def analytics(request):
    if not request.user.is_campus_admin:
        raise PermissionDenied("You don't have permission to view analytics")
    
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago = now - timedelta(days=7)
    
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
    
    top_posts = Post.objects.annotate(
        score=F("reactions__id") + F("comments__id")
    ).order_by("-score")[:5]
    
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
```

- [ ] **Step 2: Create analytics template**

Create `templates/dashboard/analytics.html`:

```django
{% extends "base.html" %}
{% block title %}Analytics - Admin Dashboard{% endblock %}
{% block content %}
<div class="animate-fade-in mb-5">
  <h1 class="text-2xl font-extrabold text-[#1c1e21] mb-1">Analytics</h1>
  <p class="text-[15px] text-[#65676b]">Campus engagement statistics</p>
</div>

<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-6">
  <div class="cv-stat-card">
    <div class="text-[13px] font-semibold text-[#65676b] uppercase">Total Users</div>
    <div class="text-3xl font-extrabold text-[#1c1e21]">{{ total_users }}</div>
    <div class="text-[13px] text-green-600">+{{ new_users_30d }} this month</div>
  </div>
  <div class="cv-stat-card">
    <div class="text-[13px] font-semibold text-[#65676b] uppercase">Total Posts</div>
    <div class="text-3xl font-extrabold text-[#1c1e21]">{{ total_posts }}</div>
    <div class="text-[13px] text-green-600">+{{ new_posts_30d }} this month</div>
  </div>
  <div class="cv-stat-card">
    <div class="text-[13px] font-semibold text-[#65676b] uppercase">Open Reports</div>
    <div class="text-3xl font-extrabold text-red-600">{{ open_reports }}</div>
  </div>
  <div class="cv-stat-card">
    <div class="text-[13px] font-semibold text-[#65676b] uppercase">Resolved Reports</div>
    <div class="text-3xl font-extrabold text-green-600">{{ resolved_reports }}</div>
  </div>
</div>

<div class="grid gap-6 lg:grid-cols-2">
  <div class="cv-card p-5">
    <h2 class="text-[17px] font-bold text-[#1c1e21] mb-4">Posts by Category</h2>
    <div class="space-y-3">
      {% for item in posts_by_category %}
      <div class="flex items-center gap-3">
        <span class="text-[14px] text-[#65676b] w-28">{{ item.category|title }}</span>
        <div class="flex-1 bg-[#e4e6eb] rounded-full h-2">
          <div class="bg-[#1877f2] rounded-full h-2" style="width: {% widthratio item.count total_posts 100 %}%"></div>
        </div>
        <span class="text-[14px] font-semibold w-8 text-right">{{ item.count }}</span>
      </div>
      {% endfor %}
    </div>
  </div>
  
  <div class="cv-card p-5">
    <h2 class="text-[17px] font-bold text-[#1c1e21] mb-4">Admin Status</h2>
    <div class="space-y-3">
      {% for item in posts_by_admin_status %}
      <div class="flex items-center gap-3">
        <span class="text-[14px] text-[#65676b] w-28">{{ item.admin_status|title }}</span>
        <div class="flex-1 bg-[#e4e6eb] rounded-full h-2">
          <div class="bg-[#42b72a] rounded-full h-2" style="width: {% widthratio item.count total_posts 100 %}%"></div>
        </div>
        <span class="text-[14px] font-semibold w-8 text-right">{{ item.count }}</span>
      </div>
      {% endfor %}
    </div>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 3: Run analytics test**

Run:

```powershell
python manage.py test dashboard.tests.DashboardViewTests.test_admin_can_view_analytics
```

Expected: PASS.

---

### Task 4: Settings View

**Files:**
- Modify: `dashboard/views.py`
- Modify: `dashboard/urls.py`
- Create: `templates/dashboard/settings.html`

- [ ] **Step 1: Add settings URL and view**

In `dashboard/urls.py`:

```python
path("settings/", views.settings, name="settings"),
```

In `dashboard/views.py`:

```python
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
```

- [ ] **Step 2: Create settings template**

Create `templates/dashboard/settings.html`:

```django
{% extends "base.html" %}
{% block title %}Settings - Admin Dashboard{% endblock %}
{% block content %}
<div class="animate-fade-in mb-5">
  <h1 class="text-2xl font-extrabold text-[#1c1e21] mb-1">System Settings</h1>
  <p class="text-[15px] text-[#65676b]">Manage roles and permissions</p>
</div>

<div class="cv-card p-5 mb-5">
  <h2 class="text-[17px] font-bold text-[#1c1e21] mb-4">Permissions</h2>
  <div class="overflow-x-auto">
    <table class="w-full">
      <thead class="bg-[#f0f2f5]">
        <tr>
          <th class="cv-th text-left">Code</th>
          <th class="cv-th text-left">Description</th>
        </tr>
      </thead>
      <tbody>
        {% for perm in permissions %}
        <tr class="border-t border-[#ddd]">
          <td class="cv-td font-mono text-sm">{{ perm.code }}</td>
          <td class="cv-td text-[14px]">{{ perm.description|default:"-" }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>

<div class="cv-card p-5">
  <h2 class="text-[17px] font-bold text-[#1c1e21] mb-4">Roles</h2>
  <div class="grid gap-4 sm:grid-cols-3">
    {% for role in roles %}
    <div class="border border-[#ddd] rounded-lg p-4">
      <h3 class="font-semibold text-[#050505] mb-2">{{ role.name|title }}</h3>
      <p class="text-[13px] text-[#65676b] mb-3">{{ role.permissions.count }} permissions</p>
      <div class="flex flex-wrap gap-1">
        {% for perm in role.permissions.all %}
        <span class="cv-chip text-[11px] bg-gray-100">{{ perm.code }}</span>
        {% endfor %}
      </div>
    </div>
    {% endfor %}
  </div>
</div>
{% endblock %}
```

- [ ] **Step 3: Run settings test**

Run:

```powershell
python manage.py test dashboard.tests.DashboardViewTests.test_admin_can_view_settings
```

Expected: PASS.

---

### Task 5: Update Sidebar Navigation

**Files:**
- Modify: `templates/partials/sidebar.html`

- [ ] **Step 1: Add admin section links**

In `templates/partials/sidebar.html`, replace the existing admin section:

```django
{% if user.is_campus_admin %}
<div class="my-4 border-t border-slate-200/60"></div>
<p class="px-4 py-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">Admin</p>
<a class="nav-item flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-slate-700 hover:text-[#2C3E94] transition-all cursor-pointer" href="{% url 'dashboard:index' %}">
  <span class="w-8 h-8 rounded-lg bg-purple-50 flex items-center justify-center text-purple-500">
    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
  </span>
  Dashboard
</a>
<a class="nav-item flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-slate-700 hover:text-[#2C3E94] transition-all cursor-pointer" href="{% url 'dashboard:users' %}">
  <span class="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center text-blue-500">
    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
  </span>
  Users
</a>
<a class="nav-item flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-slate-700 hover:text-[#2C3E94] transition-all cursor-pointer" href="{% url 'dashboard:posts' %}">
  <span class="w-8 h-8 rounded-lg bg-green-50 flex items-center justify-center text-green-500">
    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v12a2 2 0 01-2 2z"></path></svg>
  </span>
  Content
</a>
<a class="nav-item flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-slate-700 hover:text-[#2C3E94] transition-all cursor-pointer" href="{% url 'dashboard:analytics' %}">
  <span class="w-8 h-8 rounded-lg bg-yellow-50 flex items-center justify-center text-yellow-500">
    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
  </span>
  Analytics
</a>
<a class="nav-item flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-slate-700 hover:text-[#2C3E94] transition-all cursor-pointer" href="{% url 'dashboard:settings' %}">
  <span class="w-8 h-8 rounded-lg bg-gray-50 flex items-center justify-center text-gray-500">
    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
  </span>
  Settings
</a>
<a class="nav-item flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-slate-700 hover:text-[#2C3E94] transition-all cursor-pointer" href="{% url 'dashboard:moderation' %}">
  <span class="w-8 h-8 rounded-lg bg-red-50 flex items-center justify-center text-red-500">
    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
  </span>
  Moderation
</a>
{% endif %}
```

---

### Task 6: Tests and Verification

**Files:**
- Modify: `dashboard/tests.py`

- [ ] **Step 1: Add comprehensive admin tests**

Add test methods to `DashboardViewTests`:

```python
def test_admin_can_edit_user(self):
    user = get_user_model().objects.create_user(
        email="admin@test.com", username="admin", password="Pass123"
    )
    user.role = User.ROLE_ADMIN
    user.save()
    target = get_user_model().objects.create_user(
        email="target@test.com", username="target", password="Pass123"
    )
    self.client.login(email="admin@test.com", password="Pass123")

    response = self.client.post(
        reverse("dashboard:user_edit", args=[target.pk]),
        {"first_name": "Updated", "last_name": "Name", "role": User.ROLE_STUDENT, "department": "CS"},
    )

    self.assertEqual(response.status_code, 302)
    target.refresh_from_db()
    self.assertEqual(target.first_name, "Updated")

def test_admin_can_toggle_user(self):
    user = get_user_model().objects.create_user(
        email="admin@test.com", username="admin", password="Pass123"
    )
    user.role = User.ROLE_ADMIN
    user.save()
    target = get_user_model().objects.create_user(
        email="target@test.com", username="target", password="Pass123"
    )
    self.client.login(email="admin@test.com", password="Pass123")

    response = self.client.post(reverse("dashboard:user_toggle", args=[target.pk]))

    self.assertEqual(response.status_code, 302)
    target.refresh_from_db()
    self.assertFalse(target.is_active)

def test_non_admin_cannot_access_users(self):
    user = get_user_model().objects.create_user(
        email="student@test.com", username="student", password="Pass123"
    )
    self.client.login(email="student@test.com", password="Pass123")

    response = self.client.get(reverse("dashboard:users"))

    self.assertEqual(response.status_code, 403)

def test_admin_can_edit_post(self):
    admin = get_user_model().objects.create_user(
        email="admin@test.com", username="admin", password="Pass123"
    )
    admin.role = User.ROLE_ADMIN
    admin.save()
    post = Post.objects.create(
        author=admin, title="Test", description="Test", category=Post.CATEGORY_SUGGESTION
    )
    self.client.login(email="admin@test.com", password="Pass123")

    response = self.client.post(
        reverse("dashboard:post_edit", args=[post.pk]),
        {"title": "Updated", "description": "Test", "category": Post.CATEGORY_SUGGESTION,
         "status": Post.STATUS_APPROVED, "admin_status": Post.ADMIN_STATUS_PLANNED},
    )

    self.assertEqual(response.status_code, 302)
    post.refresh_from_db()
    self.assertEqual(post.title, "Updated")
    self.assertEqual(post.admin_status, Post.ADMIN_STATUS_PLANNED)
```

- [ ] **Step 2: Run all admin dashboard tests**

Run:

```powershell
python manage.py test dashboard.tests
```

Expected: PASS.

- [ ] **Step 3: Run full test suite**

Run:

```powershell
python manage.py test
```

Expected: PASS.

- [ ] **Step 4: Verify in browser**

Open `http://127.0.0.1:8000/dashboard/`. Log in as admin. Verify all 6 sections are accessible:
- Dashboard (overview)
- Users (list, create, edit, toggle)
- Content (list, edit, delete)
- Analytics (stats charts)
- Settings (roles, permissions)
- Moderation (existing reports)

---

## Self-Review

- Spec coverage: User management (list, create, edit, delete, toggle), Content management (list, edit, delete, status), Analytics dashboard, Settings view, and sidebar navigation are covered.
- Placeholder scan: no TBD/TODO placeholders.
- Type consistency: route names use `dashboard:users`, `dashboard:user_edit`, `dashboard:posts`, `dashboard:post_edit`, `dashboard:analytics`, `dashboard:settings` patterns.
- Permissions: admin routes check `is_campus_admin` or specific permissions.