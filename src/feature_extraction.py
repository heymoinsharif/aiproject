"""
Feature Engineering Module
Implements TF-IDF vectorization and a custom scikit-learn compatible
SecurityFeatureExtractor for structured heuristic signals (RQ3).
"""

import re
import numpy as np
from typing import List, Union
import pandas as pd
from scipy.sparse import hstack, csr_matrix
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline
from src.url_features import extract_urls, IPV4_REGEX

# Suspicious keyword dictionaries for behavioral signal extraction
URGENCY_KEYWORDS = [
    r"\burgent\b", r"\bimmediately\b", r"\baction required\b", r"\bwithin 24 hours\b",
    r"\bsuspended\b", r"\baccount suspension\b", r"\bterminate\b", r"\bdeadline\b",
    r"\bfailure to respond\b", r"\bcompromised\b", r"\bsecurity breach\b"
]

CREDENTIAL_KEYWORDS = [
    r"\bverify your account\b", r"\bpassword\b", r"\blogin\b", r"\bcredential\b",
    r"\bupdate your (?:information|profile|details)\b", r"\bconfirm your identity\b",
    r"\bsecurity question\b", r"\bpasscode\b", r"\bpin number\b"
]

FINANCIAL_KEYWORDS = [
    r"\bbank\b", r"\btransfer\b", r"\bwire\b", r"\binvoice\b", r"\bpayment\b",
    r"\brefund\b", r"\bcredit card\b", r"\bpaypal\b", r"\bbitcoin\b", r"\bcrypto\b",
    r"\bclaim your prize\b", r"\blottery\b", r"\bmillion dollars\b"
]

ATTACHMENT_KEYWORDS = [
    r"\battached\b", r"\battachment\b", r"\.zip\b", r"\.exe\b", r"\.scr\b",
    r"\.iso\b", r"\.vbs\b", r"\.docm\b", r"\bdocument attached\b"
]


class SecurityFeatureExtractor(BaseEstimator, TransformerMixin):
    """
    Scikit-learn compatible feature extractor extracting structured numerical
    cybersecurity indicators from raw email text.
    """
    def __init__(self):
        self.feature_names = [
            "num_urls",
            "has_ip_in_url",
            "excessive_punctuation",
            "urgency_score",
            "credential_score",
            "financial_score",
            "attachment_score",
            "uppercase_ratio",
            "log_text_length"
        ]

    def fit(self, X, y=None):
        return self

    def _extract_single(self, text: str) -> List[float]:
        if not isinstance(text, str) or not text:
            return [0.0] * len(self.feature_names)

        # 1. URL extraction & IP host presence
        urls = extract_urls(text)
        num_urls = float(len(urls))
        has_ip = 0.0
        for u in urls:
            m = re.search(r"://([^/:]+)", u)
            if m and IPV4_REGEX.match(m.group(1)):
                has_ip = 1.0
                break

        # 2. Punctuation anomalies (!, ?, $, %)
        punc_count = len(re.findall(r"[!?$%]", text))
        norm_punc = min(10.0, float(punc_count))

        # 3. Urgency signal count
        urgency_count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in URGENCY_KEYWORDS)

        # 4. Credential harvesting signal count
        cred_count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in CREDENTIAL_KEYWORDS)

        # 5. Financial signal count
        fin_count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in FINANCIAL_KEYWORDS)

        # 6. Attachment signal count
        att_count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in ATTACHMENT_KEYWORDS)

        # 7. Uppercase character ratio
        letters = re.findall(r"[a-zA-Z]", text)
        if letters:
            upper_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
        else:
            upper_ratio = 0.0

        # 8. Log text length
        log_len = float(np.log1p(len(text)))

        return [
            num_urls,
            has_ip,
            norm_punc,
            float(urgency_count),
            float(cred_count),
            float(fin_count),
            float(att_count),
            float(round(upper_ratio, 4)),
            float(round(log_len, 4))
        ]

    def transform(self, X):
        features = [self._extract_single(text) for text in X]
        return csr_matrix(np.array(features, dtype=np.float64))

    def get_feature_names_out(self, input_features=None):
        return np.array(self.feature_names)


def build_tfidf_vectorizer(
    max_features: int = 5000,
    ngram_range: tuple = (1, 2)
) -> TfidfVectorizer:
    """
    Constructs a TF-IDF vectorizer configured for email NLP classification.
    """
    return TfidfVectorizer(
        max_features=max_features,
        ngram_range=ngram_range,
        sublinear_tf=True,
        stop_words="english",
        strip_accents="unicode"
    )


def build_hybrid_feature_union(
    max_features: int = 5000,
    ngram_range: tuple = (1, 2)
) -> FeatureUnion:
    """
    Builds a FeatureUnion combining text TF-IDF features with structured security features.
    """
    return FeatureUnion([
        ("tfidf", build_tfidf_vectorizer(max_features=max_features, ngram_range=ngram_range)),
        ("structured", SecurityFeatureExtractor())
    ])
