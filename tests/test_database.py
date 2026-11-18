"""
Automated Unit Tests: Analysis History Database and Privacy Controls
"""

import os
import sys
import pytest
import tempfile

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.database import (
    init_db,
    log_analysis,
    get_history,
    get_history_stats,
    clear_history,
    sanitize_snippet,
    extract_sender_domain
)


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_db(path)
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_sanitize_snippet():
    long_text = "A" * 150
    snippet = sanitize_snippet(long_text, max_len=50)
    assert len(snippet) <= 53  # 50 chars + "..."
    assert snippet.endswith("...")


def test_extract_sender_domain():
    assert extract_sender_domain("User <test@example.com>") == "example.com"
    assert extract_sender_domain("admin@portal.org") == "portal.org"
    assert extract_sender_domain(None) == "Unknown"


def test_database_lifecycle(temp_db):
    # Log 2 records
    r1 = log_analysis(
        subject="Urgent Security Alert",
        sender="alert@security-desk.top",
        classification="Likely Phishing",
        confidence=0.98,
        risk_level="High Risk",
        indicators=["Urgent action required", "Suspicious TLD"],
        urls_count=1,
        db_path=temp_db
    )
    r2 = log_analysis(
        subject="Exam Schedule 2026",
        sender="admin@university.edu",
        classification="Likely Legitimate",
        confidence=0.92,
        risk_level="Low Risk",
        indicators=[],
        urls_count=1,
        db_path=temp_db
    )
    assert r1 > 0
    assert r2 > r1

    # Fetch all
    records = get_history(db_path=temp_db)
    assert len(records) == 2
    assert records[0]["classification"] == "Likely Legitimate"  # newest first
    assert records[1]["classification"] == "Likely Phishing"

    # Filter
    phish_only = get_history(classification_filter="Likely Phishing", db_path=temp_db)
    assert len(phish_only) == 1
    assert phish_only[0]["subject_snippet"] == "Urgent Security Alert"

    # Stats
    stats = get_history_stats(db_path=temp_db)
    assert stats["total_scanned"] == 2
    assert stats["phishing_count"] == 1
    assert stats["legitimate_count"] == 1
    assert stats["average_confidence_pct"] == 95.0

    # Clear
    clear_history(db_path=temp_db)
    assert len(get_history(db_path=temp_db)) == 0
