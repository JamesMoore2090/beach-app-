from app.models import User


def test_login_page_loads(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Login' in response.data


def test_login_success(client, regular_user):
    response = client.post('/login', data={
        'email': 'user@test.com',
        'password': 'userpass',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Dashboard' in response.data


def test_login_bad_password(client, regular_user):
    response = client.post('/login', data={
        'email': 'user@test.com',
        'password': 'wrong',
    }, follow_redirects=True)
    assert b'Invalid email or password' in response.data


def test_login_bad_email(client):
    response = client.post('/login', data={
        'email': 'nobody@test.com',
        'password': 'pass',
    }, follow_redirects=True)
    assert b'Invalid email or password' in response.data


def test_logout(client, regular_user):
    client.post('/login', data={'email': 'user@test.com', 'password': 'userpass'})
    response = client.get('/logout', follow_redirects=True)
    assert b'Login' in response.data


def test_dashboard_requires_login(client):
    response = client.get('/dashboard', follow_redirects=True)
    assert b'Login' in response.data


# Password reset tests

def test_reset_request_page_loads(client):
    response = client.get('/reset-password')
    assert response.status_code == 200
    assert b'Reset Password' in response.data


def test_reset_request_sends_email(client, regular_user, app):
    with app.extensions['mail'].record_messages() as outbox:
        response = client.post('/reset-password', data={
            'email': 'user@test.com',
        }, follow_redirects=True)
        assert b'reset link has been sent' in response.data
        assert len(outbox) == 1
        assert 'reset-password' in outbox[0].body


def test_reset_request_unknown_email_no_leak(client):
    response = client.post('/reset-password', data={
        'email': 'nobody@test.com',
    }, follow_redirects=True)
    # Same message whether email exists or not
    assert b'reset link has been sent' in response.data


def test_reset_confirm_valid_token(client, regular_user, app):
    from itsdangerous import URLSafeTimedSerializer
    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    token = s.dumps('user@test.com', salt='password-reset')

    response = client.post(f'/reset-password/{token}', data={
        'password': 'newpassword123',
    }, follow_redirects=True)
    assert b'Password updated' in response.data

    # Verify new password works
    response = client.post('/login', data={
        'email': 'user@test.com',
        'password': 'newpassword123',
    }, follow_redirects=True)
    assert b'Dashboard' in response.data


def test_reset_confirm_invalid_token(client):
    response = client.get('/reset-password/badtoken', follow_redirects=True)
    assert b'invalid or expired' in response.data


def test_reset_confirm_short_password(client, regular_user, app):
    from itsdangerous import URLSafeTimedSerializer
    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    token = s.dumps('user@test.com', salt='password-reset')

    response = client.post(f'/reset-password/{token}', data={
        'password': 'short',
    })
    assert b'at least 8 characters' in response.data


# Admin user creation tests

def test_admin_can_add_user(client, admin_user, db):
    client.post('/login', data={'email': 'admin@test.com', 'password': 'adminpass'})
    response = client.post('/admin/users/add', data={
        'name': 'New Person',
        'email': 'new@test.com',
        'password': 'newpassword',
        'birthday': '1995-03-15',
        'role': 'user',
    }, follow_redirects=True)
    assert b'User New Person created' in response.data
    assert User.query.filter_by(email='new@test.com').first() is not None


def test_regular_user_cannot_add_user(client, regular_user):
    client.post('/login', data={'email': 'user@test.com', 'password': 'userpass'})
    response = client.get('/admin/users/add', follow_redirects=True)
    assert b'Admin access required' in response.data


def test_add_user_duplicate_email(client, admin_user, regular_user):
    client.post('/login', data={'email': 'admin@test.com', 'password': 'adminpass'})
    response = client.post('/admin/users/add', data={
        'name': 'Duplicate',
        'email': 'user@test.com',
        'password': 'somepassword',
        'role': 'user',
    }, follow_redirects=True)
    assert b'Email already registered' in response.data
