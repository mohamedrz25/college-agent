from flask import Flask

from .attendance import attendance_bp
from .attendance import routes


def create_app():
    app = Flask(__name__)

    app.register_blueprint(attendance_bp)

    return app
