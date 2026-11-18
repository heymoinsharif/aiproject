"""
Email Analysis History and Privacy Page
Provides a filterable audit log of past email scans.
Ensures zero storage of full message bodies, passwords, or authentication secrets.
Allows users to purge history on demand.
"""

import os
import sys
import streamlit as st
import pandas as pd

# Add root directory to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.ui_helpers import apply_cyber_theme, render_header
from src.database import get_history, get_history_stats, clear_history

st.set_page_config(page_title="Analysis History | AI Phishing Detector", page_icon="📜", layout="wide")
apply_cyber_theme()

render_header(
    title="Email Scan Audit History & Privacy Controls",
    subtitle="Privacy-preserving local database storing metadata, classification verdicts, and indicators",
    badge="AUDIT & COMPLIANCE"
)

# Privacy Policy Callout
st.markdown("""
    <div class="cyber-card" style="border-left: 4px solid #10b981;">
        <h4 style="color: #10b981; margin-top: 0;">🔒 Zero-Knowledge Privacy Architecture</h4>
        <p style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.5; margin-bottom: 0;">
            This system enforces strict local privacy. Full email bodies, passwords, and sensitive credentials 
            are <b>never saved</b> to disk or external cloud servers. Only truncated subject previews, timestamped 
            verdicts, confidence scores, and heuristic indicators are retained in the local SQLite database.
        </p>
    </div>
""", unsafe_allow_html=True)

# Fetch stats
stats = get_history_stats()

# Filter & Action Controls
col_filter, col_limit, col_clear = st.columns([2, 1, 1])

with col_filter:
    filter_choice = st.selectbox(
        "Filter by Classification",
        options=["All", "Likely Phishing", "Suspicious", "Likely Legitimate"],
        index=0
    )

with col_limit:
    limit_choice = st.selectbox(
        "Max Records",
        options=[25, 50, 100, 250],
        index=1
    )

with col_clear:
    st.write("&nbsp;")
    if st.button("🗑️ Clear All History", type="secondary", use_container_width=True):
        clear_history()
        st.success("History database purged successfully.")
        st.rerun()

# Fetch filtered records
records = get_history(limit=limit_choice, classification_filter=filter_choice)

if records:
    st.markdown(f"### 📋 Audit Records ({len(records)} entries displayed)")

    table_data = []
    for r in records:
        table_data.append({
            "Scan ID": r["id"],
            "Timestamp": r["timestamp"],
            "Subject Snippet": r["subject_snippet"],
            "Sender Domain": r["sender_domain"],
            "Classification": r["classification"],
            "Confidence": f"{r['confidence'] * 100:.1f}%",
            "Risk Level": r["risk_level"],
            "Indicators Count": len(r["indicators"]),
            "URLs Found": r["urls_count"]
        })

    df_history = pd.DataFrame(table_data)
    st.dataframe(df_history, use_container_width=True, hide_index=True)

    # Detailed record inspector
    st.markdown("#### 🔍 Inspect Selected Scan Details")
    selected_id = st.selectbox("Select Scan ID to view indicators:", options=[r["id"] for r in records])
    selected_record = next((r for r in records if r["id"] == selected_id), None)

    if selected_record:
        st.markdown(f"""
            <div class="cyber-card">
                <div style="font-size: 0.95rem; color: #00d2ff; font-weight: 700;">
                    Scan #{selected_record['id']} — {selected_record['classification']} ({selected_record['confidence']*100:.1f}% confidence)
                </div>
                <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 4px;">
                    Timestamp: {selected_record['timestamp']} | Sender Domain: {selected_record['sender_domain']}
                </div>
                <div style="margin-top: 10px; font-size: 0.88rem; color: #cbd5e1;">
                    <b>Subject:</b> {selected_record['subject_snippet']}
                </div>
                <div style="margin-top: 10px;">
                    <b>Detected Indicators:</b>
                    <ul style="margin-top: 4px; color: #fca5a5;">
                        {''.join(f'<li>{ind}</li>' for ind in selected_record['indicators']) if selected_record['indicators'] else '<li style="color: #86efac;">None flagged</li>'}
                    </ul>
                </div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("No scan history records found matching your filter criteria. Analyze an email in the scanner to populate this log.")
