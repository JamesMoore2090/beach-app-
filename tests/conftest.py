import pytest
from datetime import date
from app import create_app, db as _db
from app.models import User


@pytest.fixture
def app():
    app = create_app('test')
    yield app


@pytest.fixture
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()


@pytest.fixture
def client(app, db):
    return app.test_client()


@pytest.fixture
def admin_user(db):
    user = User(name='Admin', email='admin@test.com', role='admin')
    user.set_password('adminpass')
    user.birthday = date(1980, 7, 4)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def regular_user(db):
    user = User(name='User', email='user@test.com', role='user')
    user.set_password('userpass')
    user.birthday = date(1990, 6, 15)
    db.session.add(user)
    db.session.commit()
    return user
