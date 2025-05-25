"""Утилиты: загрузка/генерация флагов, поиск флага."""
from __future__ import annotations
import os
import random
import string
import uuid
from collections import namedtuple
from pathlib import Path
from typing import Dict, List
import json

FlagsRecord = namedtuple("FlagsRecord", ["flag", "service", "flag_type", "description", "injection_point"])

FLAGS_FILE = Path("/opt/flags/flags.json")
FLAGS_CONFIG = Path("/opt/flags/config.json")

# Шаблоны для генерации флагов
FLAG_FORMAT = "FLAG{{{service}_{flag_type}_{unique}}}"
FLAG_CHARS = string.ascii_uppercase + string.digits

# Конфигурация флагов для каждого сервиса
SERVICES_CONFIG = {
    "dvwa": {
        "description": "Damn Vulnerable Web Application",
        "flags": {
            "sqli": {
                "description": "Найдите флаг через SQL-инъекцию в форме входа",
                "injection_point": "Логин форма на /vulnerabilities/sqli/",
                "template": "' UNION SELECT 1,'{flag}',3,4 -- "
            },
            "xss": {
                "description": "Найдите флаг через XSS в форме поиска",
                "injection_point": "Поле поиска на /vulnerabilities/xss_r/",
                "template": "<script>alert('{flag}')</script>"
            }
        }
    },
    "juice-shop": {
        "description": "OWASP Juice Shop",
        "flags": {
            "xss": {
                "description": "XSS в поле поиска",
                "injection_point": "Поиск в шапке сайта",
                "template": "<script>alert('{flag}')</script>"
            },
            "admin": {
                "description": "Получите доступ к админке",
                "injection_point": "Форма входа",
                "template": "admin@juice-sh.op:{flag}"
            }
        }
    }
}


def _generate_flags() -> List[Dict]:
    """Генерация флагов и их инъекционных векторов"""
    flags = []
    for service, config in SERVICES_CONFIG.items():
        for flag_type, flag_config in config["flags"].items():
            unique = ''.join(random.choices(FLAG_CHARS, k=8))
            flag = FLAG_FORMAT.format(
                service=service,
                flag_type=flag_type,
                unique=unique
            )

            flags.append({
                "flag": flag,
                "service": service,
                "flag_type": flag_type,
                "description": flag_config["description"],
                "injection_point": flag_config["injection_point"],
                "injection_template": flag_config["template"].format(flag=flag)
            })

    # Сохраняем конфиг для сервисов
    with FLAGS_CONFIG.open('w') as f:
        json.dump(SERVICES_CONFIG, f)

    return flags


def load_flags(force_reload: bool = False) -> List[FlagsRecord]:
    """Загрузка флагов из файла или генерация новых"""
    global _flags_cache

    if _flags_cache and not force_reload:
        return _flags_cache

    if not FLAGS_FILE.exists():
        FLAGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        flags = _generate_flags()
        with FLAGS_FILE.open('w') as f:
            json.dump(flags, f)
    else:
        with FLAGS_FILE.open() as f:
            flags = json.load(f)

    _flags_cache = [FlagsRecord(**f) for f in flags]
    return _flags_cache


def get_service_instructions(service: str) -> Dict:
    """Получение инструкций для конкретного сервиса"""
    if not FLAGS_CONFIG.exists():
        load_flags()

    with FLAGS_CONFIG.open() as f:
        config = json.load(f)

    return config.get(service, {})


def inject_flag(service: str, flag_type: str) -> str:
    """Получение инъекционного вектора для флага"""
    for flag in load_flags():
        if flag.service == service and flag.flag_type == flag_type:
            return flag.injection_template
    return ""









# """Утилиты: загрузка/генерация флагов, поиск флага."""
#
# from __future__ import annotations
#
# import os
# import random
# import uuid
# from collections import namedtuple
# from pathlib import Path
#
FlagsRecord = namedtuple("FlagsRecord", ["flag", "service", "flag_type"])

FLAGS_FILE = Path("/opt/flags/flags.txt")

# Кэшируем в память
_flags_cache: list[FlagsRecord] = []

# Статический список лабораторных (должно совпадать с compose)
LABS = [
    "dvwa",
    "juice-shop",
    "mutillidae",
    "bwapp",
    "hackazon",
    "wordpress",
    "goahead",
    "nginx_vuln",
    "webgoat",
]

FLAG_TYPES = ["easy", "medium", "hard"]


#––––––––––––––––––––––––––––––––––––––––––––––––––
#   Генерация / чтение файла с флагами
#––––––––––––––––––––––––––––––––––––––––––––––––––

def _generate_flags() -> list[FlagsRecord]:
    """Случайно генерируем по 3 флага на сервис."""
    records: list[FlagsRecord] = []
    for lab in LABS:
        for t in FLAG_TYPES:
            rand = uuid.uuid4().hex[:12]
            flag = f"FLAG{{{rand}}}"
            records.append(FlagsRecord(flag=flag, service=lab, flag_type=t))
    return records


def load_flags(force_reload: bool = False) -> list[FlagsRecord]:
    """Читаем (или создаём) flags.txt, кладём в кэш."""
    global _flags_cache
    if _flags_cache and not force_reload:
        return _flags_cache

    # Создаём файл при первом запуске
    if not FLAGS_FILE.exists():
        FLAGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        generated = _generate_flags()
        with FLAGS_FILE.open("w", encoding="utf-8") as fh:
            for rec in generated:
                fh.write(f"{rec.flag};{rec.service};{rec.flag_type}\n")
        _flags_cache = generated
        return _flags_cache

    # Читаем существующий файл
    records: list[FlagsRecord] = []
    with FLAGS_FILE.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                flag, service, flag_type = line.split(";", 2)
            except ValueError:
                continue  # пропускаем битые строки
            records.append(FlagsRecord(flag=flag, service=service, flag_type=flag_type))
    _flags_cache = records
    return _flags_cache


#––––––––––––––––––––––––––––––––––––––––––––––––––
#   Поиск флага
#––––––––––––––––––––––––––––––––––––––––––––––––––

def lookup_flag(flag: str) -> FlagsRecord | None:
    flag = flag.strip()
    if not flag:
        return None
    for rec in _flags_cache or load_flags():
        if rec.flag == flag:
            return rec
    return None


#––––––––––––––––––––––––––––––––––––––––––––––––––
#   Доп. утилки
#––––––––––––––––––––––––––––––––––––––––––––––––––

def total_flags() -> int:
    return len(_flags_cache or load_flags())
