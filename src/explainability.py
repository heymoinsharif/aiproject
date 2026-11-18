"""
Explainable AI (XAI) and Security Indicators Module
Generates human-interpretable explanations by coupling statistical token attribution
(model coefficients) with deterministic cybersecurity heuristic patterns.
"""

import re
from typing import Dict, Any, List, Optional
import numpy as np
from src.url_features import analyze_email_urls

# Pattern definitions for transparent indicator matching
SUSPICIOUS_HEURISTIC_RULES = [
    {
        "category": "Urgency & Account Suspension",
        "description": "Urgent timeline or threat of account suspension detected",
        "pattern": r"\b(?:within\s+\d+\s+hours|immediately|account\s+(?:suspended|termination|closed|disabled)|action\s+required|urgent\s+notice)\b",
        "severity": "High"
    },
    {
        "category": "Credential Harvesting",
        "description": "Solicitation of passwords, login credentials, or security passcodes",
        "pattern": r"\b(?:verify\s+your\s+(?:account|identity|password)|enter\s+your\s+passcode|update\s+your\s+credentials|login\s+to\s+restore)\b",
        "severity": "Critical"
    },
    {
        "category": "Financial Demands",
        "description": "Unscheduled invoice, overdue payment, or wire transfer demand",
        "pattern": r"\b(?:invoice\s+overdue|wire\s+transfer|bitcoin|crypto\s+payment|declined\s+card|late\s+penal\s+fees|claim\s+your\s+prize)\b",
        "severity": "Medium"
    },
    {
        "category": "Suspicious Attachment Reference",
        "description": "Reference to executable, archive, or macro-enabled attachments",
        "pattern": r"\b(?:see\s+attached|\.zip\b|\.exe\b|\.scr\b|\.iso\b|\.vbs\b|open\s+the\s+attachment)\b",
        "severity": "High"
    },
    {
        "category": "Generic Greeting Anomaly",
        "description": "Impersonal or vague greeting often characteristic of bulk phishing",
        "pattern": r"^(?:dear\s+(?:valued\s+customer|member|user|client|sir/madam)|attention\s+beneficiary)",
        "severity": "Low"
    }
]


def extract_observed_indicators(
    subject: str,
    body: str,
    url_analysis: Optional[Dict[str, Any]] = None
) -> List[Dict[str, str]]:
    """
    Identifies deterministic security indicators observed in the email.
    Explicitly marked as 'Observed Empirical Indicators'.
    """
    composite = f"{subject} {body}"
    detected = []

    # 1. Text Heuristics
    for rule in SUSPICIOUS_HEURISTIC_RULES:
        matches = re.findall(rule["pattern"], composite, re.IGNORECASE)
        if matches:
            detected.append({
                "type": "Observed Heuristic",
                "category": rule["category"],
                "severity": rule["severity"],
                "description": rule["description"],
                "evidence": f"Matched terms: '{', '.join(set(matches[:3]))}'"
            })

    # 2. URL Heuristics (Offline static indicators)
    if url_analysis and url_analysis.get("aggregated_flags"):
        for flag in url_analysis["aggregated_flags"]:
            detected.append({
                "type": "Observed URL Pattern",
                "category": "URL Structure Anomaly",
                "severity": "High" if "IP address" in flag or "@" in flag else "Medium",
                "description": flag,
                "evidence": "Offline URL structural heuristic (No external reputation query)"
            })

    return detected


def explain_token_attributions(
    email_text: str,
    vectorizer,
    classifier,
    top_n: int = 6
) -> Dict[str, Any]:
    """
    Calculates feature attribution scores for words present in the email using
    the model's learned coefficients (Logistic Regression or Linear SVM).
    """
    try:
        # Determine base estimator if wrapped in calibration
        base_clf = classifier
        if hasattr(classifier, "calibrated_classifiers_"):
            base_clf = classifier.calibrated_classifiers_[0].estimator
        elif hasattr(classifier, "estimator"):
            base_clf = classifier.estimator

        if not hasattr(base_clf, "coef_"):
            return {
                "supported": False,
                "reason": "Classifier does not expose linear feature weights (e.g., Tree ensemble)."
            }

        coefs = base_clf.coef_.ravel()
        feature_names = np.array(vectorizer.get_feature_names_out())

        # Transform single email
        x_vec = vectorizer.transform([email_text])
        non_zero_indices = x_vec.nonzero()[1]

        if len(non_zero_indices) == 0:
            return {
                "supported": True,
                "phishing_tokens": [],
                "legitimate_tokens": [],
                "note": "No recognizable vocabulary tokens found in input text."
            }

        # Calculate contributions: tfidf_weight * model_coefficient
        contributions = []
        for idx in non_zero_indices:
            term = feature_names[idx]
            tfidf_val = x_vec[0, idx]
            weight = coefs[idx]
            impact = tfidf_val * weight
            contributions.append({
                "token": term,
                "impact": float(impact),
                "weight": float(weight),
                "tfidf": float(tfidf_val)
            })

        # Sort by impact
        phishing_tokens = sorted([c for c in contributions if c["impact"] > 0], key=lambda x: x["impact"], reverse=True)[:top_n]
        legitimate_tokens = sorted([c for c in contributions if c["impact"] < 0], key=lambda x: x["impact"])[:top_n]

        return {
            "supported": True,
            "phishing_tokens": phishing_tokens,
            "legitimate_tokens": legitimate_tokens,
            "explanation_method": "Linear Model Coefficient Attribution (TF-IDF Weight × Learned Parameter)"
        }
    except Exception as e:
        return {
            "supported": False,
            "reason": f"Feature attribution error: {str(e)}"
        }
