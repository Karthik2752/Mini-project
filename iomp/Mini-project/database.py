import json
import os

DB_FILE = "analysis_history.json"


def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)


def read_db():
    init_db()

    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def write_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def save_report(report_data):
    data = read_db()
    data.append(report_data)
    data = data[-100:]
    write_db(data)


def get_reports():
    return read_db()