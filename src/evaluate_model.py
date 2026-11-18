"""
Model Evaluation and Metrics Module
Calculates performance metrics, confusion matrices, ROC/PR curves,
and structures empirical answers for research questions RQ1 through RQ4.
"""

from typing import Dict, Any, List
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    roc_curve,
    precision_recall_curve
)


def compute_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: np.ndarray = None
) -> Dict[str, Any]:
    """
    Computes key classification metrics with 4-decimal precision.
    """
    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))

    roc_auc = None
    if y_prob is not None:
        try:
            roc_auc = float(roc_auc_score(y_true, y_prob))
        except Exception:
            roc_auc = None

    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = [int(v) for v in cm.ravel()]

    fp_rate = float(round(fp / (fp + tn), 4)) if (fp + tn) > 0 else 0.0
    fn_rate = float(round(fn / (fn + tp), 4)) if (fn + tp) > 0 else 0.0

    return {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "roc_auc": round(roc_auc, 4) if roc_auc is not None else None,
        "confusion_matrix": {
            "tn": tn,
            "fp": fp,
            "fn": fn,
            "tp": tp,
            "matrix": cm.tolist()
        },
        "false_positive_rate": fp_rate,
        "false_negative_rate": fn_rate
    }


def compute_curve_points(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    max_samples: int = 80
) -> Dict[str, Any]:
    """
    Computes downsampled ROC and Precision-Recall curve coordinates for JSON serialization.
    """
    if y_prob is None:
        return {"roc": None, "pr": None}

    # ROC Curve
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    if len(fpr) > max_samples:
        indices = np.linspace(0, len(fpr) - 1, max_samples, dtype=int)
        fpr_sampled = fpr[indices].tolist()
        tpr_sampled = tpr[indices].tolist()
    else:
        fpr_sampled = fpr.tolist()
        tpr_sampled = tpr.tolist()

    # Precision-Recall Curve
    prec, rec, _ = precision_recall_curve(y_true, y_prob)
    if len(rec) > max_samples:
        indices = np.linspace(0, len(rec) - 1, max_samples, dtype=int)
        rec_sampled = rec[indices].tolist()
        prec_sampled = prec[indices].tolist()
    else:
        rec_sampled = rec.tolist()
        prec_sampled = prec.tolist()

    return {
        "roc": {
            "fpr": [round(float(x), 4) for x in fpr_sampled],
            "tpr": [round(float(x), 4) for x in tpr_sampled]
        },
        "pr": {
            "recall": [round(float(x), 4) for x in rec_sampled],
            "precision": [round(float(x), 4) for x in prec_sampled]
        }
    }


def analyze_tradeoffs(cm_data: Dict[str, int]) -> Dict[str, str]:
    """
    Provides educational analysis explaining FP vs FN cybersecurity trade-offs.
    """
    tn = cm_data["tn"]
    fp = cm_data["fp"]
    fn = cm_data["fn"]
    tp = cm_data["tp"]

    return {
        "false_positive_impact": (
            f"Observed {fp} False Positives. A False Positive occurs when a legitimate business or "
            "academic email is erroneously quarantined as phishing. Impact: user annoyance, potential "
            "missed critical communications, and operational friction."
        ),
        "false_negative_impact": (
            f"Observed {fn} False Negatives. A False Negative occurs when a genuine phishing email bypasses "
            "the filter and enters the user's inbox. Impact: severe security breach, credential harvesting, "
            "ransomware deployment, or unauthorized financial transactions."
        ),
        "accuracy_paradox_explanation": (
            "Accuracy measures total correct predictions over total emails. However, if a dataset were 95% legitimate "
            "and 5% phishing, a naive model predicting 'Legitimate' for every email would achieve 95% accuracy while "
            "completely failing to stop any cyberattacks (0% recall). Therefore, F1-Score, Precision, and Recall "
            "are essential metrics in cybersecurity evaluation."
        )
    }
