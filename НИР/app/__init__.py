from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os

# Инициализация единственных синглтонов

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def create_app():
    """Фабрика приложения."""
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Конфигурация
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///tmp.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "insecure")

    # Инициализируем расширения
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Регистрируем blueprints
    from .routes import bp as main_bp
    from .auth import bp as auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    # При старте один раз кэшируем флаги в память
    from .utils import load_flags
    load_flags()

    return app
