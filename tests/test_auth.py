import pytest
from flask import g, session
from app.db import get_db


def test_register(test_client, test_app):
    '''Test user registration.'''

    assert test_client.get('/auth/register').status_code == 200

    response = test_client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )

    assert response.headers["Location"] == "/auth/login"

    with test_app.app_context():

        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'",
        ).fetchone() is not None


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),
    ('a', '', b'Password is required.'),
    ('test', 'test', b'already registered'),
))
def test_register_validate_input(test_client, username, password, message):
    '''Test registration input validation.'''

    response = test_client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )

    assert message in response.data


def test_login(test_client, auth):
    '''Test user login.'''

    assert test_client.get('/auth/login').status_code == 200

    response = auth.login()

    assert response.headers["Location"] == "/"

    with test_client:
        test_client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    '''Test login input validation.'''

    response = auth.login(username, password)
    assert message in response.data


def test_logout(test_client, auth):
    '''Test user logout.'''

    auth.login()

    with test_client:
        auth.logout()
        assert 'user_id' not in session
