from datetime import date
from unittest.mock import patch
from app.models import User
from app.email_tasks import check_birthdays


def test_birthday_email_sent(app, db):
    today = date.today()
    user = User(name='Birthday Bob', email='bob@test.com', role='user',
                birthday=today.replace(year=1990))
    user.set_password('pass')
    other = User(name='Other', email='other@test.com', role='user')
    other.set_password('pass')
    db.session.add_all([user, other])
    db.session.commit()

    with app.extensions['mail'].record_messages() as outbox:
        sent = check_birthdays(app)
        assert 'Birthday Bob' in sent
        assert len(outbox) == 1
        assert 'Birthday Bob' in outbox[0].subject
        # Email goes to all users
        assert set(outbox[0].recipients) == {'bob@test.com', 'other@test.com'}


def test_no_birthday_today(app, db):
    today = date.today()
    # Birthday is tomorrow
    tomorrow = today.replace(day=today.day + 1) if today.day < 28 else today.replace(month=today.month + 1, day=1)
    user = User(name='Not Today', email='not@test.com', role='user',
                birthday=tomorrow.replace(year=1990))
    user.set_password('pass')
    db.session.add(user)
    db.session.commit()

    with app.extensions['mail'].record_messages() as outbox:
        sent = check_birthdays(app)
        assert sent == []
        assert len(outbox) == 0


def test_multiple_birthdays_same_day(app, db):
    today = date.today()
    u1 = User(name='Twin A', email='a@test.com', role='user',
              birthday=today.replace(year=1985))
    u1.set_password('pass')
    u2 = User(name='Twin B', email='b@test.com', role='user',
              birthday=today.replace(year=1990))
    u2.set_password('pass')
    db.session.add_all([u1, u2])
    db.session.commit()

    with app.extensions['mail'].record_messages() as outbox:
        sent = check_birthdays(app)
        assert len(sent) == 2
        assert len(outbox) == 2


def test_password_reset_sends_email(client, regular_user, app):
    """Password reset emails already tested in test_auth but included here for completeness."""
    with app.extensions['mail'].record_messages() as outbox:
        client.post('/reset-password', data={'email': 'user@test.com'})
        assert len(outbox) == 1
        assert 'Password Reset' in outbox[0].subject


def test_admin_broadcast_email(client, admin_user, regular_user, app):
    """Admin broadcast already tested in test_admin but included here for completeness."""
    from tests.test_admin import login
    login(client, 'admin@test.com', 'adminpass')
    with app.extensions['mail'].record_messages() as outbox:
        client.post('/admin/email', data={
            'subject': 'Beach Update',
            'body': 'Pack your bags!',
        })
        assert len(outbox) == 1
        assert 'Beach Update' in outbox[0].subject
        assert 'Pack your bags!' in outbox[0].body
