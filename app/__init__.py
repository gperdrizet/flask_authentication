'''Application factory module'''

import os
import secrets

from flask import Flask

from . import db, auth, blog


def create_app(test_config=None):
    '''Create and configure the Flask application.'''

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=secrets.token_hex(16),
        DATABASE=os.path.join(app.instance_path, 'app.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)

    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)

    except OSError:
        pass

    # A simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # Register the database commands
    db.init_app(app)

    # Register the authentication blueprint
    app.register_blueprint(auth.bp)

    # Register the blog blueprint
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app
