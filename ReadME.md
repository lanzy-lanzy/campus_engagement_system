You are a senior full-stack Django developer, UI/UX designer, and system architect.

Build a COMPLETE, PRODUCTION-READY web system based on the following specifications:

========================================
📌 PROJECT INFORMATION
======================

System Title: A Web-Based Student Feedback and Engagement System

Purpose:
A platform where students can:

* Share ideas to improve the school
* Post concerns/issues inside campus
* Interact through comments, likes, and reactions (heart)
* Engage in a collaborative and transparent environment

========================================
🧱 TECH STACK (STRICTLY FOLLOW)
===============================

Backend:

* Django (latest version)
* Django ORM
* SQLite (dev) / PostgreSQL (ready)

Frontend:

* Django Templates ONLY (NO React/Vue)
* Tailwind CSS (CDN)
* HTMX (for dynamic partial updates)
* Alpine.js (for interactivity)

Other:

* Mobile-first responsive design
* Clean, modern UI
* Sidebar dashboard (collapsible on mobile)

========================================
👥 USER ROLES
=============

1. Admin
2. Student (User)

========================================
🔐 AUTHENTICATION
=================

* Login / Register (Student)
* Role-based redirection
* Django auth system
* Optional: email verification ready

========================================
📦 CORE FEATURES
================

🔹 STUDENT SIDE

* Create Post (Idea / Concern)

  * Title
  * Description
  * Category (Suggestion, Complaint, Improvement, Event Idea)
  * Optional Image Upload

* Feed / Timeline

  * Display all posts (like social media)
  * Sort: Latest / Most Liked / Trending

* Interactions

  * Like 👍
  * Heart ❤️
  * Comment 💬 (threaded)

* Post Actions

  * Edit/Delete own posts
  * Report inappropriate posts

* Profile Page

  * User posts
  * Activity summary

---

🔹 ADMIN SIDE

* Dashboard

  * Total Posts
  * Most Active Students
  * Most Reported Issues

* Manage Posts

  * Approve / Remove posts
  * Moderate comments

* Reports System

  * View flagged content

* Analytics

  * Most liked posts
  * Engagement metrics

========================================
🗂️ SYSTEM ARCHITECTURE
=======================

Create Django apps:

* accounts
* posts
* interactions
* dashboard

Include:

* models.py
* views.py (HTMX-based views)
* urls.py
* forms.py

========================================
🧩 DATABASE DESIGN
==================

Models should include:

User (extend AbstractUser)
Post
Comment
Reaction (Like/Heart)
Report

Include relationships and timestamps.

========================================
⚡ HTMX FEATURES (IMPORTANT)
===========================

* Like/Heart without page reload
* Add comment dynamically
* Load more posts (infinite scroll or pagination)
* Delete/update post without reload

========================================
🎨 UI/UX REQUIREMENTS
=====================

* Mobile-first design
* Sidebar navigation (collapsible)
* Clean cards for posts
* Reaction buttons with counters
* Modal forms (create/edit post)

Color Theme:

* Primary: Royal Blue (#2C3E94)
* Accent: Sky Blue (#5DADE2)
* Success: Mint Green (#A9DFBF)
* Background: Soft White (#FDFEFE)

========================================
📊 BONUS FEATURES (IF POSSIBLE)
===============================

* Trending algorithm (based on likes + comments)
* Notification system (HTMX polling)
* Search and filter posts
* Tagging system (#ideas, #issues)

========================================
📘 OUTPUT REQUIREMENTS
======================

Generate:

1. Full Django Project Structure
2. Models (complete)
3. Views (function-based or class-based)
4. Templates (Tailwind + HTMX + Alpine)
5. URL routing
6. Forms
7. Sample UI design
8. README.md (setup guide)
9. Flow explanation

DO NOT summarize. Provide COMPLETE WORKING CODE.

Ensure:
✔ Clean architecture
✔ Modular design
✔ Production-ready structure
✔ Visually appealing UI

========================================
⚠️ IMPORTANT RULES
==================

* Do NOT use React or external JS frameworks
* Use HTMX for dynamic behavior
* Use Alpine.js only for small UI interactions
* Follow Django best practices

========================================
END OF INSTRUCTIONS
===================
