from flask import Flask

from config import Config
from app.extensions import db, login_manager, csrf

from app.main.routes import main_bp
from app.auth.routes import auth_bp
from app.student.routes import student_bp
from app.teacher.routes import teacher_bp

from app.models.user import User


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(teacher_bp)

    with app.app_context():
        db.create_all()

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))