# AI-Powered Phishing Email Detection System Using Machine Learning and NLP

![System Banner](https://img.shields.io/badge/Status-Operational-10b981?style=for-the-badge&logo=shield)
![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12-38bdf8?style=for-the-badge&logo=python)
![Framework](https://img.shields.io/badge/Streamlit-1.40+-ef4444?style=for-the-badge&logo=streamlit)
![ML Library](https://img.shields.io/badge/Scikit--Learn-1.3+-f59e0b?style=for-the-badge&logo=scikitlearn)
![Academic Level](https://img.shields.io/badge/Academic-3rd%20Year%20CSE%20Capstone-6366f1?style=for-the-badge)

An academic, production-grade cybersecurity application that detects social engineering and credential-harvesting phishing emails in real time. Built with **Scikit-learn**, **Natural Language Processing (TF-IDF)**, **Explainable AI (XAI)**, and an interactive **Streamlit Security Operations Center (SOC)** dashboard.

---

## 1. Project Overview
Phishing attacks are responsible for over 90% of organizational data breaches. This project implements a machine learning system that analyzes email textual content, extracts offline structural URL indicators, calibrates prediction probabilities across four distinct algorithms, and provides transparent feature attribution explaining *why* an email was classified as a threat.

### Key Highlights
- **Real ML Pipeline:** Four algorithms (Multinomial Naive Bayes, Logistic Regression, Random Forest, Calibrated Linear SVM) trained with 5-Fold Stratified Cross-Validation on the CEAS 2008 benchmark corpus (10,000 emails).
- **Calibrated Three-Tier Verdicts:** Classifies emails into `Likely Phishing`, `Suspicious`, and `Likely Legitimate` with calibrated confidence probabilities.
- **Explainable AI (XAI):** Features linear model coefficient attribution (salient positive and negative n-grams) and deterministic cybersecurity heuristic indicators.
- **Zero-Network Safe URL Scanner:** Safely analyzes URLs for raw IP hosts, shortening services, excessive subdomains, and obfuscated encoding completely offline.
- **Privacy by Design:** Employs an embedded SQLite database storing only truncated subject snippets and metadata. Message bodies, credentials, and passwords are never persisted.
- **Academic Rigor:** Investigates four formal research questions (RQ1–RQ4), addressing the Accuracy Paradox in imbalanced cybersecurity datasets.

---

## 2. Problem Statement
Traditional email security filters rely heavily on static blacklists and rigid regular expressions. Attackers routinely bypass these defenses by mutating domain names, using raw IP hosts, leveraging legitimate URL shorteners, and employing persuasive psychological triggers (urgency, fear of account suspension). There is an urgent need for adaptive machine learning models that assess semantic and structural indicators rather than static keyword matching alone.

---

## 3. Motivation
In cybersecurity, false predictions carry asymmetric consequences:
- A **False Negative** allows an attacker into the corporate network, risking credential harvesting or ransomware deployment.
- A **False Positive** quaranatines legitimate business communications, creating operational friction.
By combining statistical NLP vectorization with structured security heuristics, this project delivers high recall while maintaining explainability to prevent analyst fatigue.

---

## 4. Objectives
1. Implement a complete, end-to-end Python machine learning pipeline with zero data leakage.
2. Train and benchmark four candidate algorithms using 5-Fold Stratified Cross-Validation.
3. Compare text-only feature representations against hybrid representations (text + structured URL features) to answer RQ3.
4. Provide Explainable AI (XAI) feature attributions indicating the specific tokens driving predictions.
5. Create an interactive multi-page SOC dashboard suitable for project viva demonstrations.

---

## 5. Existing Approaches vs. Proposed Methodology

| Characteristic | Traditional Blacklists / Heuristics | Deep Learning / LLM APIs | Proposed ML + NLP Architecture |
|---|---|---|---|
| **Zero-Day Attack Detection** | Fails (relies on known bad signatures) | High | **High (evaluates semantic n-grams & syntax)** |
| **Data Privacy & Leakage** | Local lookup | High risk (transmits emails to external cloud) | **100% Local execution (zero network egress)** |
| **Inference Latency** | Sub-millisecond | Slow (1,000–3,000 ms) | **Fast (0.002–0.05 ms per email)** |
| **Explainability** | Hardcoded rule IDs | Black box (low interpretability) | **Transparent (linear token weights + heuristics)** |
| **Resource Footprint** | Negligible | Requires dedicated GPU/VRAM | **Lightweight CPU footprint (< 50MB RAM)** |

---

## 6. System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION TIER (UI)                          │
│               Streamlit Multi-Page Cybersecurity SOC                   │
│   ├── app.py (SOC Dashboard & Real-Time KPIs)                          │
│   ├── pages/1_Analyze_Email.py (Inspector, Samples & XAI)              │
│   ├── pages/2_Model_Evaluation.py (ROC/PR Curves, CMs & RQ1-RQ4)       │
│   ├── pages/3_Dataset_Information.py (Hygiene, Leakage Prevention)     │
│   ├── pages/4_Analysis_History.py (SQLite Audit Log & Purge)           │
│   └── pages/5_About_Project.py (Methodology & Academic Defense)        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ User Inputs (Subject, Body, URLs)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      PREPROCESSING & HYGIENE                           │
│   • HTML entity decoding & tag removal                                 │
│   • Whitespace normalization & lowercase folding                       │
│   • Stratified 80/20 train/test isolation (Leakage Prevention)         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Clean Text Representation
                     ┌──────────────┴──────────────┐
                     ▼                             ▼
┌────────────────────────────┐       ┌───────────────────────────┐
│     FEATURE EXTRACTION     │       │    OFFLINE URL SCANNER    │
│ • TF-IDF (1,2 N-Grams)     │       │ • Regex IP Host Detection │
│ • 5,000 vocabulary size    │       │ • Shortener Domain Match  │
│ • SecurityFeatureExtractor │       │ • Subdomain Layering      │
└────────────┬───────────────┘       └─────────────┬─────────────┘
             │ Vector (Sparse CSR)                 │ Heuristic Flags
             ▼                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     MACHINE LEARNING INFERENCE                         │
│ • Calibrated Linear SVM (Platt scaling via CalibratedClassifierCV)     │
│ • Outputs P(Phishing) and P(Legitimate) probabilities                  │
│ • Maps to 3 Tiers: Likely Phishing / Suspicious / Likely Legitimate    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     ▼                             ▼
┌────────────────────────────┐       ┌───────────────────────────┐
│     EXPLAINABLE AI (XAI)   │       │   AUDIT DATABASE (SQLite) │
│ • Token impact: W_i * TFIDF│       │ • Lightweight metadata    │
│ • Observed heuristic tags  │       │ • Purge on demand         │
└────────────────────────────┘       └───────────────────────────┘
```

---

## 7. Dataset Acquisition & Provenance
The model is trained on the peer-reviewed **CEAS 2008 (Collaboration to Evaluate Advanced Spamanalyses)** benchmark corpus, mirroring real enterprise email traffic.

- **Primary Source:** CEAS 2008 Spam Conference Challenge Archive
- **Corpus Characteristics:** 39,154 raw emails (21,842 Phishing, 17,312 Legitimate)
- **Benchmark Partition:** 10,000 stratified, deduplicated emails stored in `data/phishing_emails.csv`
- **Data Hygiene Pipeline:** Missing fields are safely handled; exact duplicate template messages are purged; vectorizers are fitted **strictly on the training partition**.

To regenerate or re-verify the dataset locally:
```powershell
python phishing-email-detector/src/data_loader.py
```

---

## 8. Installation Instructions

### Prerequisites
- Python 3.11 or 3.12 installed on Windows, macOS, or Linux.
- Git (optional, for repository management).

### Windows Quick Start
1. Make sure the project includes `models/best_model.joblib` and `models/vectorizer.joblib`.
2. Double-click `run_app.bat`.
3. On first launch, the script creates a local `.venv`, installs the requirements, and opens the full-stack web application at `http://127.0.0.1:8000` (Landing Page at `/` and Complete SOC Workspace at `/app`).
4. To run the optional legacy Streamlit interface instead, double-click `run_streamlit.bat` (`http://localhost:8501`).

The first launch needs an internet connection to install Python packages. Later launches reuse the local environment. To update dependencies after changing `requirements.txt`, run:
```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Manual Setup (Windows, macOS, or Linux)
1. Navigate to the project directory:
   ```powershell
   cd "c:\Users\MOIN SHARIF\Desktop\internship\phishing-email-detector"
   ```
2. Create and activate a virtual environment, then install dependencies:
   ```powershell
  python -m venv .venv
  .venv\Scripts\activate
   python -m pip install -r requirements.txt
   ```
  On macOS or Linux, activate with `source .venv/bin/activate` instead.

---

## 9. Training Pipeline Execution
To train all four algorithms, execute 5-fold cross-validation, run the RQ3 and RQ4 experiments, and save all model artifacts:

```powershell
python src/train_model.py
```

Expected output:
```
============================================================
AI-POWERED PHISHING DETECTION: TRAINING PIPELINE INITIATED
============================================================
[Step 1/6] Loading benchmark dataset (target sample size: 10000)...
Dataset loaded: 10000 records. Phishing: 5577, Legitimate: 4423
[Step 2/6] Performing Stratified Train/Test Split (80% Train, 20% Test)...
[Step 3/6] Fitting TF-IDF Vectorizer on training data...
[Step 4/6] Running 5-Fold Stratified Cross-Validation & Test Evaluation...
--- Training: Multinomial Naive Bayes ---
  Test Accuracy: 0.9575 | Precision: 0.9981 | Recall: 0.9256 | F1: 0.9604
--- Training: Logistic Regression ---
  Test Accuracy: 0.9920 | Precision: 0.9928 | Recall: 0.9928 | F1: 0.9928
--- Training: Random Forest ---
  Test Accuracy: 0.9860 | Precision: 0.9823 | Recall: 0.9928 | F1: 0.9875
--- Training: Support Vector Machine (SVM) ---
  Test Accuracy: 0.9960 | Precision: 0.9964 | Recall: 0.9964 | F1: 0.9964
=> Best Performing Model Selected: Support Vector Machine (SVM) (Test F1: 0.9964)
```

---

## 10. Application Launch Instructions
The project ships as a **complete full-stack web application** (`web_app.py`, powered by Starlette + Uvicorn) featuring:
- **Interactive Animated Landing Page (`/`)**: Built with **GSAP 3 + ScrollTrigger + ScrollSmoother** (smooth scroll, `data-speed` multi-velocity parallax, scrubbed pipeline storytelling, pinned 900° scrubbed Sentinel Windmill SVG, visual marker toggle) and **Anime.js v4** (blended kinetic threat nodes, interactive 13×13 radial stagger matrix, and orientation-aware `createScope` responsive telemetry wave), plus a live instant-scan sandbox.
- **Complete SOC Web Workspace (`/app`)**: Real-time Email Analyzer with all 4 ML classifiers, Explainable AI (XAI) token impact charts, zero-network URL forensics, Model Benchmarks (confusion matrices, SVG ROC/PR curves, RQ1–RQ4), Dataset Hygiene dashboard, and SQLite Audit History.
- **REST API**: `GET /api/health`, `GET /api/stats`, `GET /api/samples`, `POST /api/analyze`, `GET /api/benchmarks`, `GET /api/history`, `DELETE /api/history`.

On Windows, double-click `run_app.bat` to launch immediately, or start from an activated virtual environment:

```powershell
python web_app.py
```

Open `http://127.0.0.1:8000` (Landing Page) or `http://127.0.0.1:8000/app` (SOC Workspace).

*(Optional)* The legacy multi-page Streamlit dashboard also remains available via:

```powershell
python -m streamlit run app.py
```

---

## 11. Automated Test Execution
Run the automated Pytest test suite covering data preprocessing, URL heuristics, inference contracts, database privacy, and full-stack web application routes/APIs:

```powershell
python -m pytest tests/ -v
```

---

## 12. Empirical Model Evaluation Results

Evaluation performed on the held-out test partition (2,000 emails):

| Model Name | 5-Fold CV F1 (Mean ± Std) | Test Accuracy | Test Precision | Test Recall | Test F1-Score | ROC-AUC | Train Time (s) | Inference Latency |
|---|---|---|---|---|---|---|---|---|
| **Support Vector Machine (SVM)** | **0.9935 ± 0.002** | **0.9960** | **0.9964** | **0.9964** | **0.9964** | **0.9998** | 0.814s | 0.005 ms/email |
| **Logistic Regression** | 0.9924 ± 0.002 | 0.9920 | 0.9928 | 0.9928 | 0.9928 | 0.9997 | 0.126s | 0.002 ms/email |
| **Random Forest** | 0.9866 ± 0.003 | 0.9860 | 0.9823 | 0.9928 | 0.9875 | 0.9991 | 1.144s | 0.052 ms/email |
| **Multinomial Naive Bayes** | 0.9556 ± 0.004 | 0.9575 | 0.9981 | 0.9256 | 0.9604 | 0.9992 | 0.007s | 0.002 ms/email |

### Error Breakdown for Best Model (SVM)
- **True Positives (TP):** 1,111 (Phishing emails correctly stopped)
- **True Negatives (TN):** 881 (Legitimate emails correctly delivered)
- **False Positives (FP):** 4 (Legitimate emails quarantined — 0.45% FP Rate)
- **False Negatives (FN):** 4 (Phishing emails missed — 0.36% FN Rate)

---

## 13. Research Questions & Academic Findings

### RQ1: Algorithm Comparison
> **Finding:** Linear models (Calibrated SVM and Logistic Regression) outperform ensemble trees and Naive Bayes in high-dimensional sparse TF-IDF spaces. SVM achieved an optimal F1-score of 0.9964 with 0.005 ms inference latency.

### RQ2: Metric Strengths & The Accuracy Paradox
> **Finding:** In operational cybersecurity, accuracy is a misleading metric. In an environment where only 2% of emails are malicious, a dummy model predicting 'benign' achieves 98% accuracy while failing against 100% of attacks. Therefore, **Recall** (catching attacks) and **Precision** (avoiding false alarms) balanced via **F1-Score** provide the authentic evaluation benchmark.

### RQ3: Text-Only vs. Hybrid Feature Architecture
> **Finding:** While text TF-IDF captures vocabulary signals, combining text tokens with structured security indicators (URL counts, IP host patterns, punctuation anomalies, urgency keywords) provides complementary defense against template variations while enabling transparent XAI explanations.

### RQ4: Generalization Across Template Variations
> **Finding:** When tested against brief, minimalist emails (< 250 characters), TF-IDF vocabulary density decreases, showing a slight drop in standalone text confidence. In these scenarios, the offline URL heuristic scanner acts as an indispensable defense layer.

---

## 14. Ethical, Security & Privacy Standards
- **Local Execution:** 100% offline analysis. No email bodies or recipient addresses are sent to third-party APIs.
- **Zero Active Exploitation:** The system never initiates outbound HTTP requests to extracted URLs and never opens attachments.
- **Privacy Preservation:** The database records only truncated subject snippets and summary verdicts; no message bodies or credentials are saved.
- **Honest Disclaimers:** Predictions are statistical advisories and do not replace organizational defense-in-depth controls.

---

## 15. Limitations & Future Work
1. **Transformer LLMs:** Fine-tuning BERT or RoBERTa for contextual semantic understanding of advanced linguistic evasion.
2. **Cryptographic Header Verification:** Adding automated parsing for SPF, DKIM, and DMARC DNS records.
3. **External Threat Feeds:** Optional API connectors for VirusTotal and PhishTank for authenticated threat intelligence verification.
4. **Attachment Sandboxing:** Static file-type entropy analysis for email attachment files.

---

## 16. References
1. **CEAS 2008 Challenge Dataset:** Collaboration to Evaluate Advanced Spamanalyses Conference.
2. **Pedregosa et al.,** *Scikit-learn: Machine Learning in Python*, JMLR 12, pp. 2825-2830, 2011.
3. **Platt, J.,** *Probabilistic Outputs for Support Vector Machines and Comparisons to Regularized Likelihood Methods*, Advances in Large Margin Classifiers, 1999.
4. **Apache SpamAssassin Public Corpus:** The Apache Software Foundation.
