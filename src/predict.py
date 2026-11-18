"""
Inference and Prediction Pipeline Module
Loads pre-trained pipelines, computes calibrated probabilities, applies risk thresholds,
and bundles XAI explanations for user-submitted emails.
"""

import os
import sys
from typing import Dict, Any, Optional, List
import joblib

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.preprocessing import clean_text_for_nlp, combine_email_fields
from src.url_features import analyze_email_urls
from src.explainability import extract_observed_indicators, explain_token_attributions

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")


class PhishingDetector:
    """
    Production inference engine for phishing email detection.
    """
    def __init__(self):
        self.best_pipeline_path = os.path.join(MODELS_DIR, "best_model.joblib")
        self.vectorizer_path = os.path.join(MODELS_DIR, "vectorizer.joblib")
        self.all_models_path = os.path.join(MODELS_DIR, "all_models.joblib")

        self.pipeline = None
        self.vectorizer = None
        self.all_models = {}
        self.best_model_name = "Support Vector Machine (SVM)"
        self.load_artifacts()

    def load_artifacts(self):
        """Loads serialized models from disk."""
        if os.path.exists(self.best_pipeline_path):
            self.pipeline = joblib.load(self.best_pipeline_path)

        if os.path.exists(self.vectorizer_path):
            self.vectorizer = joblib.load(self.vectorizer_path)

        if os.path.exists(self.all_models_path):
            data = joblib.load(self.all_models_path)
            self.all_models = data.get("models", {})
            self.best_model_name = data.get("best_name", "Support Vector Machine (SVM)")

    def is_ready(self) -> bool:
        """Returns True if model pipeline is loaded and ready."""
        return self.pipeline is not None and self.vectorizer is not None

    def analyze_email(
        self,
        subject: str,
        body: str,
        sender: Optional[str] = None,
        urls_input: Optional[str] = None,
        selected_model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyzes supplied email inputs and returns classification, probabilities,
        heuristics, and Explainable AI feature attributions.
        """
        if not self.is_ready():
            raise RuntimeError(
                "Machine learning models are not loaded. Please ensure models/best_model.joblib exists."
            )

        # 1. Combine and clean text
        composite_text = combine_email_fields(subject=subject, body=body, sender=sender)
        cleaned_text = clean_text_for_nlp(composite_text)

        # 2. Offline URL analysis
        additional_urls = [u.strip() for u in (urls_input or "").split() if u.strip()]
        url_report = analyze_email_urls(composite_text, additional_urls=additional_urls)

        # 3. Model selection & inference
        model_name = selected_model if (selected_model and selected_model in self.all_models) else self.best_model_name
        clf = self.all_models.get(model_name)

        if clf is not None and self.vectorizer is not None:
            x_vec = self.vectorizer.transform([cleaned_text])
            probs = clf.predict_proba(x_vec)[0]
            p_legit = float(probs[0])
            p_phish = float(probs[1])
        else:
            # Fallback to pipeline
            probs = self.pipeline.predict_proba([cleaned_text])[0]
            p_legit = float(probs[0])
            p_phish = float(probs[1])
            clf = self.pipeline.named_steps["classifier"]

        # 4. Calibrated Decision Thresholding
        # Classification tiers: Likely Phishing (>= 70%), Suspicious (40-69%), Likely Legitimate (< 40%)
        # Note: If severe URL indicators are triggered (e.g. raw IP host), floor risk to Suspicious
        if p_phish >= 0.70 or (url_report["max_url_risk_score"] >= 0.5 and p_phish >= 0.40):
            classification = "Likely Phishing"
            risk_level = "High Risk"
            verdict_code = "phishing"
            confidence = p_phish
        elif p_phish >= 0.40 or url_report["total_urls_found"] > 0 and url_report["max_url_risk_score"] > 0.3:
            classification = "Suspicious"
            risk_level = "Medium Risk / Requires Review"
            verdict_code = "suspicious"
            confidence = max(p_phish, 0.50)
        else:
            classification = "Likely Legitimate"
            risk_level = "Low Risk"
            verdict_code = "legitimate"
            confidence = p_legit

        # 5. Explainable AI & Indicators
        observed_indicators = extract_observed_indicators(subject=subject, body=body, url_analysis=url_report)
        token_attributions = explain_token_attributions(
            email_text=cleaned_text,
            vectorizer=self.vectorizer,
            classifier=clf
        )

        return {
            "classification": classification,
            "risk_level": risk_level,
            "verdict_code": verdict_code,
            "confidence_pct": round(confidence * 100, 2),
            "phishing_probability": round(p_phish, 4),
            "legitimate_probability": round(p_legit, 4),
            "model_used": model_name,
            "observed_indicators": observed_indicators,
            "token_attributions": token_attributions,
            "url_analysis": url_report,
            "clean_text_preview": cleaned_text[:300] + ("..." if len(cleaned_text) > 300 else ""),
            "disclaimer": (
                "Notice: Predictions are statistical estimates derived from Natural Language Processing "
                "and trained machine learning models. They are intended as an advisory aid and do not constitute "
                "a deterministic guarantee of safety. Absence of suspicious keywords does not ensure benign origin."
            )
        }
