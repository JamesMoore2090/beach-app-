from datetime import date, timedelta
from app.models import BeachWeek, MenuItem, DinnerRSVP, RoomAssignment, Chore, BlogPost, Picture


def login(client, email, password):
    client.post('/login', data={'email': email, 'password': password})


def make_beach_week(db, year=2026, offset_days=30):
    start = date.today() + timedelta(days=offset_days)
    bw = BeachWeek(year=year, start_date=start, end_date=start + timedelta(days=7))
    db.session.add(bw)
    db.session.commit()
    return bw


# Dashboard / Countdown

def test_dashboard_shows_countdown(client, regular_user, db):
    make_beach_week(db, 2026, offset_days=30)
    login(client, 'user@test.com', 'userpass')
    response = client.get('/dashboard')
    assert b'Countdown to Beach Week 2026' in response.data


def test_dashboard_shows_current_week_menu_link(client, regular_user, db):
    today = date.today()
    bw = BeachWeek(year=2026, start_date=today - timedelta(days=1), end_date=today + timedelta(days=5))
    db.session.add(bw)
    db.session.commit()
    login(client, 'user@test.com', 'userpass')
    response = client.get('/dashboard')
    assert b'happening now' in response.data
    assert b'Menu' in response.data


def test_dashboard_no_beach_week(client, regular_user, db):
    login(client, 'user@test.com', 'userpass')
    response = client.get('/dashboard')
    assert b'No upcoming beach week' in response.data


# Room Assignments

def test_room_assignments_page(client, regular_user, db):
    bw = make_beach_week(db)
    ra = RoomAssignment(beach_week_id=bw.id, room_name='Ocean Room', user_id=regular_user.id)
    db.session.add(ra)
    db.session.commit()
    login(client, 'user@test.com', 'userpass')
    response = client.get(f'/year/{bw.year}/rooms')
    assert b'Ocean Room' in response.data
    assert b'User' in response.data


def test_room_assignments_empty(client, regular_user, db):
    bw = make_beach_week(db)
    login(client, 'user@test.com', 'userpass')
    response = client.get(f'/year/{bw.year}/rooms')
    assert b'No room assignments yet' in response.data


# Menu and RSVP

def test_menu_page(client, regular_user, db):
    bw = make_beach_week(db)
    item = MenuItem(beach_week_id=bw.id, day=bw.start_date, meal_type='dinner', description='Fish tacos')
    db.session.add(item)
    db.session.commit()
    login(client, 'user@test.com', 'userpass')
    response = client.get(f'/year/{bw.year}/menu')
    assert b'Fish tacos' in response.data
    assert b'Attending' in response.data


def test_rsvp_toggle_to_not_here(client, regular_user, db):
    bw = make_beach_week(db)
    item = MenuItem(beach_week_id=bw.id, day=bw.start_date, meal_type='dinner', description='Shrimp')
    db.session.add(item)
    db.session.commit()
    login(client, 'user@test.com', 'userpass')
    response = client.post(f'/rsvp/{item.id}', follow_redirects=True)
    rsvp = DinnerRSVP.query.filter_by(menu_item_id=item.id, user_id=regular_user.id).first()
    assert rsvp.status == 'not_here'


def test_rsvp_toggle_back_to_attending(client, regular_user, db):
    bw = make_beach_week(db)
    item = MenuItem(beach_week_id=bw.id, day=bw.start_date, meal_type='dinner', description='Steak')
    db.session.add(item)
    db.session.commit()
    rsvp = DinnerRSVP(menu_item_id=item.id, user_id=regular_user.id, status='not_here')
    db.session.add(rsvp)
    db.session.commit()
    login(client, 'user@test.com', 'userpass')
    client.post(f'/rsvp/{item.id}', follow_redirects=True)
    db.session.refresh(rsvp)
    assert rsvp.status == 'attending'


def test_rsvp_only_dinner(client, regular_user, db):
    bw = make_beach_week(db)
    item = MenuItem(beach_week_id=bw.id, day=bw.start_date, meal_type='breakfast', description='Eggs')
    db.session.add(item)
    db.session.commit()
    login(client, 'user@test.com', 'userpass')
    response = client.post(f'/rsvp/{item.id}', follow_redirects=True)
    assert b'only available for dinner' in response.data


# Chores

def test_chores_page(client, regular_user, db):
    bw = make_beach_week(db)
    chore = Chore(beach_week_id=bw.id, description='Sweep porch', day=bw.start_date)
    chore.assigned_users.append(regular_user)
    db.session.add(chore)
    db.session.commit()
    login(client, 'user@test.com', 'userpass')
    response = client.get(f'/year/{bw.year}/chores')
    assert b'Sweep porch' in response.data


# Pictures

def test_pictures_page_empty(client, regular_user, db):
    bw = make_beach_week(db)
    login(client, 'user@test.com', 'userpass')
    response = client.get(f'/year/{bw.year}/pictures')
    assert b'No pictures yet' in response.data


# Blog

def test_blog_create_and_list(client, regular_user, db):
    login(client, 'user@test.com', 'userpass')
    response = client.post('/blog/new', data={
        'title': 'Great memories',
        'content': 'What a week!',
    }, follow_redirects=True)
    assert b'Post created' in response.data
    assert b'Great memories' in response.data


def test_blog_detail(client, regular_user, db):
    login(client, 'user@test.com', 'userpass')
    post = BlogPost(title='Test Post', content='Hello world', author_id=regular_user.id)
    db.session.add(post)
    db.session.commit()
    response = client.get(f'/blog/{post.id}')
    assert b'Test Post' in response.data
    assert b'Hello world' in response.data


def test_blog_shows_on_dashboard(client, regular_user, db):
    login(client, 'user@test.com', 'userpass')
    post = BlogPost(title='Dashboard Post', content='Visible on main page', author_id=regular_user.id)
    db.session.add(post)
    db.session.commit()
    response = client.get('/dashboard')
    assert b'Dashboard Post' in response.data
