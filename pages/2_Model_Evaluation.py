"""
Model Evaluation and Comparative Research Dashboard
Displays empirical metrics, confusion matrices, ROC/PR curves,
trade-off analyses (FP vs FN), and research question findings (RQ1 - RQ4).
"""

import os
import sys
import json
import streamlit as st
import pandas as pd
import plotly.express as px

# Add root directory to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.ui_helpers import (
    apply_cyber_theme,
    render_header,
    plot_confusion_matrix,
    plot_roc_curves,
    plot_pr_curves
)

st.set_page_config(page_title="Model Evaluation | AI Phishing Detector", page_icon="📈", layout="wide")
apply_cyber_theme()

render_header(
    title="Comparative Model Evaluation & Benchmarking",
    subtitle="Empirical evaluation across 4 machine learning classifiers trained on verified benchmark data",
    badge="ACADEMIC BENCHMARK & RESEARCH QUESTIONS"
)

# Load real evaluation metadata
results_path = os.path.join(PROJECT_ROOT, "models", "evaluation_results.json")
if not os.path.exists(results_path):
    st.error("⚠️ Evaluation results not found. Please run the training pipeline first: `python src/train_model.py`")
    st.stop()

with open(results_path, "r", encoding="utf-8") as f:
    eval_data = json.load(f)

models_data = eval_data.get("models", {})
best_model_name = eval_data.get("best_model_name", "Support Vector Machine (SVM)")
metadata = eval_data.get("metadata", {})
rq_data = eval_data.get("research_questions", {})

# Top Overview Cards
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
with m_col1:
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-val">{metadata.get('train_size', 8000)} / {metadata.get('test_size', 2000)}</div>
            <div class="metric-lbl">Train / Test Split (80/20)</div>
        </div>
    """, unsafe_allow_html=True)
with m_col2:
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-val">{metadata.get('feature_count', 5000)}</div>
            <div class="metric-lbl">TF-IDF N-Gram Features</div>
        </div>
    """, unsafe_allow_html=True)
with m_col3:
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-val" style="color: #00d2ff;">5-Fold</div>
            <div class="metric-lbl">Stratified Cross-Validation</div>
        </div>
    """, unsafe_allow_html=True)
with m_col4:
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-val" style="color: #10b981;">{best_model_name.split('(')[0]}</div>
            <div class="metric-lbl">Best Classifier (F1-Score)</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 1. Comparative Model Performance Table
st.markdown("### 🏆 Comprehensive Model Comparison Table")
st.caption("All metrics computed on the strictly held-out test partition (2,000 emails) after 5-Fold Stratified Cross-Validation.")

table_rows = []
for name, data in models_data.items():
    tm = data["test_metrics"]
    cv = data.get("cross_validation", {})
    table_rows.append({
        "Algorithm": name,
        "CV F1 (Mean ± Std)": f"{cv.get('cv_f1_mean', 0.0):.4f} ± {cv.get('cv_f1_std', 0.0):.4f}",
        "Test Accuracy": f"{tm['accuracy']:.4f}",
        "Test Precision": f"{tm['precision']:.4f}",
        "Test Recall": f"{tm['recall']:.4f}",
        "Test F1-Score": f"{tm['f1']:.4f}",
        "ROC-AUC": f"{tm['roc_auc']:.4f}" if tm['roc_auc'] is not None else "N/A",
        "Train Time (s)": f"{data['train_time_seconds']:.3f}",
        "Inference (ms/email)": f"{data['inference_time_ms_per_email']:.3f}"
    })

df_table = pd.DataFrame(table_rows)
st.dataframe(df_table, use_container_width=True, hide_index=True)

st.markdown("---")

# 2. Confusion Matrices & Metric Visualizations
st.markdown("### 🔲 Confusion Matrices & Error Breakdown")

col_cm_select, col_cm_plot = st.columns([1, 2])

with col_cm_select:
    selected_eval_model = st.selectbox(
        "Select Model for Detailed Inspection",
        options=list(models_data.keys()),
        index=list(models_data.keys()).index(best_model_name) if best_model_name in models_data else 0
    )
    m_info = models_data[selected_eval_model]
    cm_info = m_info["test_metrics"]["confusion_matrix"]

    st.markdown(f"""
        <div class="cyber-card">
            <h4 style="color: #00d2ff; margin-top: 0;">Error Breakdown</h4>
            <p style="font-size: 0.88rem; color: #cbd5e1; margin-bottom: 6px;">
                • <b>True Negatives (TN):</b> {cm_info['tn']} (Legitimate correctly identified)<br>
                • <b>True Positives (TP):</b> {cm_info['tp']} (Phishing correctly caught)<br>
                • <b>False Positives (FP):</b> {cm_info['fp']} (Legitimate flagged as phish)<br>
                • <b>False Negatives (FN):</b> {cm_info['fn']} (Phishing slipped through)
            </p>
            <div style="margin-top: 10px; font-size: 0.82rem; color: #94a3b8;">
                False Positive Rate: <b>{m_info['test_metrics']['false_positive_rate'] * 100:.2f}%</b><br>
                False Negative Rate: <b>{m_info['test_metrics']['false_negative_rate'] * 100:.2f}%</b>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_cm_plot:
    cm_fig = plot_confusion_matrix(cm_info["matrix"], selected_eval_model)
    st.plotly_chart(cm_fig, use_container_width=True)

st.markdown("---")

# 3. ROC & Precision-Recall Curves
st.markdown("### 📈 Receiver Operating Characteristic (ROC) & Precision-Recall Curves")
c_roc, c_pr = st.columns(2)
with c_roc:
    roc_fig = plot_roc_curves(models_data)
    st.plotly_chart(roc_fig, use_container_width=True)
with c_pr:
    pr_fig = plot_pr_curves(models_data)
    st.plotly_chart(pr_fig, use_container_width=True)

st.markdown("---")

# 4. Critical Cybersecurity Trade-Offs & Accuracy Paradox
st.markdown("### ⚖️ Cybersecurity Trade-Off Analysis & The Accuracy Paradox")

t1, t2 = st.columns(2)
with t1:
    st.markdown("""
        <div class="cyber-card">
            <h4 style="color: #ef4444; margin-top: 0;">False Negatives vs False Positives</h4>
            <p style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.6;">
                In email security, the asymmetric risk profile is profound:
            </p>
            <ul style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.6;">
                <li><b>False Negatives (Critical Danger):</b> A phishing email reaches an employee's inbox. An unauthorized credential entry or malware download can compromise the entire enterprise network. High <b>Recall</b> is paramount.</li>
                <li><b>False Positives (Operational Friction):</b> A benign vendor quote or academic announcement is quarantined. Excessive false alarms cause user frustration and filter evasion.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with t2:
    st.markdown("""
        <div class="cyber-card">
            <h4 style="color: #f59e0b; margin-top: 0;">Why Accuracy Alone is Insufficient (The Accuracy Paradox)</h4>
            <p style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.6;">
                Consider an enterprise mail system where 98% of incoming traffic is legitimate and only 2% is phishing.
                A trivial baseline model that classifies <i>every single email as legitimate</i> achieves <b>98% accuracy</b>, 
                yet fails to stop 100% of cyberattacks (0% Recall).
            </p>
            <p style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.6;">
                Therefore, evaluators must evaluate <b>F1-score, Precision, Recall, and ROC-AUC</b> rather than raw accuracy.
            </p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 5. Research Questions Investigation (RQ1 - RQ4)
st.markdown("### 🔬 Academic Research Questions (RQ1 – RQ4)")

rq_tabs = st.tabs([
    "RQ1: Model Comparison",
    "RQ2: Metric Strengths",
    "RQ3: Hybrid vs Text-Only",
    "RQ4: Generalization Stress Test"
])

with rq_tabs[0]:
    rq1 = rq_data.get("RQ1", {})
    st.markdown(f"**Research Question 1:** *{rq1.get('question', '')}*")
    st.info(rq1.get("conclusion", ""))

with rq_tabs[1]:
    rq2 = rq_data.get("RQ2", {})
    st.markdown(f"**Research Question 2:** *{rq2.get('question', '')}*")
    st.info(rq2.get("conclusion", ""))

with rq_tabs[2]:
    rq3 = rq_data.get("RQ3", {})
    st.markdown(f"**Research Question 3:** *{rq3.get('question', '')}*")
    st.info(rq3.get("conclusion", ""))
    
    comp = rq3.get("comparison", {})
    if comp:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### Text-Only Baseline")
            st.json(comp.get("text_only_baseline", {}))
        with c2:
            st.markdown("##### Hybrid (Text + Structured Security Features)")
            st.json(comp.get("hybrid_text_plus_structured", {}))

with rq_tabs[3]:
    rq4 = rq_data.get("RQ4", {})
    st.markdown(f"**Research Question 4:** *{rq4.get('question', '')}*")
    st.info(rq4.get("conclusion", ""))
    st.markdown(f"**Stress Test Partition:** {rq4.get('stress_test_sample_count', 0)} atypical / short email samples.")
    st.json(rq4.get("stress_test_metrics", {}))
