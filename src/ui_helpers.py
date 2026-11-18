"""
UI Design Helpers, Custom CSS, and Visualization Components for Streamlit.
Provides a modern cybersecurity SOC (Security Operations Center) dashboard theme.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List, Optional


def apply_cyber_theme():
    """Injects modern dark cybersecurity SOC theme with cyan and neon accents."""
    st.markdown("""
        <style>
        /* Main background and font styling */
        .stApp {
            background-color: #0b132b;
            color: #e2e8f0;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #070d1e !important;
            border-right: 1px solid #1e293b;
        }

        /* Card container */
        .cyber-card {
            background: linear-gradient(135deg, #111d35 0%, #162444 100%);
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
        }

        .cyber-card-accent {
            background: linear-gradient(135deg, #111d35 0%, #192a4a 100%);
            border-left: 4px solid #00d2ff;
            border-top: 1px solid #1e293b;
            border-right: 1px solid #1e293b;
            border-bottom: 1px solid #1e293b;
            border-radius: 10px;
            padding: 16px 20px;
            margin-bottom: 15px;
        }

        /* Header banner */
        .soc-banner {
            background: linear-gradient(90deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
            border: 1px solid #312e81;
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            margin-bottom: 24px;
            box-shadow: 0 0 25px rgba(99, 102, 241, 0.2);
        }

        .soc-title {
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(90deg, #00d2ff, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 6px;
        }

        .soc-subtitle {
            font-size: 1.05rem;
            color: #94a3b8;
        }

        /* Metric badge styling */
        .metric-box {
            background-color: #0d1930;
            border: 1px solid #1e293b;
            border-radius: 10px;
            padding: 16px;
            text-align: center;
        }
        .metric-val {
            font-size: 1.8rem;
            font-weight: 700;
            color: #00d2ff;
        }
        .metric-lbl {
            font-size: 0.85rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* Result Verdict Badges */
        .verdict-badge {
            display: inline-block;
            font-size: 1.5rem;
            font-weight: 800;
            padding: 12px 28px;
            border-radius: 30px;
            text-align: center;
            letter-spacing: 0.05em;
            margin: 10px 0;
        }
        .verdict-phishing {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.25) 0%, rgba(185, 28, 28, 0.4) 100%);
            border: 2px solid #ef4444;
            color: #fca5a5;
            box-shadow: 0 0 20px rgba(239, 68, 68, 0.4);
        }
        .verdict-suspicious {
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.25) 0%, rgba(180, 83, 9, 0.4) 100%);
            border: 2px solid #f59e0b;
            color: #fde68a;
            box-shadow: 0 0 20px rgba(245, 158, 11, 0.4);
        }
        .verdict-legitimate {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.25) 0%, rgba(4, 120, 87, 0.4) 100%);
            border: 2px solid #10b981;
            color: #a7f3d0;
            box-shadow: 0 0 20px rgba(16, 185, 129, 0.4);
        }

        /* Indicator Pill */
        .indicator-pill {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            margin-right: 8px;
        }
        .pill-critical { background: #7f1d1d; color: #fca5a5; border: 1px solid #ef4444; }
        .pill-high { background: #7c2d12; color: #fdba74; border: 1px solid #f97316; }
        .pill-medium { background: #713f12; color: #fde047; border: 1px solid #eab308; }
        .pill-low { background: #14532d; color: #86efac; border: 1px solid #22c55e; }

        /* Custom buttons */
        div.stButton > button:first-child {
            background: linear-gradient(90deg, #0284c7 0%, #2563eb 100%);
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: 600;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4);
            transition: all 0.2s ease-in-out;
        }
        div.stButton > button:first-child:hover {
            background: linear-gradient(90deg, #0369a1 0%, #1d4ed8 100%);
            box-shadow: 0 6px 20px rgba(37, 99, 235, 0.6);
            transform: translateY(-1px);
        }
        </style>
    """, unsafe_allow_html=True)


def render_header(title: str, subtitle: str, badge: str = "SOC DEFENSE ENGINE"):
    """Renders the standard cybersecurity SOC banner."""
    st.markdown(f"""
        <div class="soc-banner">
            <span style="background-color: #312e81; color: #a5b4fc; font-size: 0.75rem; font-weight: 700; padding: 4px 12px; border-radius: 12px; letter-spacing: 0.1em; text-transform: uppercase;">
                🛡️ {badge}
            </span>
            <div class="soc-title">{title}</div>
            <div class="soc-subtitle">{subtitle}</div>
        </div>
    """, unsafe_allow_html=True)


def plot_confusion_matrix(cm_matrix: List[List[int]], model_name: str) -> go.Figure:
    """Creates an interactive Plotly confusion matrix heatmap."""
    labels = ["Legitimate (0)", "Phishing (1)"]
    z = cm_matrix
    tn, fp = z[0][0], z[0][1]
    fn, tp = z[1][0], z[1][1]
    total = tn + fp + fn + tp

    text = [
        [f"True Negatives (TN)<br>{tn}<br>({tn/total:.1%})", f"False Positives (FP)<br>{fp}<br>({fp/total:.1%})"],
        [f"False Negatives (FN)<br>{fn}<br>({fn/total:.1%})", f"True Positives (TP)<br>{tp}<br>({tp/total:.1%})"]
    ]

    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=labels,
        y=labels,
        text=text,
        texttemplate="%{text}",
        textfont={"size": 13, "color": "white"},
        colorscale=[[0, "#0f172a"], [0.5, "#1e3a8a"], [1.0, "#0284c7"]],
        showscale=False
    ))

    fig.update_layout(
        title=f"Confusion Matrix: {model_name}",
        xaxis_title="Predicted Label",
        yaxis_title="True Ground-Truth Label",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=50, b=40),
        height=360
    )
    return fig


def plot_roc_curves(models_data: Dict[str, Any]) -> go.Figure:
    """Plots comparative ROC curves for all models."""
    fig = go.Figure()
    colors = ["#00d2ff", "#10b981", "#f59e0b", "#a855f7"]

    idx = 0
    for name, data in models_data.items():
        curves = data.get("curves", {}).get("roc", {})
        if curves and "fpr" in curves and "tpr" in curves:
            auc = data.get("test_metrics", {}).get("roc_auc", 0.0)
            fig.add_trace(go.Scatter(
                x=curves["fpr"],
                y=curves["tpr"],
                mode="lines",
                name=f"{name} (AUC = {auc})",
                line=dict(color=colors[idx % len(colors)], width=2.5)
            ))
            idx += 1

    # Diagonal random baseline
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1],
        mode="lines",
        name="Random Classifier (AUC = 0.50)",
        line=dict(color="#64748b", dash="dash", width=1.5)
    ))

    fig.update_layout(
        title="Comparative Receiver Operating Characteristic (ROC) Curves",
        xaxis_title="False Positive Rate (FPR)",
        yaxis_title="True Positive Rate (Recall)",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(yanchor="bottom", y=0.05, xanchor="right", x=0.98),
        margin=dict(l=40, r=40, t=50, b=40),
        height=400
    )
    return fig


def plot_pr_curves(models_data: Dict[str, Any]) -> go.Figure:
    """Plots comparative Precision-Recall curves."""
    fig = go.Figure()
    colors = ["#00d2ff", "#10b981", "#f59e0b", "#a855f7"]

    idx = 0
    for name, data in models_data.items():
        curves = data.get("curves", {}).get("pr", {})
        if curves and "recall" in curves and "precision" in curves:
            f1 = data.get("test_metrics", {}).get("f1", 0.0)
            fig.add_trace(go.Scatter(
                x=curves["recall"],
                y=curves["precision"],
                mode="lines",
                name=f"{name} (F1 = {f1})",
                line=dict(color=colors[idx % len(colors)], width=2.5)
            ))
            idx += 1

    fig.update_layout(
        title="Comparative Precision-Recall Curves",
        xaxis_title="Recall (Sensitivity)",
        yaxis_title="Precision (PPV)",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(yanchor="bottom", y=0.05, xanchor="left", x=0.05),
        margin=dict(l=40, r=40, t=50, b=40),
        height=400
    )
    return fig


def plot_token_importance(token_attributions: Dict[str, Any]) -> Optional[go.Figure]:
    """Plots horizontal bar chart of top positive (phishing) and negative (legitimate) tokens."""
    if not token_attributions.get("supported"):
        return None

    phish_tokens = token_attributions.get("phishing_tokens", [])
    legit_tokens = token_attributions.get("legitimate_tokens", [])

    if not phish_tokens and not legit_tokens:
        return None

    terms = []
    impacts = []
    colors = []

    for t in reversed(legit_tokens):
        terms.append(t["token"])
        impacts.append(t["impact"])
        colors.append("#10b981")  # Green for legitimate

    for t in phish_tokens:
        terms.append(t["token"])
        impacts.append(t["impact"])
        colors.append("#ef4444")  # Red for phishing

    fig = go.Figure(go.Bar(
        x=impacts,
        y=terms,
        orientation="h",
        marker=dict(color=colors)
    ))

    fig.update_layout(
        title="Feature Attribution: Salient N-Gram Weights (Impact on Classification)",
        xaxis_title="← Favors Legitimate | Favors Phishing →",
        yaxis_title="Token",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=80, r=40, t=50, b=40),
        height=320
    )
    return fig
