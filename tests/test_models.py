from datetime import date
from app.models import User, BeachWeek, MenuItem, DinnerRSVP, RoomAssignment, Chore


def test_user_password(db):
    user = User(name='Test', email='test@test.com', role='user')
    user.set_password('mypassword')
    assert user.check_password('mypassword')
    assert not user.check_password('wrongpassword')


def test_user_is_admin(admin_user, regular_user):
    assert admin_user.is_admin
    assert not regular_user.is_admin


def test_beach_week_creation(db):
    bw = BeachWeek(year=2026, start_date=date(2026, 7, 11), end_date=date(2026, 7, 18))
    db.session.add(bw)
    db.session.commit()
    assert bw.id is not None
    assert bw.year == 2026


def test_room_assignment(db, regular_user):
    bw = BeachWeek(year=2026, start_date=date(2026, 7, 11), end_date=date(2026, 7, 18))
    db.session.add(bw)
    db.session.commit()
    ra = RoomAssignment(beach_week_id=bw.id, room_name='Master Bedroom', user_id=regular_user.id)
    db.session.add(ra)
    db.session.commit()
    assert ra.user.name == 'User'
    assert len(bw.room_assignments) == 1


def test_menu_item_and_rsvp(db, regular_user):
    bw = BeachWeek(year=2026, start_date=date(2026, 7, 11), end_date=date(2026, 7, 18))
    db.session.add(bw)
    db.session.commit()
    item = MenuItem(beach_week_id=bw.id, day=date(2026, 7, 12), meal_type='dinner', description='Shrimp boil')
    db.session.add(item)
    db.session.commit()
    rsvp = DinnerRSVP(menu_item_id=item.id, user_id=regular_user.id, status='not_here')
    db.session.add(rsvp)
    db.session.commit()
    assert rsvp.status == 'not_here'
    assert len(item.rsvps) == 1


def test_chore(db, regular_user):
    bw = BeachWeek(year=2026, start_date=date(2026, 7, 11), end_date=date(2026, 7, 18))
    db.session.add(bw)
    db.session.commit()
    chore = Chore(beach_week_id=bw.id, description='Wash dishes', assigned_user_id=regular_user.id, day=date(2026, 7, 12))
    db.session.add(chore)
    db.session.commit()
    assert chore.assigned_user.name == 'User'
