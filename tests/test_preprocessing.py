"""
Automated Unit Tests: Preprocessing and Text Normalization Module
"""

import os
import sys
import pytest
import pandas as pd

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.preprocessing import clean_text_for_nlp, combine_email_fields, get_stratified_train_test_split


def test_clean_text_basic():
    raw = "Hello World! Please Click Here: https://example.com/login"
    cleaned = clean_text_for_nlp(raw, mask_urls=False)
    assert "hello world!" in cleaned
    assert "https://example.com/login" in cleaned


def test_clean_text_html_stripping():
    html_raw = "<html><body><h3>Alert &amp; Warning</h3><p>Your account &lt;test&gt; is expired.</p></body></html>"
    cleaned = clean_text_for_nlp(html_raw)
    assert "<" not in cleaned
    assert ">" not in cleaned
    assert "alert & warning" in cleaned
    assert "your account" in cleaned
    assert "is expired." in cleaned


def test_clean_text_url_masking():
    raw = "Visit http://phishing.site/verify immediately."
    masked = clean_text_for_nlp(raw, mask_urls=True)
    assert "http_url_token" in masked
    assert "phishing.site" not in masked


def test_combine_email_fields():
    subj = "Security Notice"
    body = "Please review your account."
    res = combine_email_fields(subject=subj, body=body)
    assert res.startswith("Subject: Security Notice")
    assert "Please review your account." in res


def test_get_stratified_train_test_split():
    df = pd.DataFrame({
        "email_text": [f"Email content number {i}" for i in range(100)],
        "label": [1] * 50 + [0] * 50
    })
    X_train, X_test, y_train, y_test = get_stratified_train_test_split(df, test_size=0.20, random_state=42)
    assert len(X_train) == 80
    assert len(X_test) == 20
    assert sum(y_train) == 40
    assert sum(y_test) == 10
