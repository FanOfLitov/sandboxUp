"""Основной Blueprint: главная, дашборд, приём флагов."""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

from .models import FlagFound
from . import db
from .utils import lookup_flag, total_flags
from flask import render_template


bp = Blueprint("main", __name__)

LABS_INFO = [
    {
        "name": "dvwa",
        "description": "Damn Vulnerable Web Application — учебный сервис с уязвимостями.",
        "url": "http://localhost:8080",
        "port": 8080,
        "instruction": """
            <p>DVWA — это учебный сервис для практики веб-уязвимостей.</p>
            <ul>
              <li>Вход: admin/password</li>
              <li>Цель: найти флаги, используя SQLi, XSS и др.</li>
            </ul>
            
        """,
    },
    {
        "name": "juice-shop",
        "description": "OWASP Juice Shop — современный уязвимый веб-магазин.",
        "url": "http://localhost:3000",
        "port": 3000,
        "instruction": """
            <p>Juice Shop — тренажёр с множеством уязвимостей.</p>
            <ul>
              <li>Вход: нет обязательной регистрации</li>
              <li>Цель: найти и сдать флаги через форму.</li>
            </ul>
        """,
    },
    {
        "name": "webgoat",
        "description": "webgoat",
        "url": "http://localhost:8089",
        "port": 8089,
        "instruction": """
            <p>OWASP Mutillidae II</p>
            <ul>
              <li>Вход: нет обязательной регистрации</li>
              <li>Цель: найти и сдать флаги через форму.</li>
            </ul>
        """,
    },
    {
        "name": "wordpress:5.0",
        "description": "",
        "url": "http://localhost:8085",
        "port": 8085,
        "instruction": """
            <p>bwapp</p>
            <ul>
              <li>Вход: нет обязательной регистрации</li>
              <li>Цель: найти и сдать флаги через форму.</li>
            </ul>
        """,
    },
{
        "name": "hackazon",
        "description": "hackazon",
        "url": "http://localhost:8086",
        "port": 8086,
        "instruction": """
            <p>bwapp</p>
            <ul>
              <li>Вход: нет обязательной регистрации</li>
              <li>Цель: найти и сдать флаги через форму.</li>
            </ul>
        """,
    },
    # Добавь остальные сервисы по аналогии...
]

@bp.route("/quests")
@login_required
def quests():
    return render_template("quest.html", labs=LABS_INFO)

@bp.route("/instructions")
@login_required
def instructions():
    return render_template("instructions.html", labs=LABS_INFO)
@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/dashboard")
@login_required
def dashboard():
    flags = current_user.flags
    progress = current_user.progress(total_flags())
    total=total_flags()
    return render_template("dashboard.html", flags=flags, progress=progress,total_flags=total)


@bp.route("/api/flags/<service>")
@login_required
def get_service_flags(service):
    """Получение флагов и инструкций для сервиса"""
    from .utils import get_service_instructions, inject_flag

    instructions = get_service_instructions(service)
    if not instructions:
        return jsonify({"error": "Service not found"}), 404

    flags = []
    for flag_type, config in instructions.get("flags", {}).items():
        flags.append({
            "type": flag_type,
            "description": config["description"],
            "injection_point": config["injection_point"],
            "injection_template": inject_flag(service, flag_type)
        })

    return jsonify({
        "service": service,
        "description": instructions["description"],
        "flags": flags
    })


@bp.route("/submit_flag", methods=["POST"])
@login_required
def submit_flag():
    flag_text = request.form.get("flag", "").strip()
    if not flag_text:
        return jsonify(status="error", message="Флаг пустой"), 400

    found = lookup_flag(flag_text)
    if not found:
        return jsonify(status="error", message="Неверный флаг"), 400

    if FlagFound.query.filter_by(user_id=current_user.id, flag=flag_text).first():
        return jsonify(status="error", message="Уже засчитан"), 400

    ff = FlagFound(
        user_id=current_user.id,
        flag=found.flag,
        lab_name=found.service,
        flag_type=found.flag_type
    )
    db.session.add(ff)
    db.session.commit()

    return jsonify(
        status="success",
        message=f"Принято: {found.service}/{found.flag_type}",
        progress=current_user.progress(total_flags())
    )
# @bp.route("/submit_flag", methods=["POST"])
# @login_required
# def submit_flag():
#     flag_text = request.form.get("flag", "").strip()
#     if not flag_text:
#         return jsonify(status="error", message="Флаг пустой"), 400
#
#     found = lookup_flag(flag_text)
#     if not found:
#         return jsonify(status="error", message="Неверный флаг"), 400
#
#     # Проверяем, сдавался ли ранее
#     if FlagFound.query.filter_by(user_id=current_user.id, flag=flag_text).first():
#         return jsonify(status="error", message="Уже засчитан"), 400
#
#     ff = FlagFound(user_id=current_user.id,
#                    flag=found.flag,
#                    lab_name=found.service,
#                    flag_type=found.flag_type)
#     db.session.add(ff)
#     db.session.commit()
#
#     return jsonify(status="success", message=f"Принято: {found.service}/{found.flag_type}")
