# database.py

import json
import os

DB_FILE = "analysis_history.json"


def init_db():
    """
    Create JSON database file if it doesn't exist
    """
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump([], f)


def read_db():
    """
    Safely read JSON file
    """
    init_db()

    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                return []
    except json.JSONDecodeError:
        # If file is corrupted or empty
        return []


def write_db(data):
    """
    Write data back to JSON file
    """
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)


def save_report(report_data):
    """
    Save new analysis report
    """
    data = read_db()
    data.append(report_data)
    write_db(data)


def get_reports():
    """
    Get all saved reports
    """
    return read_db()