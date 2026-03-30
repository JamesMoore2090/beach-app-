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
