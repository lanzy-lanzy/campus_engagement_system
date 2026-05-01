# Phase 2 Campus Engagement - Enhanced Features

## Goal
Add richer search, tag expansion, notification polling, and PostgreSQL environment configuration.

## Scope

### Task 1: Richer Search
- Add full-text search for posts
- Search by title, description, category
- Search templates

### Task 2: Tag Expansion
- Add tags to posts
- Tag filtering
- Popular tags sidebar

### Task 3: Notification Polling
- HTMX polling for new posts
- Notification count badge
- Real-time updates

### Task 4: PostgreSQL Configuration
- Production-ready settings
- Environment-based config
- Database backup scripts

---

## Implementation Steps

### Task 1: Search Features
- [ ] Modify Post model to add search_vector
- [ ] Add search view
- [ ] Add search template
- [ ] Add search URL

### Task 2: Tags
- [ ] Add Tag model
- [ ] Many-to-many for posts
- [ ] Tag filtering
- [ ] Popular tags

### Task 3: Notifications
- [ ] Add unread count to user
- [ ] HTMX polling endpoint
- [ ] Update navbar with badge

### Task 4: PostgreSQL
- [ ] Add psycopg2 dependency
- [ ] settings.py for production
- [ ] docker-compose.yml (optional)
- [ ] .env.example