'''Fixtures for testing.'''

import os
import tempfile

import pytest
from app import create_app
from app.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    '''Create and configure a new app instance for each test.'''

    db_fd, db_path = tempfile.mkstemp()

    test_app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with test_app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield test_app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(test_app):
    '''A test client for the app.'''

    return test_app.test_client()


@pytest.fixture
def runner(test_app):
    '''A test runner for the apps Click commands.'''

    return test_app.test_cli_runner()
