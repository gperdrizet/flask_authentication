'''Fixtures for testing.'''

import os
import tempfile

import pytest
from app import create_app
from app.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def test_app():
    '''Create and configure a new app instance for each test.'''

    db_fd, db_path = tempfile.mkstemp()

    app_instance = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with app_instance.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app_instance

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def test_client(test_app):
    '''A test client for the app.'''

    return test_app.test_client()


@pytest.fixture
def runner(test_app):
    '''A test runner for the apps Click commands.'''

    return test_app.test_cli_runner()


class AuthActions(object):
    '''Helper class for authentication actions in tests.'''

    def __init__(self, client_instance):
        self._client = client_instance

    def login(self, username='test', password='test'):
        '''Login action.'''

        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        '''Logout action.'''

        return self._client.get('/auth/logout')


@pytest.fixture
def auth(test_client):
    '''Authentication actions fixture.'''

    return AuthActions(test_client)
