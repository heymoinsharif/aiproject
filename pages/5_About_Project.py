"""
About Project, Academic Methodology, and Viva Defense Guide
Provides a comprehensive overview of the research problem, system architecture,
NLP/ML algorithms, experimental conclusions, and defense preparation questions.
"""

import os
import sys
import streamlit as st

# Add root directory to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.ui_helpers import apply_cyber_theme, render_header

st.set_page_config(page_title="About Project | AI Phishing Detector", page_icon="🎓", layout="wide")
apply_cyber_theme()

render_header(
    title="Academic Project Overview & Methodology",
    subtitle="Third-Year Computer Science Engineering Capstone Project Documentation",
    badge="CSE CAPSTONE DEFENSE"
)

# Project Header
st.markdown("""
    <div class="cyber-card">
        <h3 style="color: #00d2ff; margin-top: 0;">AI-Powered Phishing Email Detection Using Natural Language Processing and Machine Learning</h3>
        <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.6;">
            Phishing continues to be the primary attack vector for initial unauthorized network access, ransomware infection, 
            and identity credential theft. Traditional signature-based detection systems and static blocklists fail against zero-day 
            phishing lures and polymorphic email templates. This project applies statistical NLP and machine learning algorithms to evaluate 
            semantic text structure, syntactic coercion, and structural URL indicators to detect attacks in real-time.
        </p>
    </div>
""", unsafe_allow_html=True)

# Tabs for Structured Viva Information
viva_tabs = st.tabs([
    "🎯 Objectives & Scope",
    "🏗️ System Architecture",
    "🤖 ML & NLP Pipeline",
    "🔬 Research Questions (RQ1-RQ4)",
    "💡 Viva Defense Q&A",
    "🚀 Future Roadmap"
])

with viva_tabs[0]:
    st.markdown("### 🎯 Project Objectives & Academic Scope")
    st.markdown("""
        1. **Multi-Model Benchmark:** Implement, train, and compare 4 standard machine learning algorithms (Multinomial Naive Bayes, Logistic Regression, Random Forest, Calibrated Linear SVM) on a verified academic corpus.
        2. **Explainable AI (XAI):** Eliminate black-box opacity by extracting model coefficients to show token-level feature attribution and observed security heuristic indicators.
        3. **Safe Offline URL Analysis:** Provide local, zero-network structural feature extraction for URLs (IP hosts, shortening, excessive subdomains) without exposing the host to external threat intelligence beacons.
        4. **Data Leakage Prevention:** Enforce scientific integrity with strict train/test stratification and isolated vocabulary fitting.
        5. **Interactive Cybersecurity SOC Dashboard:** Build a production-grade Streamlit web interface with real-time feedback, sample scenario loaders, and privacy-preserving audit logs.
    """)

with viva_tabs[1]:
    st.markdown("### 🏗️ High-Level System Architecture")
    st.markdown("""
        ```
        ┌────────────────────────────────────────────────────────────────────────┐
        │                         CLIENT APPLICATION TIER                         │
        │               Streamlit Interactive Cybersecurity Dashboard             │
        │    [Analyze Email]   [Model Evaluation]   [Dataset Info]   [History]    │
        └───────────────────────────────────┬────────────────────────────────────┘
                                            │ Raw Inputs (Subject, Body, URLs)
                                            ▼
        ┌────────────────────────────────────────────────────────────────────────┐
        │                       PREPROCESSING & HYGIENE TIER                     │
        │ • HTML entity decoding & tag sanitization                              │
        │ • Lowercase normalization & punctuation preservation                   │
        │ • Stratified isolation (Zero data leakage across partitions)           │
        └───────────────────────────────────┬────────────────────────────────────┘
                                            │ Clean Text & Tokens
                     ┌──────────────────────┴──────────────────────┐
                     ▼                                             ▼
        ┌────────────────────────────┐               ┌───────────────────────────┐
        │    FEATURE ENGINEERING     │               │    OFFLINE URL SCANNER    │
        │ • TF-IDF (1,2 N-Grams)     │               │ • IP host regex checks    │
        │ • Sublinear TF scaling     │               │ • Shortener recognition   │
        │ • SecurityFeatureExtractor │               │ • Subdomain depth count   │
        └────────────┬───────────────┘               └─────────────┬─────────────┘
                     │ High-Dimensional Vector                     │ Indicators
                     ▼                                             ▼
        ┌────────────────────────────────────────────────────────────────────────┐
        │                       MACHINE LEARNING INFERENCE                       │
        │   Support Vector Machine (Calibrated) / Logistic Regression            │
        │   ──► Calibrated Probability P(Phishing) & P(Legitimate)               │
        │   ──► 3-Tier Risk Verdict: Likely Phishing / Suspicious / Legitimate   │
        └───────────────────────────────────┬────────────────────────────────────┘
                                            │
                     ┌──────────────────────┴──────────────────────┐
                     ▼                                             ▼
        ┌────────────────────────────┐               ┌───────────────────────────┐
        │      EXPLAINABLE AI        │               │     AUDIT DATABASE        │
        │ • Linear token impact      │               │ • SQLite scan history     │
        │ • Heuristic pattern tags   │               │ • Privacy: No bodies saved│
        └────────────────────────────┘               └───────────────────────────┘
        ```
    """)

with viva_tabs[2]:
    st.markdown("### 🤖 Machine Learning & NLP Pipeline Details")
    st.markdown("""
        - **Term Frequency-Inverse Document Frequency (TF-IDF):** Reflects how important a word or bigram is to a message in the collection. Sublinear TF scaling (`1 + log(tf)`) prevents common words from dominating.
        - **Algorithms Evaluated:**
          1. **Multinomial Naive Bayes (MNB):** Probabilistic classifier utilizing Bayes' Theorem with strong independence assumptions. Extremely fast, but sensitive to word co-occurrence correlations.
          2. **Logistic Regression (LR):** Parametric linear model with balanced class weighting. Solves the convex cross-entropy loss function. Produces natural log-odds probabilities.
          3. **Random Forest (RF):** Ensemble of decision trees trained on bootstrapped subsets with random feature splits. Highly resistant to overfitting, but larger model footprint.
          4. **Support Vector Machine (SVM):** Constructs an optimal hyper-plane maximizing the margin between phishing and benign vectors in high-dimensional space. Wrapped in Platt calibration (`CalibratedClassifierCV`) to output well-calibrated probabilities.
    """)

with viva_tabs[3]:
    st.markdown("### 🔬 Summary of Research Questions (RQ1 – RQ4)")
    st.markdown("""
        - **RQ1 (Model Comparison):** Linear models (SVM and Logistic Regression) consistently outperform tree ensembles and Naive Bayes in high-dimensional sparse TF-IDF spaces, achieving F1-scores exceeding 99% with sub-millisecond inference latency.
        - **RQ2 (Evaluation Metrics):** Accuracy suffers from the *Accuracy Paradox* on imbalanced distributions. In email security, **Recall** is prioritized to minimize catastrophic False Negatives, while **Precision** prevents alert fatigue. F1-score balances both.
        - **RQ3 (Hybrid Feature Value):** Combining unstructured TF-IDF text with structured behavioral indicators (URL counts, urgency keywords, punctuation anomalies) equips the model with robust defense against template variations while powering transparent XAI.
        - **RQ4 (Out-of-Distribution Generalization):** Atypical short emails with sparse text provide fewer n-grams for TF-IDF matching, where hybrid heuristics and URL structure analysis provide critical safety nets.
    """)

with viva_tabs[4]:
    st.markdown("### 💡 Frequently Asked Viva Defense Questions")
    st.markdown("""
        **Q1: Why did you calibrate the Support Vector Machine?**  
        *Answer:* Standard Linear SVM outputs uncalibrated signed distances from the separating hyper-plane (`decision_function`). By wrapping the estimator with `CalibratedClassifierCV` using Platt scaling (sigmoid calibration), the system produces true, calibrated probabilities representing genuine confidence scores.

        **Q2: How did you ensure your model does not suffer from data leakage?**  
        *Answer:* We performed an 80/20 stratified split on the raw email corpus *before* any feature extraction occurred. The TF-IDF vectorizer and all transformers were fitted strictly on the 8,000 training emails. Test emails were evaluated solely by transforming against the fixed vocabulary.

        **Q3: Why doesn't your URL scanner make live DNS or HTTP requests?**  
        *Answer:* In real-world security operations, opening or pinging an untrusted attacker-controlled URL can trigger unique tracking tokens (confirming the email address was active), execute malicious web payloads, or alert the adversary. Our offline feature extraction evaluates URL structure safely and 100% locally.

        **Q4: What is the Accuracy Paradox in cybersecurity?**  
        *Answer:* If 99% of emails are benign and 1% are malicious, a dummy classifier predicting 'benign' for all inputs achieves 99% accuracy while permitting 100% of cyberattacks to penetrate. Hence, Recall and F1-score are the authentic metrics.
    """)

with viva_tabs[5]:
    st.markdown("### 🚀 Limitations and Future Work")
    st.markdown("""
        1. **Transformer LLMs (BERT / RoBERTa):** Fine-tuning contextual transformer models for contextual sentence embeddings.
        2. **Protocol Header Cryptography:** Integrating SPF, DKIM, and DMARC DNS verification checks.
        3. **Live Threat Intelligence Feeds:** Integration with VirusTotal, PhishTank, and URLhaus APIs for verified external reputation lookups.
        4. **Multi-Modal Attachment Sandboxing:** Safe static file-type parsing and entropy analysis of email attachments.
    """)
