# Admin Dashboard Design Specification

> **For implementation reference:** This spec defines the UI/UX design for the admin dashboard features.

## Overview

| Component | Detail |
|-----------|--------|
| **Feature** | Admin Dashboard with User Management, Content Management, Analytics, and Settings |
| **Target Users** | Admins with `is_campus_admin=True` (role=admin, is_staff, or is_superuser) |
| **URLs** | `/dashboard/`, `/dashboard/users/`, `/dashboard/posts/`, `/dashboard/analytics/`, `/dashboard/settings/` |
| **Tech Stack** | Django templates, HTMX, Alpine.js, TailwindCSS |

---

## Layout Structure

### Base Layout
- Same as existing `base.html` layout
- Sidebar navigation (left) + Main content (right)
- No changes to header/footer

### Responsive Breakpoints
- Mobile: `< 640px` - stacked cards, hamburger menu
- Tablet: `640px - 1024px` - 2-column grids
- Desktop: `> 1024px` - full sidebar + 3-column grids

---

## UI Components

### 1. Dashboard Overview (`/dashboard/`)

Existing implementation with stats cards:
- Total Posts count
- Total Users count
- Open Reports count
- Quick actions: Review Reports, View Feed

### 2. User Management (`/dashboard/users/`)

**Layout:**
- Header: "User Management" title + "Add User" button (top-right)
- Filter bar: Search input + Role dropdown + Status dropdown + Filter/Clear buttons
- Table: User list with pagination

**Table Columns:**
| Column | Content |
|-------|--------|
| User | Avatar placeholder + Name + Email |
| Role | Role chip (admin=purple, moderator=blue, student=gray) |
| Department | Text or "-" |
| Status | Active/Inactive chip (green/red) |
| Joined | Date |
| Actions | Edit link + Activate/Deactivate button |

**User Edit Form:**
- Email input (readonly for existing)
- Username input (readonly for existing)
- Password input (new users only)
- First Name + Last Name (grid)
- Role dropdown
- Department
- Student ID
- Bio textarea
- Save + Cancel buttons

### 3. Content Management (`/dashboard/posts/`)

**Layout:**
- Header: "Content Management" title
- Filter bar: Search + Category + Status + Admin Status dropdowns
- Table: Posts list

**Table Columns:**
| Column | Content |
|-------|--------|
| Title | Truncated title (max 300px) |
| Author | Username |
| Category | Category chip |
| Status | Status chip (approved=green, pending=yellow, removed=red) |
| Admin Status | Admin status chip |
| Created | Date |
| Actions | Edit + Delete buttons |

**Post Edit Form:**
- Title input
- Description textarea
- Category dropdown
- Status dropdown
- Admin Status dropdown (none, under_review, planned, in_progress, completed)
- Post info sidebar (author, created, reactions, comments, reports)

### 4. Analytics (`/dashboard/analytics/`)

**Stats Cards (4-column):**
- Total Users + new users this month
- Total Posts + new posts this month
- Open Reports (red)
- Resolved Reports (green)

**Charts:**
- Posts by category (horizontal bar chart)
- Admin status distribution (horizontal bar chart)

### 5. Settings (`/dashboard/settings/`)

**Permissions Table:**
- Code column (monospace)
- Description column

**Roles Grid:**
- Role card with name, permission count, permission chips

---

## Component Styles

### Card Component (`.cv-card`)
```css
background: white;
border-radius: 8px;
box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
```

### Stat Card (`.cv-stat-card`)
```css
.cv-card;
padding: 20px;
```

### Chip Component (`.cv-chip`)
```css
display: inline-block;
padding: 4px 8px;
border-radius: 6px;
font-size: 12px;
font-weight: 500;
```

**Color Variants:**
| Chip | Background | Text |
|------|-----------|------|
| Admin | `bg-purple-100` | `text-purple-700` |
| Moderator | `bg-blue-100` | `text-blue-700` |
| Student | `bg-gray-100` | `text-gray-700` |
| Active | `bg-green-100` | `text-green-700` |
| Inactive | `bg-red-100` | `text-red-700` |
| Approved | `bg-green-100` | `text-green-700` |
| Pending | `bg-yellow-100` | `text-yellow-700` |
| Removed | `bg-red-100` | `text-red-700` |

### Table Components
```css
.cv-th {
  padding: 12px 16px;
  font-size: 13px;
  font-weight: 600;
  color: #65676b;
}
.cv-td {
  padding: 12px 16px;
  font-size: 14px;
}
```

### Form Components
```css
.cv-input {
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 10px 12px;
  font-size: 14px;
  transition: border-color 0.15s;
}
.cv-input:focus {
  border-color: #1877f2;
  outline: none;
}
.cv-select {
  @apply .cv-input;
  cursor: pointer;
}
.cv-textarea {
  @apply .cv-input;
  resize: vertical;
}
```

### Buttons
Reuse existing `.btn-fb` classes from base template:
- `.btn-primary-fb` - Primary action (blue)
- `.btn-secondary-fb` - Secondary action (gray outline)

---

## Navigation

### Sidebar Admin Section

Location: `templates/partials/sidebar.html`

```html
{% if user.is_campus_admin %}
<div class="my-4 border-t border-slate-200/60"></div>
<p class="px-4 py-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">Admin</p>
<!-- Dashboard -->
<!-- Users -->
<!-- Content -->
<!-- Analytics -->
<!-- Settings -->
<!-- Moderation -->
{% endif %}
```

**Icon Colors:**
| Section | Background | Icon Color |
|---------|------------|-----------|
| Dashboard | `bg-purple-50` | `text-purple-500` |
| Users | `bg-blue-50` | `text-blue-500` |
| Content | `bg-green-50` | `text-green-500` |
| Analytics | `bg-yellow-50` | `text-yellow-500` |
| Settings | `bg-gray-50` | `text-gray-500` |
| Moderation | `bg-red-50` | `text-red-500` |

---

## Animations

### Fade In Animation
```css
.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
```

### Stagger Delays (existing)
```css
.stagger-1 { animation-delay: 0.1s; }
.stagger-2 { animation-delay: 0.2s; }
.stagger-3 { animation-delay: 0.3s; }
```

---

## Permissions

### Route Access
| Route | Permission Check |
|-------|------------------|
| `/dashboard/` | `is_campus_admin` |
| `/dashboard/users/` | `is_campus_admin` |
| `/dashboard/users/new/` | `is_campus_admin` |
| `/dashboard/users/<id>/edit/` | `is_campus_admin` |
| `/dashboard/users/<id>/delete/` | `is_campus_admin` |
| `/dashboard/users/<id>/toggle/` | `is_campus_admin` |
| `/dashboard/posts/` | `is_campus_admin` |
| `/dashboard/posts/<id>/edit/` | `is_campus_admin` |
| `/dashboard/posts/<id>/delete/` | `is_campus_admin` |
| `/dashboard/analytics/` | `is_campus_admin` |
| `/dashboard/settings/` | `is_campus_admin` |
| `/dashboard/moderation/` | `is_campus_admin` (existing) |

### Permission Checks
```python
if not request.user.is_campus_admin:
    raise PermissionDenied("You don't have permission to manage users")
```

---

## HTMX Patterns

### Table Row Actions
```html
<!-- Inline edit in modal -->
<button hx-get="{% url 'dashboard:user_edit' user.pk %}" hx-target="#modal-root">
<!-- Delete with confirmation -->
<form hx-post="{% url 'dashboard:user_delete' user.pk %}" hx-target="#user-table">
```

### Form Submissions
```html
<form hx-post="{% url 'dashboard:user_create' %}" hx-target="#user-list" hx-swap="outerHTML">
```

### Filter Updates
```html
<select name="role" hx-get="{% url 'dashboard:users' %}" hx-target="#user-table" hx-trigger="change">
```

---

## Accessibility

### ARIA Labels
```html
<!-- Filter buttons -->
<button aria-label="Filter users">Filter</button>
<!-- Action buttons -->
<button aria-label="Edit user {{ user.username }}">Edit</button>
<!-- Toggle buttons -->
<button aria-label="Toggle {{ user.username }} active status">
```

### Keyboard Navigation
- Tab order: filters → table → actions
- Enter to submit forms
- Escape to cancel modals

### Screen Reader Support
- Use semantic `<th>` headers
- Add `aria-label` to icon-only buttons
- Use proper table structure (`<thead>`, `<tbody>`)

---

## Error Handling

### Permission Denied
```python
raise PermissionDenied("You don't have permission to manage users")
```

Returns 403 Forbidden.

### Form Errors
- Display inline error messages
- Use Django's form validation messages
- Show field-specific errors

### Success Messages
```python
messages.success(request, f"User {username} created successfully")
messages.error(request, "Email already exists")
```

---

## Responsive Behavior

### Mobile (< 640px)
- Hide sidebar, show hamburger menu
- Stack filter bar vertically
- Stack table cells vertically
- Full-width buttons

### Tablet (640-1024px)
- 2-column grids
- Horizontal scroll for tables

### Desktop (> 1024px)
- Full sidebar visible
- 3-4 column grids
- Full-width tables