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
- [ ] Login page (landing page)
- [ ] Flask-Login session management (session expires on browser close)
- [ ] Password reset via email
- [ ] User registration (admin-only: admin creates users)
- [ ] Unit tests: login/logout, session expiry, password reset, role-based access

### Phase 3: Layout & Navigation
- [ ] Base template with responsive Bootstrap layout
- [ ] Left sidebar with year list and sub-pages
- [ ] Dashboard/main page with countdown timer

### Phase 4: Core User Features
- [ ] Room assignments view (read-only)
- [ ] Menu view with breakfast/lunch/dinner per day
- [ ] Dinner "Not here" toggle (RSVP)
- [ ] Chore list view (read-only)
- [ ] Pictures gallery
- [ ] Blog posts with picture support
- [ ] Dashboard switches to dinner menu when countdown reaches zero
- [ ] Unit tests: room assignments, menu/RSVP, chores, pictures, blog posts, countdown logic

### Phase 5: Admin Features
- [ ] Add/edit beach week (creates year entry in sidebar)
- [ ] Edit room assignments
- [ ] Edit menu
- [ ] Edit chore list
- [ ] Send email to all users
- [ ] Unit tests: admin CRUD operations, email send, non-admin access denied

### Phase 6: Email & Notifications
- [ ] Birthday email notifications (scheduled daily check)
- [ ] Password reset emails
- [ ] Admin broadcast emails
- [ ] Unit tests: birthday check logic, email sending (mocked SMTP)

### Phase 7: Polish & Deployment Prep
- [ ] Responsive testing (phone, tablet, desktop)
- [ ] Error handling and flash messages
- [ ] Production config (secret key, email server, database URL)
- [ ] Deployment documentation
- [ ] Full test suite passing with coverage report

### Nice to Have (Future)
- [ ] MFA (multi-factor authentication)

---

## Review
_To be filled in after implementation._
