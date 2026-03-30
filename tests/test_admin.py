from datetime import date
from app.models import User, BeachWeek, RoomAssignment, MenuItem, Chore


def login(client, email, password):
    client.post('/login', data={'email': email, 'password': password})


# --- Access control ---

def test_non_admin_blocked(client, regular_user):
    login(client, 'user@test.com', 'userpass')
    response = client.get('/admin/', follow_redirects=True)
    assert b'Admin access required' in response.data


def test_admin_can_access(client, admin_user):
    login(client, 'admin@test.com', 'adminpass')
    response = client.get('/admin/')
    assert response.status_code == 200
    assert b'Admin' in response.data


# --- Beach Week CRUD ---

def test_add_beach_week(client, admin_user, db):
    login(client, 'admin@test.com', 'adminpass')
    response = client.post('/admin/beach-week/add', data={
        'year': '2027',
        'start_date': '2027-07-10',
        'end_date': '2027-07-17',
    }, follow_redirects=True)
    assert b'Beach week 2027 created' in response.data
    assert BeachWeek.query.filter_by(year=2027).first() is not None


def test_add_duplicate_beach_week(client, admin_user, db):
    bw = BeachWeek(year=2026, start_date=date(2026, 7, 11), end_date=date(2026, 7, 18))
    db.session.add(bw)
    db.session.commit()
    login(client, 'admin@test.com', 'adminpass')
    response = client.post('/admin/beach-week/add', data={
        'year': '2026',
        'start_date': '2026-07-11',
        'end_date': '2026-07-18',
    }, follow_redirects=True)
    assert b'already exists' in response.data


def test_edit_beach_week(client, admin_user, db):
    bw = BeachWeek(year=2026, start_date=date(2026, 7, 11), end_date=date(2026, 7, 18))
    db.session.add(bw)
    db.session.commit()
    login(client, 'admin@test.com', 'adminpass')
    response = client.post('/admin/beach-week/2026/edit', data={
        'start_date': '2026-07-12',
        'end_date': '2026-07-19',
    }, follow_redirects=True)
    assert b'updated' in response.data
    db.session.refresh(bw)
    assert bw.start_date == date(2026, 7, 12)


# --- Room Assignments ---

def test_add_room_assignment(client, admin_user, regular_user, db):
    bw = BeachWeek(year=2026, start_date=date(2026, 7, 11), end_date=date(2026, 7, 18))
    db.session.add(bw)
    db.session.commit()
    login(client, 'admin@test.com', 'adminpass')
    response = client.post(f'/admin/beach-week/2026/rooms', data={
        'room_name': 'Ocean Suite',
        'user_id': str(regular_user.id),
    }, follow_redirects=True)
    assert b'Room assignment added' in response.data
    assert RoomAssignment.query.filter_by(room_name='Ocean Suite').first() is not None


def test_delete_room_assignment(client, admin_user, regular_user, db):
    bw = BeachWeek(year=2026, start_date=date(2026, 7, 11), end_date=date(2026, 7, 18))
    db.session.add(bw)
    db.session.commit()
    ra = RoomAssignment(beach_week_id=bw.id, room_name='Test Room', user_id=regular_user.id)
    db.session.add(ra)
    db.session.commit()
    login(client, 'admin@test.com', 'adminpass')
    response = client.post(f'/admin/room-assignment/{ra.id}/delete', follow_redirects=True)
    assert b'removed' in response.data
    assert db.session.get(RoomAssignment, ra.id) is None


def test_multiple_people_per_room(client, admin_user, regular_user, db):
    bw = BeachWeek(year=2026, start_date=date(2026, 7, 11), end_date=date(2026, 7, 18))
    db.session.add(bw)
    db.session.commit()
    login(client, 'admin@test.com', 'adminpass')
    # Add admin to same room
    client.post('/admin/beach-week/2026/rooms', data={
        'room_name': 'Master Suite',
        'user_id': str(admin_user.id),
    })
    # Add regular user to same room
    client.post('/admin/beach-week/2026/rooms', data={
        'room_name': 'Master Suite',
        'user_id': str(regular_user.id),
    })
    assignments = RoomAssignment.query.filter_by(room_name='Master Suite').all()
    assert len(assignments) == 2


# --- Menu ---

def test_add_menu_item(client, admin_user, db):
    bw = BeachWeek(year=2026, start_date=date(2026, 7, 11), end_date=date(2026, 7, 18))
    db.session.add(bw)
    db.session.commit()
    login(client, 'admin@test.com', 'adminpass')
    response = client.post('/admin/beach-week/2026/menu', data={
        'day': '2026-07-12',
        'meal_type': 'dinner',
        'description': 'Lobster',
    }, follow_redirects=True)
    assert b'Menu item added' in response.data
    assert MenuItem.query.filter_by(description='Lobster').first() is not None


def test_add_menu_item_with_assigned_users(client, admin_user, regular_user, db):
    bw = BeachWeek(year=2026, start_date=date(2026, 7, 11), end_date=date(2026, 7, 18))
    db.session.add(bw)
    db.session.commit()
    login(client, 'admin@test.com', 'adminpass')
    response = client.post('/admin/beach-week/2026/menu', data={
        'day': '2026-07-12',
        'meal_type': 'dinner',
        'description': 'Shrimp Boil',
        'assigned_users': [str(admin_user.id), str(regular_user.id)],
    }, follow_redirects=True)
    assert b'Menu item added' in response.data
    item = MenuItem.query.filter_by(description='Shrimp Boil').first()
    assert len(item.assigned_users) == 2


def test_delete_menu_item(client, admin_user, db):
    bw = BeachWeek(year=2026, start_date=date(2026, 7, 11), end_date=date(2026, 7, 18))
    db.session.add(bw)
    db.session.commit()
    item = MenuItem(beach_week_id=bw.id, day=date(2026, 7, 12), meal_type='lunch', description='Sandwiches')
    db.session.add(item)
    db.session.commit()
    login(client, 'admin@test.com', 'adminpass')
    response = client.post(f'/admin/menu-item/{item.id}/delete', follow_redirects=True)
    assert b'removed' in response.data


# --- Chores ---

def test_add_chore(client, admin_user, regular_user, db):
    bw = BeachWeek(year=2026, start_date=date(2026, 7, 11), end_date=date(2026, 7, 18))
    db.session.add(bw)
    db.session.commit()
    login(client, 'admin@test.com', 'adminpass')
    response = client.post('/admin/beach-week/2026/chores', data={
        'description': 'Mop floors',
        'assigned_user_id': str(regular_user.id),
        'day': '2026-07-13',
    }, follow_redirects=True)
    assert b'Chore added' in response.data
    assert Chore.query.filter_by(description='Mop floors').first() is not None


def test_delete_chore(client, admin_user, db):
    bw = BeachWeek(year=2026, start_date=date(2026, 7, 11), end_date=date(2026, 7, 18))
    db.session.add(bw)
    db.session.commit()
    chore = Chore(beach_week_id=bw.id, description='Take out trash')
    db.session.add(chore)
    db.session.commit()
    login(client, 'admin@test.com', 'adminpass')
    response = client.post(f'/admin/chore/{chore.id}/delete', follow_redirects=True)
    assert b'removed' in response.data


# --- Email ---

def test_send_email(client, admin_user, regular_user, app):
    login(client, 'admin@test.com', 'adminpass')
    with app.extensions['mail'].record_messages() as outbox:
        response = client.post('/admin/email', data={
            'subject': 'Beach Update',
            'body': 'See you soon!',
        }, follow_redirects=True)
        assert b'Email sent' in response.data
        assert len(outbox) == 1
        assert 'Beach Update' in outbox[0].subject


# --- Users ---

def test_edit_user(client, admin_user, regular_user, db):
    login(client, 'admin@test.com', 'adminpass')
    response = client.post(f'/admin/users/{regular_user.id}/edit', data={
        'name': 'Updated Name',
        'email': 'updated@test.com',
        'role': 'user',
        'birthday': '1992-08-20',
    }, follow_redirects=True)
    assert b'Updated Name' in response.data
    assert b'updated' in response.data
    db.session.refresh(regular_user)
    assert regular_user.name == 'Updated Name'
    assert regular_user.email == 'updated@test.com'


def test_edit_user_password(client, admin_user, regular_user, db):
    login(client, 'admin@test.com', 'adminpass')
    client.post(f'/admin/users/{regular_user.id}/edit', data={
        'name': regular_user.name,
        'email': regular_user.email,
        'role': 'user',
        'password': 'newpass123',
    })
    db.session.refresh(regular_user)
    assert regular_user.check_password('newpass123')


def test_delete_user(client, admin_user, regular_user, db):
    user_id = regular_user.id
    login(client, 'admin@test.com', 'adminpass')
    response = client.post(f'/admin/users/{user_id}/delete', follow_redirects=True)
    assert b'deleted' in response.data
    assert db.session.get(User, user_id) is None


def test_cannot_delete_self(client, admin_user, db):
    login(client, 'admin@test.com', 'adminpass')
    response = client.post(f'/admin/users/{admin_user.id}/delete', follow_redirects=True)
    assert b'cannot delete yourself' in response.data
    assert db.session.get(User, admin_user.id) is not None


def test_non_admin_cannot_edit_user(client, regular_user):
    login(client, 'user@test.com', 'userpass')
    response = client.get(f'/admin/users/{regular_user.id}/edit', follow_redirects=True)
    assert b'Admin access required' in response.data


def test_non_admin_cannot_send_email(client, regular_user):
    login(client, 'user@test.com', 'userpass')
    response = client.post('/admin/email', data={
        'subject': 'Hack',
        'body': 'Nope',
    }, follow_redirects=True)
    assert b'Admin access required' in response.data
