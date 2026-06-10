"""
QuantScore Credit Risk Intelligence — Streamlit Frontend v2
Includes: Single scoring, Batch upload, Portfolio dashboard, Expected Loss
"""

import io
import os

import pandas as pd
import requests
import streamlit as st

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="QuantScore — Credit Risk Intelligence",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg:      #0a0e17;
    --surface: #111827;
    --border:  #1e2d45;
    --accent:  #00d4aa;
    --accent2: #3b82f6;
    --danger:  #ef4444;
    --warning: #f59e0b;
    --text:    #e2e8f0;
    --muted:   #64748b;
    --mono:    'DM Mono', monospace;
    --sans:    'Syne', sans-serif;
}

html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2.5rem !important; max-width: 1600px !important; }

.qs-header {
    display: flex; align-items: center; gap: 1rem;
    padding: 1rem 0 1.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
}
.qs-logo {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    clip-path: polygon(50% 0%,100% 25%,100% 75%,50% 100%,0% 75%,0% 25%);
}
.qs-title { font-size: 1.5rem; font-weight: 800; letter-spacing: -0.02em; }
.qs-title span { color: var(--accent); }
.qs-subtitle { font-size: 0.75rem; color: var(--muted); font-family: var(--mono); }

.qs-section {
    font-size: 0.65rem; font-family: var(--mono); color: var(--accent);
    letter-spacing: 0.15em; text-transform: uppercase;
    margin-bottom: 0.75rem; padding-bottom: 0.35rem;
    border-bottom: 1px solid var(--border);
}

.qs-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 8px; padding: 1.25rem; margin-bottom: 0.75rem;
}

/* Score */
.qs-score-value { font-size: 3.5rem; font-weight: 800; font-family: var(--mono); line-height: 1; }
.qs-score-label { font-size: 0.7rem; font-family: var(--mono); color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase; margin-top: 0.4rem; }

/* Gauge */
.gauge-wrap { position: relative; width: 160px; height: 90px; margin: 0 auto; overflow: hidden; }
.gauge-track { position: absolute; width: 160px; height: 160px; border-radius: 50%; top: 0; left: 0;
    border: 16px solid var(--border); border-bottom-color: transparent; border-right-color: transparent; transform: rotate(135deg); }
.gauge-fill  { position: absolute; width: 160px; height: 160px; border-radius: 50%; top: 0; left: 0;
    border: 16px solid transparent; border-bottom-color: transparent; border-right-color: transparent; transform-origin: center; }

/* Badge */
.qs-badge { display: inline-block; padding: 0.3rem 0.85rem; border-radius: 4px; font-family: var(--mono); font-size: 0.75rem; font-weight: 500; letter-spacing: 0.05em; text-transform: uppercase; }
.badge-approved { background: rgba(0,212,170,0.15); color: #00d4aa; border: 1px solid rgba(0,212,170,0.3); }
.badge-manual   { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.3); }
.badge-declined { background: rgba(239,68,68,0.15);  color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }

/* Metrics */
.qs-metric-row { display: grid; grid-template-columns: repeat(3,1fr); gap: 0.75rem; margin: 0.75rem 0; }
.qs-metric { background: var(--bg); border: 1px solid var(--border); border-radius: 6px; padding: 0.85rem; text-align: center; }
.qs-metric-val { font-size: 1.4rem; font-weight: 700; font-family: var(--mono); }
.qs-metric-lbl { font-size: 0.6rem; color: var(--muted); font-family: var(--mono); letter-spacing: 0.08em; text-transform: uppercase; margin-top: 0.2rem; }

/* Portfolio metrics */
.port-grid { display: grid; grid-template-columns: repeat(5,1fr); gap: 1rem; margin-bottom: 1.5rem; }
.port-card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 1.25rem; text-align: center; }
.port-val  { font-size: 1.8rem; font-weight: 800; font-family: var(--mono); }
.port-lbl  { font-size: 0.65rem; color: var(--muted); font-family: var(--mono); letter-spacing: 0.08em; text-transform: uppercase; margin-top: 0.3rem; }

/* SHAP */
.shap-row { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.5rem; font-family: var(--mono); font-size: 0.78rem; }
.shap-feature  { width: 170px; color: var(--text); flex-shrink: 0; }
.shap-bar-wrap { flex: 1; height: 5px; background: var(--border); border-radius: 3px; overflow: hidden; }
.shap-bar      { height: 100%; border-radius: 3px; }
.shap-val      { width: 55px; text-align: right; color: var(--muted); font-size: 0.72rem; }

/* Regime */
.regime-panel { display: flex; align-items: center; gap: 1.25rem; background: var(--bg); border: 1px solid var(--border); border-radius: 6px; padding: 0.85rem 1.25rem; margin-bottom: 0.75rem; }
.regime-dot    { width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }
.regime-normal { background: var(--accent); box-shadow: 0 0 6px var(--accent); }
.regime-stress { background: var(--danger);  box-shadow: 0 0 6px var(--danger); }
.regime-text   { font-family: var(--mono); font-size: 0.78rem; }
.regime-label  { color: var(--muted); font-size: 0.62rem; letter-spacing: 0.08em; text-transform: uppercase; }

/* Audit */
.audit-row { display: flex; justify-content: space-between; padding: 0.45rem 0; border-bottom: 1px solid var(--border); font-family: var(--mono); font-size: 0.78rem; }
.audit-key { color: var(--muted); }

/* Risk band bar */
.band-row  { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.6rem; font-family: var(--mono); font-size: 0.78rem; }
.band-name { width: 80px; color: var(--muted); }
.band-bar  { flex: 1; height: 8px; background: var(--border); border-radius: 4px; overflow: hidden; }
.band-fill { height: 100%; border-radius: 4px; }
.band-pct  { width: 45px; text-align: right; }

/* Button */
div.stButton > button {
    background: var(--accent) !important; color: #0a0e17 !important;
    font-family: var(--mono) !important; font-weight: 600 !important;
    letter-spacing: 0.08em !important; text-transform: uppercase !important;
    border: none !important; border-radius: 4px !important;
    padding: 0.6rem 1.5rem !important; width: 100% !important; font-size: 0.8rem !important;
}
div.stButton > button:hover { background: #00b894 !important; }

/* Inputs — light background for visibility */
.stNumberInput input,
.stSelectbox select,
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
div[data-testid="stNumberInputContainer"] input {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    color: #f1f5f9 !important;
    font-family: var(--mono) !important;
    border-radius: 4px !important;
}

/* Labels — dark green */
label,
.stSelectbox label,
.stNumberInput label,
.stSlider label,
.stRadio label,
div[data-testid="stSelectbox"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stSlider"] label,
div[data-testid="stRadio"] label,
div[data-baseweb="select"] label,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] {
    color: #00d4aa !important;
    font-size: 0.78rem !important;
    font-family: var(--mono) !important;
    font-weight: 500 !important;
}

/* Radio and checkbox */
.stRadio > div > label,
.stCheckbox > label {
    color: #e2e8f0 !important;
}

/* Selectbox dropdown text */
div[data-baseweb="select"] span {
    color: #f1f5f9 !important;
    font-family: var(--mono) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: var(--surface) !important; border-radius: 6px; }
.stTabs [data-baseweb="tab"] { color: #94a3b8 !important; font-family: var(--mono) !important; font-size: 0.78rem !important; }
.stTabs [aria-selected="true"] { color: var(--accent) !important; }

/* DataFrame */
.stDataFrame { font-family: var(--mono) !important; font-size: 0.78rem !important; }

/* Nuclear override — force all inputs dark */
input, textarea,
input[type="number"],
input[type="text"],
div[data-testid="stNumberInputContainer"],
div[data-testid="stNumberInputContainer"] input,
div[data-testid="stTextInputRootElement"],
div[data-testid="stTextInputRootElement"] input,
div[data-baseweb="input"] input,
div[data-baseweb="base-input"] input,
div[data-baseweb="base-input"],
[data-baseweb="input"] > div {
    background: #1e293b !important;
    background-color: #1e293b !important;
    color: #f1f5f9 !important;
    -webkit-text-fill-color: #f1f5f9 !important;
    border-color: #334155 !important;
}

input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus,
input:-webkit-autofill:active {
    -webkit-box-shadow: 0 0 0 1000px #1e293b inset !important;
    -webkit-text-fill-color: #f1f5f9 !important;
    caret-color: #f1f5f9 !important;
}

/* Streamlit number input specific fix */
div[data-testid="stNumberInput"] input,
div[data-testid="stNumberInput"] div,
div[class*="stNumberInput"] input,
section[data-testid="stSidebar"] input,
div[role="spinbutton"],
input[aria-label],
.st-emotion-cache-1n76uvr,
.st-emotion-cache-vk3wp9,
.st-emotion-cache-1xw8zd7,
[class*="st-emotion-cache"] input {
    background: #1e293b !important;
    background-color: #1e293b !important;
    color: #f1f5f9 !important;
    -webkit-text-fill-color: #f1f5f9 !important;
    opacity: 1 !important;
}

/* Target the wrapper div that Streamlit wraps inputs in */
div[data-testid="stNumberInput"] > div > div {
    background: transparent !important;
    border: 1px solid #334155 !important;
}
/* Basic Info tab — select and number input accent */
div[data-testid="stSelectbox"] label,
div[data-testid="stNumberInput"] label {
    color: #00d4aa !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)
# ── Config ────────────────────────────────────────────────────
BASE_URL = os.getenv("QUANTSCORE_API_URL", "http://127.0.0.1:8000")
API_KEY  = os.getenv("QUANTSCORE_API_KEY", "")
LGD      = 0.45  # Loss Given Default — standard retail credit assumption

# ── Header ────────────────────────────────────────────────────
st.markdown("""
<div class="qs-header">
    <div class="qs-logo"></div>
    <div>
        <div class="qs-title">Quant<span>Score</span></div>
        <div class="qs-subtitle">Credit Risk Intelligence Platform · v2.0</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────
def score_applicant(payload: dict, explain: bool = False) -> dict | None:
    endpoint = "explain" if explain else "predict"
    try:
        r = requests.post(
            f"{BASE_URL}/{endpoint}",
            json=payload,
            headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
            timeout=15,
        )
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def score_batch(applicants: list[dict]) -> dict | None:
    try:
        r = requests.post(
            f"{BASE_URL}/batch_predict",
            json={"applicants": applicants},
            headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
            timeout=60,
        )
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def get_regime() -> dict:
    try:
        r = requests.get(
            f"{BASE_URL}/regime/current",
            headers={"x-api-key": API_KEY},
            timeout=5,
        )
        return r.json() if r.status_code == 200 else {}
    except Exception:
        return {}


def band_label(pd_val: float) -> str:
    if pd_val < 0.20:  return "Low"
    if pd_val < 0.40:  return "Medium"
    return "High"


def expected_loss(pd_val: float, loan_amount: float) -> float:
    return pd_val * LGD * loan_amount


def score_color(score: int) -> str:
    if score >= 750: return "#00d4aa"
    if score >= 600: return "#f59e0b"
    return "#ef4444"


def badge_class(band: str) -> str:
    return {"approved": "badge-approved", "manual_review": "badge-manual"}.get(band, "badge-declined")


def gauge_html(score: int) -> str:
    """SVG semicircle gauge for credit score."""
    pct    = (score - 300) / 550
    angle  = pct * 180
    color  = score_color(score)
    r, cx, cy = 70, 90, 90
    import math
    rad = math.radians(180 + angle)
    x   = cx + r * math.cos(rad)
    y   = cy + r * math.sin(rad)
    large = 1 if angle > 180 else 0
    return f"""
    <svg width="180" height="100" viewBox="0 0 180 100">
      <path d="M 20 90 A 70 70 0 0 1 160 90" fill="none" stroke="#1e2d45" stroke-width="14" stroke-linecap="round"/>
      <path d="M 20 90 A 70 70 0 {large} 1 {x:.1f} {y:.1f}" fill="none" stroke="{color}" stroke-width="14" stroke-linecap="round"/>
      <text x="90" y="82" text-anchor="middle" fill="{color}" font-size="26" font-weight="800" font-family="DM Mono,monospace">{score}</text>
      <text x="90" y="97" text-anchor="middle" fill="#64748b" font-size="9" font-family="DM Mono,monospace">CREDIT SCORE</text>
    </svg>"""


# ── Main tabs ─────────────────────────────────────────────────
tab_score, tab_batch, tab_portfolio = st.tabs([
    "⬡  Single Score",
    "⬡  Batch Upload",
    "⬡  Portfolio Dashboard",
])


# ══════════════════════════════════════════════════════════════
# TAB 1 — SINGLE SCORE
# ══════════════════════════════════════════════════════════════
with tab_score:
    col_form, col_result = st.columns([1, 1], gap="large")

    with col_form:
        st.markdown('<div class="qs-section">Applicant Profile</div>', unsafe_allow_html=True)

        t_basic, t_fin, t_hist = st.tabs(["Basic Info", "Financials", "Credit History"])

        with t_basic:
            age        = st.number_input("Age", 18, 75, 35)
            gender     = st.selectbox("Gender", [1, 0], format_func=lambda x: "Male" if x else "Female")
            married    = st.selectbox("Marital Status", [1, 0], format_func=lambda x: "Married" if x else "Single")
            education  = st.selectbox("Education", [1, 0], format_func=lambda x: "Graduate" if x else "Not Graduate")
            dependents = st.number_input("Dependents", 0, 10, 2)
            self_emp   = st.selectbox("Employment", [0, 1], format_func=lambda x: "Salaried" if x == 0 else "Self-Employed")

        with t_fin:
            monthly_income = st.number_input("Monthly Income (₦)",    1.0, value=300_000.0, step=10_000.0)
            loan_amount    = st.number_input("Loan Amount (₦)",        1.0, value=450_000.0, step=10_000.0)
            loan_duration  = st.number_input("Loan Duration (months)", 1,   value=18)
            savings        = st.number_input("Savings (₦)",            0.0, value=40_000.0,  step=5_000.0)
            transactions   = st.number_input("Transactions / Month",   0,   value=8)

            dti       = loan_amount / monthly_income if monthly_income > 0 else 0
            dti_color = "#00d4aa" if dti < 1.4 else ("#f59e0b" if dti < 1.6 else "#ef4444")
            dti_label = "✓ LOW" if dti < 1.4 else ("⚠ BORDERLINE" if dti < 1.6 else "✗ HIGH")
            st.markdown(f"""
            <div style="background:var(--bg);border:1px solid var(--border);border-radius:6px;
                        padding:0.65rem 1rem;margin-top:0.5rem;font-family:var(--mono);font-size:0.78rem;">
                <span style="color:var(--muted);">DEBT-TO-INCOME</span>
                <span style="float:right;color:{dti_color};font-weight:600;">{dti:.2f}x &nbsp; {dti_label}</span>
            </div>""", unsafe_allow_html=True)

            el_preview = expected_loss(0.35, loan_amount)
            st.markdown(f"""
            <div style="background:var(--bg);border:1px solid var(--border);border-radius:6px;
                        padding:0.65rem 1rem;margin-top:0.5rem;font-family:var(--mono);font-size:0.78rem;">
                <span style="color:var(--muted);">EST. EXPECTED LOSS (avg PD)</span>
                <span style="float:right;color:var(--warning);">₦{el_preview:,.0f}</span>
            </div>""", unsafe_allow_html=True)

        with t_hist:
            credit_history  = st.selectbox("Credit History", [1, 0], format_func=lambda x: "Good (1+ year)" if x else "None / Poor")
            prev_defaults   = st.selectbox("Previous Defaults", [0, 1, 2, 3])
            repayment_ratio = st.slider("Repayment Ratio", 0.0, 1.0, 0.5, 0.05)

        st.markdown("<br>", unsafe_allow_html=True)
        mode      = st.radio("Mode", ["Standard", "With SHAP Explanation"], horizontal=True)
        submitted = st.button("⬡  Score Applicant", key="score_btn")

    with col_result:
        st.markdown('<div class="qs-section">Risk Assessment</div>', unsafe_allow_html=True)

        if not submitted:
            st.markdown("""
            <div class="qs-card" style="text-align:center;padding:3rem 2rem;border-style:dashed;">
                <div style="font-size:2rem;margin-bottom:1rem;opacity:0.3;">⬡</div>
                <div style="font-family:var(--mono);color:var(--muted);font-size:0.82rem;">
                    Fill in the applicant profile and click<br>Score Applicant to see results.
                </div>
            </div>""", unsafe_allow_html=True)

        else:
            if not API_KEY:
                st.error("API key not configured. Set QUANTSCORE_API_KEY environment variable.")
                st.stop()

            payload = {
                "Age": age, "Gender": gender, "MonthlyIncome": monthly_income,
                "LoanAmount": loan_amount, "LoanDuration": loan_duration,
                "Dependents": dependents, "CreditHistory": credit_history,
                "Married": married, "Education": education, "SelfEmployed": self_emp,
                "Savings": savings, "TransactionsPerMonth": transactions,
                "PreviousDefaults": prev_defaults, "RepaymentRatio": repayment_ratio,
            }

            with st.spinner("Analysing credit risk..."):
                res = score_applicant(payload, explain=(mode == "With SHAP Explanation"))

            if not res:
                st.error("API request failed. Make sure uvicorn is running.")
                st.stop()

            prob      = res.get("probability", 0)
            score     = res.get("credit_score", 300)
            band      = res.get("decision_band", "declined")
            risk_cat  = res.get("risk_category", "High")
            regime    = res.get("regime", "normal")
            threshold = res.get("threshold", "—")
            el        = expected_loss(prob, loan_amount)

            # Gauge
            st.markdown(f"""
            <div class="qs-card" style="text-align:center;">
                {gauge_html(score)}
                <div style="margin-top:0.5rem;">
                    <span class="qs-badge {badge_class(band)}">{band.replace('_',' ').upper()}</span>
                </div>
            </div>""", unsafe_allow_html=True)

            # Metrics
            sc = score_color(score)
            st.markdown(f"""
            <div class="qs-metric-row">
                <div class="qs-metric">
                    <div class="qs-metric-val" style="color:{sc};">{prob:.1%}</div>
                    <div class="qs-metric-lbl">Default PD</div>
                </div>
                <div class="qs-metric">
                    <div class="qs-metric-val">{risk_cat}</div>
                    <div class="qs-metric-lbl">Risk Band</div>
                </div>
                <div class="qs-metric">
                    <div class="qs-metric-val" style="color:var(--warning);">₦{el:,.0f}</div>
                    <div class="qs-metric-lbl">Expected Loss</div>
                </div>
            </div>""", unsafe_allow_html=True)

            # Portfolio segment
            seg_color = {"Low": "#00d4aa", "Medium": "#f59e0b", "High": "#ef4444"}.get(risk_cat, "#64748b")
            observed_dr = {"Low": "~4%", "Medium": "~27%", "High": "~82%"}.get(risk_cat, "—")
            st.markdown(f"""
            <div style="background:var(--bg);border:1px solid var(--border);border-radius:6px;
                        padding:0.75rem 1rem;margin-bottom:0.75rem;font-family:var(--mono);font-size:0.78rem;">
                <span style="color:var(--muted);">PORTFOLIO SEGMENT</span>
                <span style="float:right;color:{seg_color};font-weight:600;">
                    {risk_cat.upper()} RISK &nbsp;·&nbsp; Observed default rate {observed_dr}
                </span>
            </div>""", unsafe_allow_html=True)

            # Regime
            rdot = "regime-normal" if regime == "normal" else "regime-stress"
            st.markdown(f"""
            <div class="regime-panel">
                <div class="regime-dot {rdot}"></div>
                <div class="regime-text">
                    <div class="regime-label">Market Regime</div>
                    <div style="margin-top:0.15rem;">{regime.upper()} — Approval threshold: {threshold}</div>
                </div>
            </div>""", unsafe_allow_html=True)

            # SHAP
            if "top_risk_drivers" in res:
                st.markdown('<div class="qs-section" style="margin-top:1rem;">Top Risk Drivers</div>', unsafe_allow_html=True)
                drivers  = res["top_risk_drivers"]
                max_abs  = max(abs(d["impact"]) for d in drivers) or 1
                for d in drivers:
                    impact = d["impact"]
                    pct    = abs(impact) / max_abs * 100
                    color  = "#ef4444" if impact > 0 else "#00d4aa"
                    sign   = "↑ risk" if impact > 0 else "↓ risk"
                    st.markdown(f"""
                    <div class="shap-row">
                        <div class="shap-feature">{d['feature']}</div>
                        <div class="shap-bar-wrap"><div class="shap-bar" style="width:{pct}%;background:{color};"></div></div>
                        <div class="shap-val" style="color:{color};">{sign}</div>
                    </div>""", unsafe_allow_html=True)

            # Audit trail
            st.markdown('<div class="qs-section" style="margin-top:1rem;">Audit Trail</div>', unsafe_allow_html=True)
            for key, val in [
                ("Base Probability",  f"{res.get('base_probability',0):.4f}"),
                ("Regime Adjustment", f"{res.get('regime_adjustment',0):+.4f}"),
                ("Final PD",          f"{prob:.4f}"),
                ("Threshold",         f"{threshold}"),
                ("Decision",          res.get("decision","—").upper()),
                ("Confidence",        res.get("confidence","—")),
            ]:
                st.markdown(f"""
                <div class="audit-row">
                    <span class="audit-key">{key}</span>
                    <span class="audit-value">{val}</span>
                </div>""", unsafe_allow_html=True)

            st.markdown(f"""
            <div style="margin-top:0.75rem;padding:0.65rem 1rem;background:var(--bg);
                        border:1px solid var(--border);border-radius:6px;
                        font-family:var(--mono);font-size:0.72rem;color:var(--muted);">
                {res.get('decision_reason','')}
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# TAB 2 — BATCH UPLOAD
# ══════════════════════════════════════════════════════════════
with tab_batch:
    st.markdown('<div class="qs-section">Batch Scoring — Upload CSV</div>', unsafe_allow_html=True)

    REQUIRED_COLS = [
        "Age", "Gender", "MonthlyIncome", "LoanAmount", "LoanDuration",
        "Dependents", "CreditHistory", "Married", "Education", "SelfEmployed",
        "Savings", "TransactionsPerMonth", "PreviousDefaults", "RepaymentRatio",
    ]

    # Template download
    template_df = pd.DataFrame([{
        "Age": 35, "Gender": 1, "MonthlyIncome": 300000, "LoanAmount": 450000,
        "LoanDuration": 18, "Dependents": 2, "CreditHistory": 1, "Married": 1,
        "Education": 1, "SelfEmployed": 0, "Savings": 40000,
        "TransactionsPerMonth": 8, "PreviousDefaults": 0, "RepaymentRatio": 0.5,
    }] * 20)

    col_a, col_b = st.columns([2, 1])
    with col_a:
        uploaded = st.file_uploader(
            "Upload CSV with applicant data (max 100 rows)",
            type=["csv"],
            help=f"Required columns: {', '.join(REQUIRED_COLS)}",
        )
    with col_b:
        st.markdown("<br>", unsafe_allow_html=True)
        csv_bytes = template_df.to_csv(index=False).encode()
        st.download_button(
            "⬡  Download Template CSV",
            data=csv_bytes,
            file_name="quantscore_template.csv",
            mime="text/csv",
        )

    if uploaded:
        try:
            df_input = pd.read_csv(uploaded)
        except Exception as e:
            st.error(f"Could not read CSV: {e}")
            st.stop()

        missing = [c for c in REQUIRED_COLS if c not in df_input.columns]
        if missing:
            st.error(f"Missing columns: {missing}")
            st.stop()

        df_input = df_input[REQUIRED_COLS].head(100)
        st.markdown(f"**{len(df_input)} applicants loaded.** Preview:")
        st.dataframe(df_input.head(5), use_container_width=True)

        if st.button("⬡  Score All Applicants", key="batch_btn"):
            if not API_KEY:
                st.error("API key not configured.")
                st.stop()

            applicants = df_input.to_dict(orient="records")

            with st.spinner(f"Scoring {len(applicants)} applicants..."):
                batch_res = score_batch(applicants)

            if not batch_res:
                st.error("Batch scoring failed. Check the API is running.")
                st.stop()

            results = batch_res["results"]
            st.write(f"API returned: {len(results)} results")
            st.write(f"Input CSV had: {len(df_input)} rows")

            rows = []
            for i, r in enumerate(results):
                loan_amt = df_input.iloc[i]["LoanAmount"]
                pd_val   = r["probability"]
                rows.append({
    "Index":          r["applicant_index"],
    "Request ID":     r["request_id"],
    "Credit Score":   r["credit_score"],
    "PD":             round(pd_val, 4),
    "Risk Category":  r["risk_category"],
    "Recommendation": r["decision_band"].replace("_", " ").title(),
    "Final Decision": r["decision"].title(),
    "Regime":         r["regime"],
    "Threshold":      r["threshold"],
    "Expected Loss":  round(expected_loss(pd_val, loan_amt), 0),
})

            df_results = pd.DataFrame(rows)

            st.markdown('<div class="qs-section" style="margin-top:1.5rem;">Results</div>', unsafe_allow_html=True)
            st.dataframe(df_results, use_container_width=True)

            # Summary stats
            approved  = (df_results["Final Decision"] == "approved").sum()
            declined  = (df_results["Final Decision"] == "declined").sum()
            review    = (df_results["Recommendation"] == "manual_review").sum()
            avg_pd    = df_results["PD"].mean()
            total_el  = df_results["Expected Loss"].sum()

            st.markdown(f"""
            <div class="port-grid" style="grid-template-columns:repeat(5,1fr);margin-top:1rem;">
                <div class="port-card"><div class="port-val" style="color:#00d4aa;">{approved}</div><div class="port-lbl">Approved</div></div>
                <div class="port-card"><div class="port-val" style="color:#f59e0b;">{review}</div><div class="port-lbl">Manual Review</div></div>
                <div class="port-card"><div class="port-val" style="color:#ef4444;">{declined}</div><div class="port-lbl">Declined</div></div>
                <div class="port-card"><div class="port-val">{avg_pd:.1%}</div><div class="port-lbl">Avg PD</div></div>
                <div class="port-card"><div class="port-val" style="color:var(--warning);">₦{total_el:,.0f}</div><div class="port-lbl">Total Exp. Loss</div></div>
            </div>""", unsafe_allow_html=True)

            # Download results
            csv_out = df_results.to_csv(index=False).encode()
            st.download_button(
                "⬡  Download Results CSV",
                data=csv_out,
                file_name="quantscore_results.csv",
                mime="text/csv",
            )


# ══════════════════════════════════════════════════════════════
# TAB 3 — PORTFOLIO DASHBOARD
# ══════════════════════════════════════════════════════════════
with tab_portfolio:
    st.markdown('<div class="qs-section">Portfolio Analytics</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="qs-card" style="border-style:dashed;margin-bottom:1.5rem;">
        <div style="font-family:var(--mono);font-size:0.78rem;color:var(--muted);">
            Score a batch of applicants in the <strong style="color:var(--text);">Batch Upload</strong> tab first,
            then return here to view portfolio analytics. The dashboard below shows model validation benchmarks
            from the training evaluation.
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Model validation benchmarks ──────────────────────────
    st.markdown('<div class="qs-section">Model Validation — Band Performance</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("""
        <div class="qs-card">
            <div style="font-family:var(--mono);font-size:0.72rem;color:var(--muted);margin-bottom:1rem;
                        letter-spacing:0.08em;text-transform:uppercase;">
                Observed Default Rate by Risk Band
            </div>""", unsafe_allow_html=True)

        bands_data = [
            ("Low",    4.0,  "#00d4aa", 4.0/82.0),
            ("Medium", 27.1, "#f59e0b", 27.1/82.0),
            ("High",   82.0, "#ef4444", 1.0),
        ]
        for name, rate, color, pct in bands_data:
            st.markdown(f"""
            <div class="band-row">
                <div class="band-name">{name}</div>
                <div class="band-bar"><div class="band-fill" style="width:{pct*100:.0f}%;background:{color};"></div></div>
                <div class="band-pct" style="color:{color};">{rate:.1f}%</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="qs-card">
            <div style="font-family:var(--mono);font-size:0.72rem;color:var(--muted);margin-bottom:1rem;
                        letter-spacing:0.08em;text-transform:uppercase;">
                Model Performance Metrics
            </div>""", unsafe_allow_html=True)

        metrics = [
            ("ROC-AUC",     "0.9516", "#00d4aa"),
            ("Brier Score", "0.0819", "#00d4aa"),
            ("F1 Score",    "0.836",  "#00d4aa"),
            ("Accuracy",    "89.0%",  "#00d4aa"),
            ("Precision",   "84.3%",  "#00d4aa"),
            ("Recall",      "83.0%",  "#00d4aa"),
        ]
        for key, val, color in metrics:
            st.markdown(f"""
            <div class="audit-row">
                <span class="audit-key">{key}</span>
                <span class="audit-value" style="color:{color};">{val}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Decision boundary ─────────────────────────────────────
    st.markdown('<div class="qs-section" style="margin-top:1.5rem;">Decision Boundary — DTI Sweep</div>', unsafe_allow_html=True)

    dti_data = {
        "DTI":  [0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5],
        "PD":   [0.0128,0.0128,0.0128,0.0128,0.0128,0.0202,0.0412,0.1023,0.1276,0.2093,0.3282,
                 0.5000,0.5233,0.6761,0.7044,0.8478,0.9009,0.9153,0.9368,0.9764,0.9764],
    }
    df_dti = pd.DataFrame(dti_data)
    st.line_chart(df_dti.set_index("DTI"), use_container_width=True, color=["#00d4aa"])

    st.markdown("""
    <div style="font-family:var(--mono);font-size:0.72rem;color:var(--muted);margin-top:0.5rem;">
        DTI &lt; 1.4 → Low risk (Approve) &nbsp;·&nbsp;
        DTI 1.4–1.6 → Borderline (Manual Review) &nbsp;·&nbsp;
        DTI &gt; 1.6 → High risk (Decline)
    </div>""", unsafe_allow_html=True)

    # ── Regime status ─────────────────────────────────────────
    st.markdown('<div class="qs-section" style="margin-top:1.5rem;">Live Market Regime</div>', unsafe_allow_html=True)

    regime_data = get_regime()
    if regime_data:
        r_label = regime_data.get("regime", "—").upper()
        r_vol   = regime_data.get("volatility", 0)
        r_ret   = regime_data.get("mean_return", 0)
        r_risk  = regime_data.get("risk_level", "—").upper()
        r_probs = regime_data.get("market_state_probability", {})
        rdot    = "regime-normal" if regime_data.get("regime") == "normal" else "regime-stress"

        st.markdown(f"""
        <div class="regime-panel">
            <div class="regime-dot {rdot}"></div>
            <div class="regime-text">
                <div class="regime-label">Current Regime</div>
                <div style="margin-top:0.15rem;">{r_label} &nbsp;·&nbsp; Risk Level: {r_risk} &nbsp;·&nbsp;
                    Volatility: {r_vol:.4f} &nbsp;·&nbsp; Mean Return: {r_ret:.4f}
                </div>
            </div>
        </div>
        <div class="qs-metric-row" style="grid-template-columns:repeat(2,1fr);">
            <div class="qs-metric">
                <div class="qs-metric-val" style="color:#00d4aa;">{r_probs.get('normal',0):.1%}</div>
                <div class="qs-metric-lbl">Normal Probability</div>
            </div>
            <div class="qs-metric">
                <div class="qs-metric-val" style="color:#ef4444;">{r_probs.get('stress',0):.1%}</div>
                <div class="qs-metric-lbl">Stress Probability</div>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.warning("Could not fetch regime data. Make sure the API is running.")

# ── Footer ────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:2rem;padding-top:1.25rem;border-top:1px solid var(--border);
            font-family:var(--mono);font-size:0.68rem;color:var(--muted);
            display:flex;justify-content:space-between;">
    <span>QuantScore Credit Risk Intelligence · v2.0</span>
    <span>For internal use and demonstration only · LGD assumption: 45%</span>
</div>""", unsafe_allow_html=True)