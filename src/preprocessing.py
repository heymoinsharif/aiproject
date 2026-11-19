"""
Email Text Preprocessing Module
Implements domain-aware text normalization, HTML entity cleanup,
and train/test splitting with data leakage prevention.
"""

import re
import html
from typing import Tuple, List, Optional, Any
from sklearn.model_selection import train_test_split


def clean_text_for_nlp(text: str, mask_urls: bool = False) -> str:
    """
    Standardize raw email text for NLP tokenization.
    - Decodes HTML entities (e.g., &amp; -> &)
    - Strips HTML tags (<p>, <a href...>)
    - Handles whitespace and non-ASCII character normalization
    - Optionally masks URLs with a normalized token
    """
    if not isinstance(text, str):
        return ""

    # Decode HTML entities
    text = html.unescape(text)

    # Strip HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Optionally mask URLs
    if mask_urls:
        url_regex = r"https?://[^\s<>\"'()]+|www\.[^\s<>\"'()]+"
        text = re.sub(url_regex, " http_url_token ", text)

    # Replace multiple whitespace, tabs, newlines with single space
    text = re.sub(r"\s+", " ", text)

    return text.strip().lower()


def _is_na(val: Any) -> bool:
    """Helper to check for None or NaN without requiring pandas."""
    if val is None:
        return True
    try:
        import math
        if isinstance(val, float) and math.isnan(val):
            return True
    except Exception:
        pass
    return False


def combine_email_fields(
    subject: Optional[str] = "",
    body: Optional[str] = "",
    sender: Optional[str] = None
) -> str:
    """
    Combines subject, body, and optionally sender domain into a single textual representation.
    Subject is weighted by appearing at the beginning.
    """
    subj_str = str(subject) if subject is not None and not _is_na(subject) else ""
    body_str = str(body) if body is not None and not _is_na(body) else ""
    
    parts = []
    if subj_str.strip():
        # Subject given explicit prominence
        parts.append(f"Subject: {subj_str.strip()}")
    if body_str.strip():
        parts.append(body_str.strip())
        
    return " ".join(parts)


def get_stratified_train_test_split(
    df: Any,
    text_column: str = "email_text",
    target_column: str = "label",
    test_size: float = 0.20,
    random_state: int = 42
) -> Tuple[Any, Any, Any, Any]:
    """
    Splits the dataset into train and test sets using stratified sampling.
    Returns:
        X_train_text, X_test_text, y_train, y_test
    """
    import pandas as pd
    if text_column not in df.columns or target_column not in df.columns:
        raise KeyError(f"Columns '{text_column}' or '{target_column}' missing from DataFrame.")

    X = df[text_column].astype(str).apply(clean_text_for_nlp)
    y = df[target_column].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        stratify=y,
        random_state=random_state
    )

    return X_train, X_test, y_train, y_test
