from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_cors import CORS

db = SQLAlchemy()


def create_app(config):
    flask_app = Flask(__name__)
    for k,v in config.items():
        flask_app.config[k] = v
    from . import app
    flask_app.register_blueprint(app.api)
    CORS(flask_app)
    db.init_app(flask_app)

    with flask_app.app_context():
        db.create_all()
        app.reload_state()
    return flask_app