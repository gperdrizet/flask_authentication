'''Blog tests.'''

import pytest
from app.db import get_db


def test_index(test_client, auth):
    '''Test the index page.'''

    response = test_client.get('/')

    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = test_client.get('/')

    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'by test on 2018-01-01' in response.data
    assert b'test\nbody' in response.data
    assert b'href="/1/update"' in response.data


@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(test_client, path):
    '''Test that login is required for certain views.'''

    response = test_client.post(path)
    assert response.headers['Location'] == '/auth/login'


def test_author_required(test_app, test_client, auth):
    '''Test that only the author can modify a post.'''

    # change the post author to another user
    with test_app.app_context():
        db = get_db()
        db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
        db.commit()

    auth.login()

    # Current user can't modify other user's post
    assert test_client.post('/1/update').status_code == 403
    assert test_client.post('/1/delete').status_code == 403

    # Current user doesn't see edit link
    assert b'href="/1/update"' not in test_client.get('/').data


@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete',
))
def test_exists_required(test_client, auth, path):
    '''Test that a 404 is returned if the post does not exist.'''

    auth.login()
    assert test_client.post(path).status_code == 404


def test_create(test_client, auth, test_app):
    '''Test creating a blog post.'''

    auth.login()

    assert test_client.get('/create').status_code == 200

    test_client.post('/create', data={'title': 'created', 'body': ''})

    with test_app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 2


def test_update(test_client, auth, test_app):
    '''Test updating a blog post.'''

    auth.login()

    assert test_client.get('/1/update').status_code == 200

    test_client.post('/1/update', data={'title': 'updated', 'body': ''})

    with test_app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post['title'] == 'updated'


@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
))
def test_create_update_validate(test_client, auth, path):
    '''Test validation for creating and updating posts.'''

    auth.login()
    response = test_client.post(path, data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data


def test_delete(test_client, auth, test_app):
    '''Test deleting a blog post.'''

    auth.login()
    response = test_client.post('/1/delete')
    assert response.headers["Location"] == "/"

    with test_app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post is None
