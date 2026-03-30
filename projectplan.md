# Beach App - Project Plan

## Overview
A responsive web app for organizing an annual family beach vacation at Carolina Beach, NC. ~26 users, two roles (admin/user), accessible from desktop, phone, and tablet.

## Tech Stack
- **Backend:** Python 3 + Flask
- **Frontend:** Jinja2 templates + Bootstrap 5 (responsive, no build step)
- **Database:** SQLite (local dev), migrateable to PostgreSQL for production
- **Auth:** Flask-Login (session-based, session ends on browser close)
- **Email:** Flask-Mail (password reset, birthday notifications, admin broadcasts)
- **ORM:** SQLAlchemy
- **Testing:** pytest + Flask test client

## Data Model
- **User** — id, name, email, password_hash, birthday, role (admin|user)
- **BeachWeek** — id, year, start_date, end_date
- **RoomAssignment** — id, beach_week_id, room_name, user_ids
- **MenuItem** — id, beach_week_id, day, meal_type (breakfast|lunch|dinner), description
- **DinnerRSVP** — id, menu_item_id, user_id, status (attending|not_here)
- **Chore** — id, beach_week_id, description, assigned_user_id, day
- **Picture** — id, beach_week_id, uploaded_by, file_path, caption, created_at
- **BlogPost** — id, beach_week_id, author_id, title, content, created_at
- **BlogPostPicture** — id, blog_post_id, picture_id

## Pages / Routes

### Auth
- Login page (main landing page)
- Password reset request
- Password reset confirm

### User Views
- **Dashboard/Main** — countdown to next beach week; blog posts; switches to dinner menu when countdown hits zero
- **Left Sidebar** — list of years, each expandable to: Room Assignments, Menu, Chore List, Pictures
- **Room Assignments** — read-only view of room assignments for a given year
- **Menu** — breakfast/lunch/dinner for each day; dinner has "Not here" toggle
- **Chore List** — read-only view of chores for the week
- **Pictures** — gallery view; pictures from blog posts also appear here

### Admin Views (extends user views)
- **Manage Beach Week** — add/edit beach week dates (auto-creates year in sidebar)
- **Edit Room Assignments** — assign users to rooms
- **Edit Menu** — add/edit meals for each day
- **Edit Chore List** — add/edit/assign chores
- **Send Email** — compose and send email to all users

## Todo List

### Phase 1: Project Setup
- [x] Initialize project structure (folders, requirements.txt, .gitignore)
- [x] Set up Flask app with config (dev/prod/testing)
- [x] Set up SQLAlchemy models and database
- [x] Set up pytest with test fixtures (test client, test database, test users)

### Phase 2: Authentication
- [x] Login page (landing page)
- [x] Flask-Login session management (session expires on browser close)
- [x] Password reset via email
- [x] User registration (admin-only: admin creates users)
- [x] Unit tests: login/logout, session expiry, password reset, role-based access

### Phase 3: Layout & Navigation
- [x] Base template with responsive Bootstrap layout
- [x] Left sidebar with year list and sub-pages
- [x] Dashboard/main page with countdown timer

### Phase 4: Core User Features
- [x] Room assignments view (read-only)
- [x] Menu view with breakfast/lunch/dinner per day
- [x] Dinner "Not here" toggle (RSVP)
- [x] Chore list view (read-only)
- [x] Pictures gallery
- [x] Blog posts with picture support
- [x] Dashboard switches to dinner menu when countdown reaches zero
- [x] Unit tests: room assignments, menu/RSVP, chores, pictures, blog posts, countdown logic
- [x] Push to git

### Phase 5: Admin Features
- [x] Add/edit beach week (creates year entry in sidebar)
- [x] Edit room assignments
- [x] Edit menu
- [x] Edit chore list
- [x] Send email to all users
- [x] Unit tests: admin CRUD operations, email send, non-admin access denied
- [x] Push to git

### Phase 6: Email & Notifications
- [x] Birthday email notifications (scheduled daily check)
- [x] Password reset emails
- [x] Admin broadcast emails
- [x] Unit tests: birthday check logic, email sending (mocked SMTP)
- [x] Push to git

### Phase 7: Polish & Deployment Prep
- [x] Responsive testing (phone, tablet, desktop)
- [x] Error handling and flash messages
- [x] Production config (secret key, email server, database URL)
- [x] Deployment documentation
- [x] Full test suite passing with coverage report
- [x] Push to git

### Nice to Have (Future)
- [ ] MFA (multi-factor authentication)

---

## Review

### Summary
All 7 phases complete. The Beach App is a fully functional responsive web application for organizing the annual Moore family beach vacation at Carolina Beach, NC.

### What was built
- **Auth system** — email login, password reset via email tokens, session expires on browser close, admin-only user management (add/edit/delete)
- **Dashboard** — live countdown timer to next beach week, blog feed, auto-switches to menu link during beach week
- **Sidebar navigation** — collapsible year list with sub-pages for rooms, menu, chores, pictures; collapses to hamburger on mobile
- **Room assignments** — multi-person per room, grouped display
- **Menu** — pre-populated weekly schedule (day 1: dinner only, last day: none, rest: all meals), multi-user assignment for cooks, dinner RSVP toggle (Attending/Not Here)
- **Chore list** — multi-user assignment per chore
- **Pictures** — per-year gallery with upload
- **Blog** — posts with photo attachments, visible on dashboard
- **Admin panel** — full CRUD for beach weeks, rooms, menu, chores, users; broadcast email to all users
- **Email** — password reset, admin broadcasts, daily birthday check via CLI command (`flask check-birthdays`)
- **Dark/light mode** — toggle with localStorage persistence
- **Error pages** — custom 404 and 500 pages
- **Production ready** — secure session cookies, `.env.example`, `DEPLOY.md` with Gunicorn/Nginx/HTTPS/cron setup

### Test coverage
- **60 tests passing**
- **91% code coverage**
- Tests cover: auth flows, password reset, role-based access, all CRUD operations, RSVP toggle, blog, birthday emails, admin email broadcast

### Tech stack
- Python 3 / Flask / SQLAlchemy / SQLite (dev) / PostgreSQL (prod)
- Bootstrap 5 with dark mode / Jinja2 templates
- Flask-Login / Flask-Mail / itsdangerous
- pytest with Flask test client

### Files created
- 20+ templates (Bootstrap 5 responsive)
- 5 test files
- 9 database models + 3 join tables
- 3 route blueprints (auth, main, admin)
- Deployment guide and environment template
