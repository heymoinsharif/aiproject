"""
Dataset Loading, Validation, and Hygiene Module
Handles dataset ingestion, missing value remediation, deduplication, 
label canonicalization, and validation reporting.
"""

import os
import re
from typing import Tuple, Dict, Any, Optional
import pandas as pd
import numpy as np

# Default relative paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DEFAULT_RAW_FILE = os.path.join(DATA_DIR, "CEAS_08.csv")
DEFAULT_PROCESSED_FILE = os.path.join(DATA_DIR, "phishing_emails.csv")


def normalize_label(val: Any) -> Optional[int]:
    """
    Standardize various label encodings into binary 0 (legitimate) or 1 (phishing).
    Returns None if label cannot be confidently mapped.
    """
    if pd.isna(val):
        return None
    val_str = str(val).strip().lower()
    if val_str in ("1", "1.0", "phishing", "phish", "spam", "true", "yes", "fraud"):
        return 1
    if val_str in ("0", "0.0", "legitimate", "safe", "ham", "false", "no"):
        return 0
    return None


def extract_url_count(text: str) -> int:
    """Extract approximate URL count from text using regex."""
    if not isinstance(text, str) or not text:
        return 0
    pattern = r"https?://[^\s<>\"'()]+|www\.[^\s<>\"'()]+"
    return len(re.findall(pattern, text))


def validate_and_clean_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Validates, deduplicates, normalizes, and cleans an input email dataframe.

    Returns:
        cleaned_df: Validated DataFrame with canonical columns
        report: Summary statistics of the data hygiene process
    """
    initial_count = len(df)
    report = {
        "initial_records": initial_count,
        "missing_subject_count": 0,
        "missing_body_count": 0,
        "invalid_label_dropped": 0,
        "duplicates_removed": 0,
        "empty_text_dropped": 0,
        "final_records": 0,
        "phishing_count": 0,
        "legitimate_count": 0,
        "phishing_ratio": 0.0,
    }

    # Case-insensitive column name resolution
    col_map = {c.lower(): c for c in df.columns}
    
    # Identify label column
    label_col = None
    for cand in ["label", "class", "email type", "type", "target", "category"]:
        if cand in col_map:
            label_col = col_map[cand]
            break
            
    if label_col is None:
        raise ValueError(f"Could not find a valid label column in dataset. Available columns: {list(df.columns)}")

    # Identify subject and body columns
    subject_col = col_map.get("subject", None)
    body_col = None
    for cand in ["body", "email text", "text", "message", "content"]:
        if cand in col_map:
            body_col = col_map[cand]
            break

    sender_col = col_map.get("sender", None)
    urls_col = col_map.get("urls", None)

    # 1. Normalize labels
    df["clean_label"] = df[label_col].apply(normalize_label)
    invalid_mask = df["clean_label"].isna()
    report["invalid_label_dropped"] = int(invalid_mask.sum())
    df = df[~invalid_mask].copy()
    df["clean_label"] = df["clean_label"].astype(int)

    # 2. Extract and sanitize text fields
    if subject_col:
        report["missing_subject_count"] = int(df[subject_col].isna().sum())
        clean_subj = df[subject_col].fillna("").astype(str)
    else:
        clean_subj = pd.Series([""] * len(df), index=df.index)

    if body_col:
        report["missing_body_count"] = int(df[body_col].isna().sum())
        clean_body = df[body_col].fillna("").astype(str)
    else:
        clean_body = pd.Series([""] * len(df), index=df.index)

    if sender_col:
        clean_sender = df[sender_col].fillna("Unknown").astype(str)
    else:
        clean_sender = pd.Series(["Unknown"] * len(df), index=df.index)

    # Combined composite text (subject + body)
    composite_text = (clean_subj + " " + clean_body).str.strip()

    # Calculate or extract URLs count
    if urls_col and pd.api.types.is_numeric_dtype(df[urls_col]):
        clean_urls = df[urls_col].fillna(0).astype(int)
    else:
        clean_urls = composite_text.apply(extract_url_count)

    cleaned_df = pd.DataFrame({
        "sender": clean_sender,
        "subject": clean_subj,
        "body": clean_body,
        "email_text": composite_text,
        "urls_count": clean_urls,
        "label": df["clean_label"].values
    })

    # 3. Filter empty text records
    empty_mask = cleaned_df["email_text"].str.len() < 5
    report["empty_text_dropped"] = int(empty_mask.sum())
    cleaned_df = cleaned_df[~empty_mask].copy()

    # 4. Handle duplicates
    before_dedup = len(cleaned_df)
    cleaned_df = cleaned_df.drop_duplicates(subset=["email_text"]).copy()
    report["duplicates_removed"] = before_dedup - len(cleaned_df)

    # 5. Final distribution statistics
    report["final_records"] = len(cleaned_df)
    report["phishing_count"] = int((cleaned_df["label"] == 1).sum())
    report["legitimate_count"] = int((cleaned_df["label"] == 0).sum())
    if report["final_records"] > 0:
        report["phishing_ratio"] = round(report["phishing_count"] / report["final_records"], 4)

    return cleaned_df.reset_index(drop=True), report


def load_dataset(
    filepath: Optional[str] = None, 
    sample_size: Optional[int] = 10000, 
    random_state: int = 42
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Loads and validates the phishing email dataset.
    Prioritizes `data/phishing_emails.csv`, falling back to `data/CEAS_08.csv`.
    """
    target_path = filepath
    if target_path is None:
        if os.path.exists(DEFAULT_PROCESSED_FILE):
            target_path = DEFAULT_PROCESSED_FILE
        elif os.path.exists(DEFAULT_RAW_FILE):
            target_path = DEFAULT_RAW_FILE
        else:
            raise FileNotFoundError(
                f"No dataset found at '{DEFAULT_PROCESSED_FILE}' or '{DEFAULT_RAW_FILE}'.\n"
                "Please run data ingestion or check data/README.md for dataset setup."
            )

    df_raw = pd.read_csv(target_path, low_memory=False)
    cleaned_df, report = validate_and_clean_data(df_raw)

    if sample_size and len(cleaned_df) > sample_size:
        # Stratified sampling to preserve realistic class distribution
        from sklearn.model_selection import train_test_split
        cleaned_df, _ = train_test_split(
            cleaned_df,
            train_size=sample_size,
            stratify=cleaned_df["label"],
            random_state=random_state
        )
        cleaned_df = cleaned_df.reset_index(drop=True)
        report["sampled_benchmark_size"] = len(cleaned_df)

    return cleaned_df, report


def prepare_benchmark_csv(
    raw_path: str = DEFAULT_RAW_FILE,
    output_path: str = DEFAULT_PROCESSED_FILE,
    sample_size: Optional[int] = 10000,
    random_state: int = 42
) -> str:
    """
    Cleans raw CEAS_08 dataset and writes a benchmark CSV for fast, reproducible training.
    """
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Source raw dataset not found at {raw_path}")

    print(f"Loading raw dataset from {raw_path}...")
    df_raw = pd.read_csv(raw_path, low_memory=False)
    cleaned_df, report = validate_and_clean_data(df_raw)

    if sample_size and len(cleaned_df) > sample_size:
        print(f"Sampling {sample_size} records using stratified sampling...")
        from sklearn.model_selection import train_test_split
        cleaned_df, _ = train_test_split(
            cleaned_df,
            train_size=sample_size,
            stratify=cleaned_df["label"],
            random_state=random_state
        )
        cleaned_df = cleaned_df.reset_index(drop=True)

    cleaned_df.to_csv(output_path, index=False)
    print(f"Saved benchmark dataset to {output_path} ({len(cleaned_df)} records).")
    print(f"Hygiene report: {report}")
    return output_path


if __name__ == "__main__":
    prepare_benchmark_csv()
