"""
Automated Unit Tests: Feature Extraction and URL Security Heuristics
"""

import os
import sys
import pytest
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.url_features import extract_urls, analyze_url, analyze_email_urls
from src.feature_extraction import SecurityFeatureExtractor, build_tfidf_vectorizer, build_hybrid_feature_union


def test_extract_urls():
    text = "Visit http://malicious-domain.com/login and https://bit.ly/3xSample for verification."
    urls = extract_urls(text)
    assert len(urls) == 2
    assert "http://malicious-domain.com/login" in urls
    assert "https://bit.ly/3xSample" in urls


def test_analyze_url_ip_host():
    ip_url = "http://192.168.1.105/login.php"
    analysis = analyze_url(ip_url)
    assert analysis["has_ip_host"] is True
    assert analysis["risk_score"] > 0.3
    assert any("raw IP address" in flag for flag in analysis["flags"])


def test_analyze_url_shortener():
    short_url = "https://bit.ly/3abc123"
    analysis = analyze_url(short_url)
    assert analysis["is_shortener"] is True
    assert any("shortening service" in flag for flag in analysis["flags"])


def test_analyze_url_suspicious_tld():
    tld_url = "https://banking-secure-portal.top/account"
    analysis = analyze_url(tld_url)
    assert analysis["tld"] == "top"
    assert any(".top" in flag for flag in analysis["flags"])


def test_security_feature_extractor():
    texts = [
        "URGENT: Verify your password immediately at http://192.168.1.1/login or your account will be suspended!!",
        "Hello, this is the regular meeting notes for tomorrow."
    ]
    extractor = SecurityFeatureExtractor()
    features = extractor.transform(texts)
    
    # 2 samples, 9 engineered features
    assert features.shape == (2, 9)
    dense = features.toarray()
    
    # First sample has 1 url, IP host, urgency, credential keyword, high punctuation
    assert dense[0, 0] >= 1.0  # num_urls
    assert dense[0, 1] == 1.0  # has_ip_in_url
    assert dense[0, 3] >= 1.0  # urgency
    assert dense[0, 4] >= 1.0  # credential

    # Second sample is clean
    assert dense[1, 0] == 0.0
    assert dense[1, 1] == 0.0


def test_build_tfidf_vectorizer():
    corpus = [
        "This is an urgent phishing email with sensitive verification details.",
        "Here are the meeting notes for the departmental seminar."
    ]
    vec = build_tfidf_vectorizer(max_features=100)
    X = vec.fit_transform(corpus)
    assert X.shape[0] == 2
    assert X.shape[1] > 5
