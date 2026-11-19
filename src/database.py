"""
Privacy-Preserving SQLite Analysis History Database Module
Persists lightweight metadata, classification verdicts, and indicators.
Never persists full email message bodies, passwords, or authentication secrets.
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# In serverless environments like Vercel/AWS Lambda, only /tmp is writable
if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    DEFAULT_DB_PATH = os.path.join("/tmp", "analysis_history.db")
else:
    DEFAULT_DB_PATH = os.path.join(BASE_DIR, "data", "analysis_history.db")


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Creates a connection to the SQLite database."""
    target_path = db_path or DEFAULT_DB_PATH
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initializes the database schema if not already created."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            subject_snippet TEXT,
            sender_domain TEXT,
            classification TEXT NOT NULL,
            confidence REAL NOT NULL,
            risk_level TEXT NOT NULL,
            indicators_json TEXT,
            urls_count INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def sanitize_snippet(text: Optional[str], max_len: int = 80) -> str:
    """Truncates text to prevent storing extensive message content."""
    if not text:
        return "[No Subject Provided]"
    cleaned = " ".join(str(text).split())
    if len(cleaned) > max_len:
        return cleaned[:max_len] + "..."
    return cleaned


def extract_sender_domain(sender: Optional[str]) -> str:
    """Safely extracts domain name from email sender field."""
    if not sender:
        return "Unknown"
    sender_str = str(sender)
    if "@" in sender_str:
        domain = sender_str.split("@")[-1].rstrip(">").strip()
        return domain.lower()
    return "Unknown"


def log_analysis(
    subject: Optional[str],
    sender: Optional[str],
    classification: str,
    confidence: float,
    risk_level: str,
    indicators: List[str],
    urls_count: int = 0,
    db_path: Optional[str] = None
) -> int:
    """
    Logs an analysis event with privacy-conscious metadata.
    """
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    snippet = sanitize_snippet(subject)
    domain = extract_sender_domain(sender)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ind_json = json.dumps(indicators)

    cursor.execute("""
        INSERT INTO scan_history (
            timestamp, subject_snippet, sender_domain, classification,
            confidence, risk_level, indicators_json, urls_count
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (now_str, snippet, domain, classification, round(float(confidence), 4), risk_level, ind_json, urls_count))

    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id


def get_history(
    limit: int = 100,
    classification_filter: Optional[str] = None,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves historical scan records with optional classification filtering.
    """
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    if classification_filter and classification_filter != "All":
        cursor.execute("""
            SELECT id, timestamp, subject_snippet, sender_domain, classification,
                   confidence, risk_level, indicators_json, urls_count
            FROM scan_history
            WHERE classification = ?
            ORDER BY id DESC
            LIMIT ?
        """, (classification_filter, limit))
    else:
        cursor.execute("""
            SELECT id, timestamp, subject_snippet, sender_domain, classification,
                   confidence, risk_level, indicators_json, urls_count
            FROM scan_history
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))

    rows = cursor.fetchall()
    results = []
    for r in rows:
        try:
            indicators = json.loads(r["indicators_json"]) if r["indicators_json"] else []
        except Exception:
            indicators = []

        results.append({
            "id": r["id"],
            "timestamp": r["timestamp"],
            "subject_snippet": r["subject_snippet"],
            "sender_domain": r["sender_domain"],
            "classification": r["classification"],
            "confidence": r["confidence"],
            "risk_level": r["risk_level"],
            "indicators": indicators,
            "urls_count": r["urls_count"]
        })

    conn.close()
    return results


def get_history_stats(db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Computes summary aggregates for the dashboard overview.
    """
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM scan_history")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT classification, COUNT(*) as cnt FROM scan_history GROUP BY classification")
    class_counts = {r["classification"]: r["cnt"] for r in cursor.fetchall()}

    cursor.execute("SELECT AVG(confidence) as avg_conf FROM scan_history")
    row_avg = cursor.fetchone()
    avg_conf = round(row_avg["avg_conf"] * 100, 2) if row_avg and row_avg["avg_conf"] else 0.0

    conn.close()
    return {
        "total_scanned": total,
        "phishing_count": class_counts.get("Likely Phishing", 0),
        "suspicious_count": class_counts.get("Suspicious", 0),
        "legitimate_count": class_counts.get("Likely Legitimate", 0),
        "average_confidence_pct": avg_conf
    }


def clear_history(db_path: Optional[str] = None) -> bool:
    """
    Permanently purges all historical scan entries.
    """
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM scan_history")
    conn.commit()
    conn.close()
    return True
