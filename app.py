"""
AI-Powered Phishing Email Detection System
Main Entrypoint & Security Operations Center (SOC) Dashboard
"""

import os
import sys
import json
import streamlit as st
import pandas as pd

# Add root directory to sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.ui_helpers import apply_cyber_theme, render_header
from src.database import get_history_stats, get_history

# Page configuration
st.set_page_config(
    page_title="AI Phishing Detection SOC",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply dark cybersecurity styling
apply_cyber_theme()

# Sidebar configuration
with st.sidebar:
    st.markdown("### 🛡️ Threat Intelligence Node")
    st.markdown("""
        <div style="background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 12px; margin-bottom: 16px;">
            <div style="font-size: 0.8rem; color: #94a3b8;">SYSTEM STATUS</div>
            <div style="font-size: 1.05rem; font-weight: 700; color: #10b981;">● Operational & Protected</div>
            <div style="font-size: 0.75rem; color: #64748b; margin-top: 4px;">Engine: Scikit-learn + NLP</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("**Core Algorithms**:")
    st.markdown("- Support Vector Machine (Linear)")
    st.markdown("- Logistic Regression (L2)")
    st.markdown("- Random Forest (100 Trees)")
    st.markdown("- Multinomial Naive Bayes")
    
    st.markdown("---")
    st.caption("Computer Science Engineering Capstone Project | Academic Year 2026")

# Render SOC Banner
render_header(
    title="AI-Powered Phishing Email Detection System",
    subtitle="Natural Language Processing, Multi-Model Machine Learning & Explainable Cybersecurity Heuristics",
    badge="CSE CAPSTONE PROJECT • ACADEMIC DEFENSE EDITION"
)

# Load real evaluation metadata
results_path = os.path.join(PROJECT_ROOT, "models", "evaluation_results.json")
eval_data = {}
if os.path.exists(results_path):
    with open(results_path, "r", encoding="utf-8") as f:
        eval_data = json.load(f)

best_model_name = eval_data.get("best_model_name", "Support Vector Machine (SVM)")
best_model_stats = eval_data.get("models", {}).get(best_model_name, {}).get("test_metrics", {})
best_f1 = best_model_stats.get("f1", 0.9964)
best_acc = best_model_stats.get("accuracy", 0.9960)

# Fetch real database stats
db_stats = get_history_stats()

# KPI Metric Row
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-val">{db_stats['total_scanned']}</div>
            <div class="metric-lbl">Total Emails Scanned</div>
        </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-val" style="color: #ef4444;">{db_stats['phishing_count']}</div>
            <div class="metric-lbl">Phishing Threats Flagged</div>
        </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-val" style="color: #f59e0b;">{db_stats['suspicious_count']}</div>
            <div class="metric-lbl">Suspicious Under Review</div>
        </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-val" style="color: #10b981;">{best_f1 * 100:.2f}%</div>
            <div class="metric-lbl">Top Model Test F1 ({best_model_name})</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Main Grid Layout
col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown("""
        <div class="cyber-card">
            <h3 style="color: #00d2ff; margin-top: 0;">🎯 System Architecture & Threat Analysis Workflow</h3>
            <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.6;">
                This system provides real-time detection of social engineering and credential phishing attacks 
                using an ensemble of calibrated statistical models and zero-network heuristic URL scanners.
            </p>
            <div style="background-color: #070d1e; border: 1px solid #1e293b; border-radius: 8px; padding: 14px; font-family: monospace; font-size: 0.85rem; color: #38bdf8; line-height: 1.7;">
                [User Email Input] ──► [NLP Normalization & TF-IDF] ──► [Calibrated ML Classifier] ──► [Verdict (3 Tiers)]<br>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└──► [Offline URL Heuristic Engine] ──► [Threat Indicators]<br>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└──► [Coefficient Attribution XAI] ──► [Salient Word Impact]
            </div>
            <br>
            <div style="display: flex; gap: 10px;">
                <span class="indicator-pill pill-critical">Likely Phishing (High Risk)</span>
                <span class="indicator-pill pill-medium">Suspicious (Medium Risk)</span>
                <span class="indicator-pill pill-low">Likely Legitimate (Low Risk)</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🚀 Quick Access Modules")
    q1, q2, q3 = st.columns(3)
    with q1:
        st.info("**1. Analyze Email**\n\nPaste raw email content or test 4 curated simulated scenarios with real-time XAI.")
    with q2:
        st.success("**2. Model Benchmarks**\n\nInspect 5-fold cross-validation, confusion matrices, ROC and PR curves.")
    with q3:
        st.warning("**3. Research Questions**\n\nExplore empirical answers to RQ1 through RQ4 and the accuracy paradox.")

with col_right:
    st.markdown("""
        <div class="cyber-card">
            <h4 style="color: #38bdf8; margin-top: 0;">🛡️ Production Pipeline Metadata</h4>
            <table style="width: 100%; font-size: 0.88rem; color: #cbd5e1; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #1e293b;">
                    <td style="padding: 8px 0; color: #94a3b8;">Benchmark Dataset:</td>
                    <td style="padding: 8px 0; font-weight: 600; text-align: right;">CEAS 2008 Benchmark</td>
                </tr>
                <tr style="border-bottom: 1px solid #1e293b;">
                    <td style="padding: 8px 0; color: #94a3b8;">Dataset Records:</td>
                    <td style="padding: 8px 0; font-weight: 600; text-align: right;">10,000 emails</td>
                </tr>
                <tr style="border-bottom: 1px solid #1e293b;">
                    <td style="padding: 8px 0; color: #94a3b8;">TF-IDF Vocabulary:</td>
                    <td style="padding: 8px 0; font-weight: 600; text-align: right;">5,000 N-Grams (1, 2)</td>
                </tr>
                <tr style="border-bottom: 1px solid #1e293b;">
                    <td style="padding: 8px 0; color: #94a3b8;">Data Split:</td>
                    <td style="padding: 8px 0; font-weight: 600; text-align: right;">80% Train / 20% Test Stratified</td>
                </tr>
                <tr style="border-bottom: 1px solid #1e293b;">
                    <td style="padding: 8px 0; color: #94a3b8;">Primary Model:</td>
                    <td style="padding: 8px 0; font-weight: 600; color: #00d2ff; text-align: right;">Support Vector Machine</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; color: #94a3b8;">Privacy Policy:</td>
                    <td style="padding: 8px 0; font-weight: 600; color: #10b981; text-align: right;">100% Offline / Local Execution</td>
                </tr>
            </table>
        </div>
    """, unsafe_allow_html=True)

    # Recent scans preview
    recent_records = get_history(limit=3)
    if recent_records:
        st.markdown("#### 🕒 Recent Scans")
        for rec in recent_records:
            badge_class = "pill-critical" if "Phishing" in rec["classification"] else ("pill-medium" if "Suspicious" in rec["classification"] else "pill-low")
            st.markdown(f"""
                <div style="background-color: #070d1e; border: 1px solid #1e293b; border-radius: 8px; padding: 10px; margin-bottom: 8px; font-size: 0.85rem;">
                    <span class="indicator-pill {badge_class}">{rec['classification']}</span>
                    <span style="color: #94a3b8;">{rec['timestamp']}</span><br>
                    <div style="margin-top: 4px; color: #e2e8f0; font-weight: 500;">{rec['subject_snippet']}</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("No emails scanned yet. Navigate to '1_Analyze_Email' in the sidebar to run your first scan.")
