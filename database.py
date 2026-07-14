"""
database.py
------------
Centralized SQLite database layer for SafeVision AI.
Handles schema creation, seeding of default data, and reusable
query helpers used across every page of the app.
"""

import sqlite3
import os
from datetime import datetime, timedelta
import bcrypt
import pandas as pd

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DB_DIR, "safevision.db")


def get_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT,
    role TEXT NOT NULL CHECK(role IN ('Admin','Safety Officer','Supervisor','Viewer')),
    department TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_date TEXT NOT NULL,
    incident_time TEXT,
    location TEXT NOT NULL,
    incident_type TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('Low','Medium','High','Critical')),
    description TEXT,
    injured_persons INTEGER DEFAULT 0,
    reported_by TEXT,
    status TEXT DEFAULT 'Open' CHECK(status IN ('Open','Under Investigation','Closed')),
    root_cause TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS hazards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_date TEXT NOT NULL,
    location TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    risk_level TEXT NOT NULL CHECK(risk_level IN ('Low','Medium','High','Critical')),
    reported_by TEXT,
    status TEXT DEFAULT 'Open' CHECK(status IN ('Open','Mitigated','Closed')),
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS inspections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inspection_date TEXT NOT NULL,
    area TEXT NOT NULL,
    inspector TEXT NOT NULL,
    checklist_item TEXT,
    result TEXT CHECK(result IN ('Pass','Fail','N/A')),
    findings TEXT,
    score REAL,
    status TEXT DEFAULT 'Completed' CHECK(status IN ('Scheduled','Completed','Overdue')),
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS risk_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_date TEXT NOT NULL,
    activity TEXT NOT NULL,
    hazard_identified TEXT NOT NULL,
    likelihood INTEGER NOT NULL CHECK(likelihood BETWEEN 1 AND 5),
    severity INTEGER NOT NULL CHECK(severity BETWEEN 1 AND 5),
    risk_score INTEGER,
    risk_rating TEXT,
    control_measures TEXT,
    assessed_by TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ppe_inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    min_stock INTEGER NOT NULL DEFAULT 10,
    unit TEXT DEFAULT 'pcs',
    location TEXT,
    last_restocked TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS training (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_name TEXT NOT NULL,
    department TEXT,
    training_type TEXT NOT NULL,
    training_date TEXT NOT NULL,
    expiry_date TEXT,
    trainer TEXT,
    status TEXT DEFAULT 'Completed' CHECK(status IN ('Completed','Scheduled','Expired')),
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS corrective_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT CHECK(source_type IN ('Incident','Hazard','Inspection','Risk Assessment','General')),
    source_id INTEGER,
    description TEXT NOT NULL,
    assigned_to TEXT,
    priority TEXT DEFAULT 'Medium' CHECK(priority IN ('Low','Medium','High')),
    due_date TEXT,
    status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending','In Progress','Completed','Overdue')),
    completion_date TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    action TEXT,
    module TEXT,
    timestamp TEXT DEFAULT (datetime('now'))
);
"""


def init_db():
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.commit()

    cur = conn.execute("SELECT COUNT(*) c FROM users")
    if cur.fetchone()["c"] == 0:
        seed_data(conn)
    conn.close()


def seed_data(conn):
    default_users = [
        ("admin", "Admin@123", "System Administrator", "admin@safevision.ai", "Admin", "HSE"),
        ("safety.officer", "Safety@123", "Priya Sharma", "priya@safevision.ai", "Safety Officer", "HSE"),
        ("supervisor", "Super@123", "Ravi Kumar", "ravi@safevision.ai", "Supervisor", "Operations"),
        ("viewer", "View@123", "Guest Viewer", "viewer@safevision.ai", "Viewer", "Management"),
    ]
    for username, pwd, name, email, role, dept in default_users:
        conn.execute(
            "INSERT INTO users (username, password_hash, full_name, email, role, department) VALUES (?,?,?,?,?,?)",
            (username, hash_password(pwd), name, email, role, dept),
        )

    today = datetime.now()

    incidents = [
        ((today - timedelta(days=40)).strftime("%Y-%m-%d"), "09:15", "Warehouse A", "Slip/Fall", "Medium",
         "Worker slipped on wet floor near loading bay.", 1, "Ravi Kumar", "Closed", "Wet floor, no warning sign"),
        ((today - timedelta(days=30)).strftime("%Y-%m-%d"), "14:00", "Production Line 2", "Machine Injury", "High",
         "Hand caught in conveyor mechanism.", 1, "Priya Sharma", "Closed", "Guard removed during maintenance"),
        ((today - timedelta(days=20)).strftime("%Y-%m-%d"), "11:30", "Chemical Storage", "Chemical Spill", "Critical",
         "Solvent drum leaked during transfer.", 0, "Priya Sharma", "Under Investigation", "Faulty drum valve"),
        ((today - timedelta(days=12)).strftime("%Y-%m-%d"), "08:00", "Site Gate", "Near Miss", "Low",
         "Forklift nearly collided with pedestrian.", 0, "Ravi Kumar", "Open", None),
        ((today - timedelta(days=5)).strftime("%Y-%m-%d"), "16:45", "Warehouse B", "Fire", "Critical",
         "Electrical short circuit caused small fire, extinguished quickly.", 0, "Priya Sharma", "Open", None),
        ((today - timedelta(days=2)).strftime("%Y-%m-%d"), "10:10", "Production Line 1", "Struck By Object", "Medium",
         "Falling material struck worker's shoulder.", 1, "Ravi Kumar", "Open", None),
    ]
    conn.executemany(
        """INSERT INTO incidents (incident_date, incident_time, location, incident_type, severity,
           description, injured_persons, reported_by, status, root_cause)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        incidents,
    )

    hazards = [
        ((today - timedelta(days=35)).strftime("%Y-%m-%d"), "Warehouse A", "Slip/Trip", "Loose flooring tile", "Medium", "Ravi Kumar", "Mitigated"),
        ((today - timedelta(days=25)).strftime("%Y-%m-%d"), "Production Line 2", "Machine Guarding", "Missing guard on cutter", "High", "Priya Sharma", "Closed"),
        ((today - timedelta(days=15)).strftime("%Y-%m-%d"), "Chemical Storage", "Chemical Exposure", "Improper labeling on drums", "High", "Priya Sharma", "Open"),
        ((today - timedelta(days=8)).strftime("%Y-%m-%d"), "Office Block", "Electrical", "Exposed wiring near pantry", "Medium", "Admin", "Open"),
        ((today - timedelta(days=3)).strftime("%Y-%m-%d"), "Site Gate", "Traffic", "Poor visibility at blind corner", "Medium", "Ravi Kumar", "Open"),
        ((today - timedelta(days=1)).strftime("%Y-%m-%d"), "Warehouse B", "Fire", "Blocked fire exit", "Critical", "Priya Sharma", "Open"),
    ]
    conn.executemany(
        """INSERT INTO hazards (report_date, location, category, description, risk_level, reported_by, status)
           VALUES (?,?,?,?,?,?,?)""",
        hazards,
    )

    inspections = [
        ((today - timedelta(days=30)).strftime("%Y-%m-%d"), "Warehouse A", "Priya Sharma", "Fire extinguisher check", "Pass", "All units charged", 95, "Completed"),
        ((today - timedelta(days=25)).strftime("%Y-%m-%d"), "Production Line 1", "Ravi Kumar", "Machine guard inspection", "Fail", "2 guards missing bolts", 60, "Completed"),
        ((today - timedelta(days=18)).strftime("%Y-%m-%d"), "Chemical Storage", "Priya Sharma", "PPE compliance", "Pass", "All staff wearing PPE", 90, "Completed"),
        ((today - timedelta(days=10)).strftime("%Y-%m-%d"), "Office Block", "Admin", "Emergency exit check", "Pass", "Clear and marked", 100, "Completed"),
        ((today - timedelta(days=4)).strftime("%Y-%m-%d"), "Warehouse B", "Ravi Kumar", "Housekeeping audit", "Fail", "Blocked walkway", 55, "Completed"),
        ((today + timedelta(days=5)).strftime("%Y-%m-%d"), "Production Line 2", "Priya Sharma", "Monthly safety audit", None, None, None, "Scheduled"),
    ]
    conn.executemany(
        """INSERT INTO inspections (inspection_date, area, inspector, checklist_item, result, findings, score, status)
           VALUES (?,?,?,?,?,?,?,?)""",
        inspections,
    )

    def rating(score):
        if score <= 5:
            return "Low"
        elif score <= 10:
            return "Medium"
        elif score <= 15:
            return "High"
        return "Critical"

    risk_rows = [
        ("Forklift operation", "Collision with pedestrian", 3, 4, "Ravi Kumar"),
        ("Chemical handling", "Toxic exposure", 2, 5, "Priya Sharma"),
        ("Working at height", "Fall from scaffolding", 3, 5, "Priya Sharma"),
        ("Manual lifting", "Musculoskeletal injury", 4, 2, "Ravi Kumar"),
        ("Electrical maintenance", "Electric shock", 2, 4, "Admin"),
        ("Machine operation", "Entanglement", 3, 4, "Priya Sharma"),
    ]
    risk_assessments = []
    for i, (activity, hazard, like, sev, by) in enumerate(risk_rows):
        score = like * sev
        risk_assessments.append((
            (today - timedelta(days=30 - i * 3)).strftime("%Y-%m-%d"),
            activity, hazard, like, sev, score, rating(score),
            "Implement engineering controls, PPE, and training.", by
        ))
    conn.executemany(
        """INSERT INTO risk_assessments (assessment_date, activity, hazard_identified, likelihood, severity,
           risk_score, risk_rating, control_measures, assessed_by) VALUES (?,?,?,?,?,?,?,?,?)""",
        risk_assessments,
    )

    ppe_items = [
        ("Safety Helmet", "Head Protection", 120, 50, "pcs", "Main Store", (today - timedelta(days=10)).strftime("%Y-%m-%d")),
        ("Safety Goggles", "Eye Protection", 35, 40, "pcs", "Main Store", (today - timedelta(days=20)).strftime("%Y-%m-%d")),
        ("Steel Toe Boots", "Foot Protection", 60, 30, "pairs", "Main Store", (today - timedelta(days=15)).strftime("%Y-%m-%d")),
        ("Nitrile Gloves", "Hand Protection", 15, 100, "boxes", "Chemical Store", (today - timedelta(days=5)).strftime("%Y-%m-%d")),
        ("Respirator Mask N95", "Respiratory Protection", 200, 100, "pcs", "Main Store", (today - timedelta(days=8)).strftime("%Y-%m-%d")),
        ("Hi-Vis Vest", "Body Protection", 8, 25, "pcs", "Main Store", (today - timedelta(days=40)).strftime("%Y-%m-%d")),
        ("Safety Harness", "Fall Protection", 18, 15, "sets", "Warehouse B", (today - timedelta(days=25)).strftime("%Y-%m-%d")),
        ("Ear Plugs", "Hearing Protection", 300, 150, "pairs", "Main Store", (today - timedelta(days=12)).strftime("%Y-%m-%d")),
    ]
    conn.executemany(
        """INSERT INTO ppe_inventory (item_name, category, quantity, min_stock, unit, location, last_restocked)
           VALUES (?,?,?,?,?,?,?)""",
        ppe_items,
    )

    trainings = [
        ("Ravi Kumar", "Operations", "Fire Safety", (today - timedelta(days=100)).strftime("%Y-%m-%d"), (today + timedelta(days=265)).strftime("%Y-%m-%d"), "Priya Sharma", "Completed"),
        ("Suresh Nair", "Production", "First Aid", (today - timedelta(days=200)).strftime("%Y-%m-%d"), (today - timedelta(days=10)).strftime("%Y-%m-%d"), "External Trainer", "Expired"),
        ("Anita Rao", "Warehouse", "Forklift Operation", (today - timedelta(days=50)).strftime("%Y-%m-%d"), (today + timedelta(days=315)).strftime("%Y-%m-%d"), "Ravi Kumar", "Completed"),
        ("Vikram Singh", "Chemical Store", "Hazmat Handling", (today - timedelta(days=15)).strftime("%Y-%m-%d"), (today + timedelta(days=350)).strftime("%Y-%m-%d"), "Priya Sharma", "Completed"),
        ("Meena Iyer", "Office", "Workplace Ergonomics", (today + timedelta(days=10)).strftime("%Y-%m-%d"), None, "Priya Sharma", "Scheduled"),
        ("Karan Mehta", "Production", "Machine Safety", (today - timedelta(days=400)).strftime("%Y-%m-%d"), (today - timedelta(days=35)).strftime("%Y-%m-%d"), "Ravi Kumar", "Expired"),
    ]
    conn.executemany(
        """INSERT INTO training (employee_name, department, training_type, training_date, expiry_date, trainer, status)
           VALUES (?,?,?,?,?,?,?)""",
        trainings,
    )

    corrective_actions = [
        ("Incident", 2, "Reinstall and lock-out conveyor guard; retrain maintenance staff.", "Ravi Kumar", "High", (today - timedelta(days=20)).strftime("%Y-%m-%d"), "Completed", (today - timedelta(days=18)).strftime("%Y-%m-%d")),
        ("Hazard", 3, "Relabel all chemical drums per GHS standard.", "Priya Sharma", "High", (today + timedelta(days=3)).strftime("%Y-%m-%d"), "In Progress", None),
        ("Inspection", 2, "Replace missing bolts on machine guards.", "Ravi Kumar", "Medium", (today - timedelta(days=15)).strftime("%Y-%m-%d"), "Overdue", None),
        ("Hazard", 6, "Clear blocked fire exit immediately.", "Admin", "High", (today + timedelta(days=1)).strftime("%Y-%m-%d"), "Pending", None),
        ("Incident", 4, "Install pedestrian barriers at site gate.", "Ravi Kumar", "Medium", (today + timedelta(days=10)).strftime("%Y-%m-%d"), "Pending", None),
        ("Inspection", 5, "Clear housekeeping walkway obstruction.", "Ravi Kumar", "Low", (today - timedelta(days=1)).strftime("%Y-%m-%d"), "Completed", (today - timedelta(days=1)).strftime("%Y-%m-%d")),
    ]
    conn.executemany(
        """INSERT INTO corrective_actions (source_type, source_id, description, assigned_to, priority, due_date, status, completion_date)
           VALUES (?,?,?,?,?,?,?,?)""",
        corrective_actions,
    )

    conn.commit()


# ---------- Generic helpers ----------

def run_query(query, params=()):
    conn = get_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def execute(query, params=()):
    conn = get_connection()
    cur = conn.execute(query, params)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id


def log_activity(username, action, module):
    execute(
        "INSERT INTO activity_log (username, action, module) VALUES (?,?,?)",
        (username, action, module),
    )
