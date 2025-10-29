'''Tests for the app factory.'''


from app import create_app


def test_config():
    '''Test the app configuration.'''

    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_hello(test_client):
    '''Test the /hello route.'''

    response = test_client.get('/hello')
    assert response.data == b'Hello, World!'
