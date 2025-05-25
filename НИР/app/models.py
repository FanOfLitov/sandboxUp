"""SQLAlchemy модели: пользователи, найденные флаги."""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from . import db, login_manager
from flask_login import UserMixin

#############################################
#                 USERS                     #
#############################################

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    # связь 1-ко-многим
    flags = db.relationship("FlagFound", back_populates="user", cascade="all, delete-orphan")

    # –– helpers ––
    def set_password(self, raw: str):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw: str) -> bool:
        return check_password_hash(self.password_hash, raw)

    # Для прогресса: сколько всего флагов и сколько найдено
    def progress(self, total_flags: int) -> float:
        if total_flags == 0:
            return 0.0
        return round((len(self.flags) / total_flags) * 100, 2)


#############################################
#            Найденные флаги                #
#############################################

class FlagFound(db.Model):
    __tablename__ = "flags_found"

    id = db.Column(db.Integer, primary_key=True)
    flag = db.Column(db.String(128), nullable=False)
    lab_name = db.Column(db.String(64), nullable=False)
    flag_type = db.Column(db.String(32))
    found_at = db.Column(db.DateTime, default=datetime.utcnow)

    # FK → users
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    user = db.relationship("User", back_populates="flags")

    def __repr__(self):
        return f"<Flag {self.flag} {self.user.username}>"


#############################################
#        Flask-Login integration            #
#############################################

@login_manager.user_loader
def _load_user(user_id):
    from .models import User  # локальный импорт, чтобы избежать циклов
    return User.query.get(int(user_id))
