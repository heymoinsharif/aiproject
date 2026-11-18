"""
Automated Unit Tests: Prediction Pipeline and Classification Logic
"""

import os
import sys
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.predict import PhishingDetector
from data.samples import SAMPLE_EMAILS


@pytest.fixture(scope="module")
def detector():
    det = PhishingDetector()
    assert det.is_ready(), "Model artifacts must be present and loaded before running prediction tests."
    return det


def test_detector_phishing_sample(detector):
    sample = SAMPLE_EMAILS["Phishing: Urgent Account Verification"]
    result = detector.analyze_email(
        subject=sample["subject"],
        body=sample["body"],
        sender=sample["sender"],
        urls_input=sample["urls"]
    )
    assert result["classification"] == "Likely Phishing"
    assert result["risk_level"] == "High Risk"
    assert result["phishing_probability"] > 0.50
    assert len(result["observed_indicators"]) > 0
    assert "token_attributions" in result
    assert result["url_analysis"]["total_urls_found"] >= 1


def test_detector_legitimate_sample(detector):
    sample = SAMPLE_EMAILS["Legitimate: Academic Announcement"]
    result = detector.analyze_email(
        subject=sample["subject"],
        body=sample["body"],
        sender=sample["sender"],
        urls_input=sample["urls"]
    )
    assert result["classification"] == "Likely Legitimate"
    assert result["risk_level"] == "Low Risk"
    assert result["legitimate_probability"] > 0.60


def test_detector_output_contract(detector):
    result = detector.analyze_email(
        subject="Hello",
        body="Short message test"
    )
    required_keys = [
        "classification", "risk_level", "verdict_code", "confidence_pct",
        "phishing_probability", "legitimate_probability", "model_used",
        "observed_indicators", "token_attributions", "url_analysis", "disclaimer"
    ]
    for key in required_keys:
        assert key in result, f"Key '{key}' missing from detector output."
    assert result["classification"] in ["Likely Phishing", "Suspicious", "Likely Legitimate"]
