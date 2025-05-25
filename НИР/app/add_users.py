from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    if not User.query.filter_by(username="admin").first():
        user = User(username="admin")
        user.set_password("12345")  # Задай пароль
        db.session.add(user)
        db.session.commit()
        print("Пользователь admin создан")
    else:
        print("Пользователь admin уже существует")