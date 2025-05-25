"""Blueprint auth: регистрация, логин, логаут."""

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user

from .models import User
from . import db

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if not username or not password:
            flash("Заполните все поля", "danger")
            return render_template("register.html")
        if User.query.filter_by(username=username).first():
            flash("Пользователь уже существует", "warning")
            return render_template("register.html")
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Регистрация успешна!", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Добро пожаловать!", "success")
            return redirect(url_for("main.dashboard"))
        flash("Неверные учётные данные", "danger")
    return render_template("login.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли", "info")
    return redirect(url_for("auth.login"))
