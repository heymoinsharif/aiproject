"""
Analyze Email Page
Allows users to analyze custom email inputs or test fictional sample emails.
Features real-time probability calibration, Explainable AI (XAI) feature attribution,
offline URL security heuristics, and privacy-preserving history logging.
"""

import os
import sys
import streamlit as st
import pandas as pd

# Add root directory to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.ui_helpers import apply_cyber_theme, render_header, plot_token_importance
from src.predict import PhishingDetector
from src.database import log_analysis
from data.samples import SAMPLE_EMAILS

st.set_page_config(page_title="Analyze Email | AI Phishing Detector", page_icon="🔍", layout="wide")
apply_cyber_theme()

render_header(
    title="Email Threat Analyzer & Explainable AI",
    subtitle="Paste custom email contents or load simulated test scenarios for multi-tier classification",
    badge="INSPECTION ENGINE"
)

# Initialize detector in session state
if "detector" not in st.session_state:
    st.session_state.detector = PhishingDetector()

detector = st.session_state.detector

# Initialize form values in session state
if "form_subject" not in st.session_state:
    st.session_state.form_subject = ""
if "form_body" not in st.session_state:
    st.session_state.form_body = ""
if "form_sender" not in st.session_state:
    st.session_state.form_sender = ""
if "form_urls" not in st.session_state:
    st.session_state.form_urls = ""

# Sample email loader callback
def load_sample_email(sample_name: str):
    if sample_name in SAMPLE_EMAILS:
        sample = SAMPLE_EMAILS[sample_name]
        st.session_state.form_subject = sample["subject"]
        st.session_state.form_body = sample["body"]
        st.session_state.form_sender = sample["sender"]
        st.session_state.form_urls = sample["urls"]
        st.session_state["loaded_sample_desc"] = sample["description"]

# Sample Email Bar
st.markdown("### 🧪 Load Curated Demonstration Samples")
st.caption("These fictional test scenarios illustrate model behavior across distinct threat profiles. Sample emails are simulations, not proof of absolute model accuracy.")

s_cols = st.columns(4)
sample_keys = list(SAMPLE_EMAILS.keys())
for i, key in enumerate(sample_keys):
    with s_cols[i]:
        if st.button(key, use_container_width=True):
            load_sample_email(key)
            st.rerun()

if "loaded_sample_desc" in st.session_state and st.session_state["loaded_sample_desc"]:
    st.info(f"💡 **Loaded Scenario Notes:** {st.session_state['loaded_sample_desc']}")

st.markdown("---")

# Input Form
with st.form("email_analysis_form"):
    st.markdown("### 📥 Email Content Input")
    
    col_hdr1, col_hdr2 = st.columns([2, 1])
    with col_hdr1:
        subject_input = st.text_input(
            "Email Subject Line *",
            value=st.session_state.form_subject,
            placeholder="e.g. Action Required: Please verify your account"
        )
    with col_hdr2:
        model_choice = st.selectbox(
            "Select Inference Model",
            options=["Support Vector Machine (SVM)", "Logistic Regression", "Random Forest", "Multinomial Naive Bayes"],
            index=0,
            help="Allows comparing how distinct algorithms classify the exact same email."
        )

    body_input = st.text_area(
        "Email Body Content *",
        value=st.session_state.form_body,
        height=200,
        placeholder="Paste full plain-text email message body here..."
    )

    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        sender_input = st.text_input(
            "Sender Information (Optional)",
            value=st.session_state.form_sender,
            placeholder="e.g. IT Support <support@company-portal.xyz>"
        )
    with col_opt2:
        urls_input = st.text_input(
            "Additional URLs / Hyperlinks (Optional)",
            value=st.session_state.form_urls,
            placeholder="e.g. http://192.168.1.100/login.php"
        )

    submitted = st.form_submit_button("🔍 Analyze Email", use_container_width=True)

# Analysis execution
if submitted:
    if not subject_input.strip() and not body_input.strip():
        st.error("⚠️ Please provide at least an email subject line or body content for analysis.")
    else:
        with st.spinner("Analyzing email text, extracting URL indicators, and computing model attributions..."):
            result = detector.analyze_email(
                subject=subject_input,
                body=body_input,
                sender=sender_input,
                urls_input=urls_input,
                selected_model=model_choice
            )

            # Log to privacy-preserving SQLite database
            log_analysis(
                subject=subject_input,
                sender=sender_input,
                classification=result["classification"],
                confidence=result["confidence_pct"] / 100.0,
                risk_level=result["risk_level"],
                indicators=[ind["description"] for ind in result["observed_indicators"]],
                urls_count=result["url_analysis"]["total_urls_found"]
            )

            st.session_state["latest_result"] = result

# Display Results
if "latest_result" in st.session_state:
    res = st.session_state["latest_result"]
    verdict = res["classification"]
    confidence = res["confidence_pct"]
    risk_level = res["risk_level"]
    badge_style = "verdict-phishing" if verdict == "Likely Phishing" else ("verdict-suspicious" if verdict == "Suspicious" else "verdict-legitimate")
    icon = "🚨" if verdict == "Likely Phishing" else ("⚠️" if verdict == "Suspicious" else "✅")

    st.markdown("### 📊 Classification Verdict")

    r_col1, r_col2 = st.columns([1, 2])
    with r_col1:
        st.markdown(f"""
            <div class="cyber-card" style="text-align: center;">
                <div style="font-size: 0.9rem; color: #94a3b8; text-transform: uppercase;">Primary Classification</div>
                <div class="verdict-badge {badge_style}">{icon} {verdict}</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #e2e8f0; margin-top: 8px;">
                    Risk Level: <span style="color: #00d2ff;">{risk_level}</span>
                </div>
                <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 4px;">
                    Evaluated by: <b>{res['model_used']}</b>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with r_col2:
        st.markdown(f"""
            <div class="cyber-card">
                <h4 style="margin-top: 0; color: #00d2ff;">Calibrated Probability Distribution</h4>
                <div style="margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px;">
                        <span>Phishing Likelihood</span>
                        <b>{res['phishing_probability'] * 100:.2f}%</b>
                    </div>
                    <div style="background-color: #1e293b; border-radius: 6px; height: 12px; overflow: hidden;">
                        <div style="background: linear-gradient(90deg, #f59e0b 0%, #ef4444 100%); width: {res['phishing_probability'] * 100}%; height: 100%;"></div>
                    </div>
                </div>
                <div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px;">
                        <span>Legitimate Likelihood</span>
                        <b>{res['legitimate_probability'] * 100:.2f}%</b>
                    </div>
                    <div style="background-color: #1e293b; border-radius: 6px; height: 12px; overflow: hidden;">
                        <div style="background: linear-gradient(90deg, #0284c7 0%, #10b981 100%); width: {res['legitimate_probability'] * 100}%; height: 100%;"></div>
                    </div>
                </div>
                <div style="margin-top: 14px; font-size: 0.82rem; color: #94a3b8; line-height: 1.4;">
                    ℹ️ <i>{res['disclaimer']}</i>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Explainable AI & Indicators Tabs
    tab_xai, tab_indicators, tab_urls = st.tabs([
        "🧠 Statistical Feature Attribution (XAI)",
        "🚩 Observed Security Indicators",
        "🔗 Offline URL Heuristics"
    ])

    with tab_xai:
        st.markdown("#### Model Feature Weights (Salient N-Grams)")
        st.caption(
            "Feature attributions computed from model coefficients. Words pushing the decision boundary toward "
            "phishing are shown in red (+), while terms characteristic of legitimate correspondence are shown in green (-)."
        )
        xai_fig = plot_token_importance(res["token_attributions"])
        if xai_fig:
            st.plotly_chart(xai_fig, use_container_width=True)
        else:
            st.info("Linear feature attribution is not exposed by the selected model architecture (e.g., Random Forest).")

    with tab_indicators:
        st.markdown("#### Observed Threat Patterns & Heuristic Rules")
        st.caption("Deterministic pattern matches observed in subject and body. Distinct from statistical inference.")
        indicators = res["observed_indicators"]
        if indicators:
            for ind in indicators:
                sev = ind.get("severity", "Medium")
                pill_class = f"pill-{sev.lower()}"
                st.markdown(f"""
                    <div class="cyber-card-accent">
                        <span class="indicator-pill {pill_class}">{sev} Severity</span>
                        <b>{ind['category']}</b>: {ind['description']}<br>
                        <span style="font-size: 0.82rem; color: #94a3b8; margin-top: 4px; display: inline-block;">
                            {ind['evidence']}
                        </span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.success("No overt suspicious keywords, urgency triggers, or credential patterns observed.")

    with tab_urls:
        st.markdown("#### Offline URL Structural Analysis")
        st.caption("Static inspection of URL structure, encoding, IP hosts, and domain properties. Zero external network requests made.")
        url_rep = res["url_analysis"]
        st.write(f"**Total URLs Identified:** {url_rep['total_urls_found']}")
        if url_rep["url_details"]:
            for u in url_rep["url_details"]:
                st.markdown(f"""
                    <div class="cyber-card">
                        <div style="font-family: monospace; font-size: 0.95rem; color: #38bdf8;">{u['url']}</div>
                        <div style="margin-top: 6px; font-size: 0.85rem; color: #cbd5e1;">
                            • Hostname: <b>{u['hostname']}</b> | Length: <b>{u['length']} chars</b> | Subdomains: <b>{u['subdomain_count']}</b>
                        </div>
                        {f"<div style='color: #fca5a5; margin-top: 4px; font-size: 0.85rem;'>⚠️ Flags: {', '.join(u['flags'])}</div>" if u['flags'] else "<div style='color: #86efac; margin-top: 4px; font-size: 0.85rem;'>✓ No structural URL anomalies flagged</div>"}
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.write("No URLs identified in this email.")
