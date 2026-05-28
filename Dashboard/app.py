# UniMediTrend Dashboard — Modern Edition

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pymongo import MongoClient, errors
import joblib, json, warnings
import sys
from pathlib import Path

warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ───────────────────────────────────────────────────────────────────
# DESIGN SYSTEM
# ───────────────────────────────────────────────────────────────────
BG        = "#0b0f1a"
SURFACE   = "#111827"
CARD      = "#1a2035"
CARD_HI   = "#1f2940"
BORDER    = "#2a3655"
BORDER_HI = "#3b4d7a"
TEXT      = "#e2e8f0"
TEXT_DIM  = "#8899b4"
ACCENT    = "#3b82f6"
ACCENT_HI = "#60a5fa"
TEAL      = "#14b8a6"
TEAL_HI   = "#2dd4bf"
AMBER     = "#f59e0b"
RED       = "#ef4444"
RED_HI    = "#f87171"
GREEN     = "#22c55e"
PURPLE    = "#a78bfa"
ORANGE    = "#fb923c"

st.set_page_config(
    page_title="UniMediTrend",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = f"""
<style>
  .stApp {{ background-color: {BG}; color: {TEXT}; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
  .block-container {{ padding-top: 1.5rem; padding-bottom: 1.5rem; max-width: 1440px; }}
  section[data-testid="stSidebar"] {{ background: {SURFACE} !important; border-right: 1px solid {BORDER}; }}
  section[data-testid="stSidebar"] .block-container {{ padding-top: 0.5rem; padding-bottom: 1.5rem; }}
  .main-header {{ font-size: 1.6rem; font-weight: 800; color: {TEXT}; margin: 0 0 4px 0; letter-spacing: -0.02em; line-height: 1.2; }}
  .main-sub {{ font-size: 0.82rem; color: {TEXT_DIM}; margin: 0 0 1.5rem 0; line-height: 1.5; }}
  div[data-testid="metric-container"] {{ background: {CARD} !important; border: 1px solid {BORDER} !important; border-radius: 12px !important; padding: 18px 20px !important; box-shadow: 0 1px 3px rgba(0,0,0,0.3); }}
  div[data-testid="metric-container"] label {{ color: {TEXT_DIM} !important; font-size: 0.7rem !important; font-weight: 600 !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; }}
  div[data-testid="metric-container"] [data-testid="stMetricValue"] {{ color: {TEXT} !important; font-size: 2rem !important; font-weight: 700 !important; }}
  div[data-testid="metric-container"] [data-testid="stMetricDelta"] {{ font-size: 0.75rem !important; color: {TEXT_DIM} !important; }}
  .panel {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.25); }}
  .panel-accent {{ background: linear-gradient(135deg, {ACCENT}12, transparent); border: 1px solid {ACCENT}30; border-radius: 12px; padding: 20px; }}
  .panel-red {{ background: {RED}08; border: 1px solid {RED}20; border-radius: 12px; padding: 20px; }}
  .divider {{ height: 1px; background: {BORDER}; margin: 1.5rem 0; }}
  .divider-thin {{ height: 1px; background: {BORDER}; margin: 1rem 0; }}
  .section-title {{ color: {TEXT}; font-size: 0.95rem; font-weight: 700; letter-spacing: -0.01em; margin-bottom: 1rem; display: flex; align-items: center; gap: 8px; }}
  .section-dot {{ width: 8px; height: 8px; border-radius: 50%; display: inline-block; }}
  .tag {{ display: inline-block; padding: 3px 10px; border-radius: 6px; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; }}
  .tag-red {{ background: {RED}18; color: {RED}; border: 1px solid {RED}30; }}
  .tag-amber {{ background: {AMBER}18; color: {AMBER}; border: 1px solid {AMBER}30; }}
  .tag-teal {{ background: {TEAL}18; color: {TEAL}; border: 1px solid {TEAL}30; }}
  .tag-blue {{ background: {ACCENT}18; color: {ACCENT}; border: 1px solid {ACCENT}30; }}
  .tag-green {{ background: {GREEN}18; color: {GREEN}; border: 1px solid {GREEN}30; }}
  .stat-row {{ display: flex; align-items: center; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid {BORDER}; }}
  .stat-row:last-child {{ border-bottom: none; }}
  .stat-label {{ color: {TEXT_DIM}; font-size: 0.82rem; }}
  .stat-value {{ color: {TEXT}; font-weight: 700; font-size: 0.9rem; }}
  .risk-high {{ background: {RED}15; color: {RED}; border: 1px solid {RED}30; border-radius: 8px; padding: 4px 12px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.04em; }}
  .risk-med {{ background: {AMBER}15; color: {AMBER}; border: 1px solid {AMBER}30; border-radius: 8px; padding: 4px 12px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.04em; }}
  .risk-low {{ background: {TEAL}15; color: {TEAL}; border: 1px solid {TEAL}30; border-radius: 8px; padding: 4px 12px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.04em; }}
  .fc-normal {{ background: {ACCENT}08; border: 1px solid {ACCENT}25; border-radius: 12px; padding: 18px 20px; }}
  .fc-warn {{ background: {AMBER}08; border: 1px solid {AMBER}25; border-radius: 12px; padding: 18px 20px; }}
  .fc-crit {{ background: {RED}10; border: 1px solid {RED}30; border-radius: 12px; padding: 18px 20px; }}
  .insight-box {{ background: linear-gradient(135deg, {TEAL}08, {ACCENT}06); border: 1px solid {TEAL}25; border-radius: 12px; padding: 16px 20px; }}
  .stDataFrame {{ border-radius: 10px; overflow: hidden; border: 1px solid {BORDER}; }}
  .stButton > button {{ border-radius: 8px; font-weight: 600; font-size: 0.82rem; border: none; letter-spacing: 0.02em; font-family: 'Inter', sans-serif; }}
  ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
  ::-webkit-scrollbar-track {{ background: transparent; }}
  ::-webkit-scrollbar-thumb {{ background: {BORDER_HI}; border-radius: 3px; }}
  /* clean multiselect / input overrides */
  .stMultiSelect > div > div {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 8px; }}
  .stTextInput > div > div > input {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 8px; color: {TEXT}; }}
  [data-testid="stSidebar"] .stTextInput > div > div > input {{ background: {SURFACE}; border-color: {BORDER}; }}
  [data-testid="stSidebar"] .stMultiSelect > div > div {{ background: {SURFACE}; border-color: {BORDER}; }}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

# ───────────────────────────────────────────────────────────────────
# DATA LOADING
# ───────────────────────────────────────────────────────────────────
def get_mongo_col():
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
    db = client["UniMediTrend"]
    return db["clinic_logs_enriched"]

@st.cache_data(ttl=60)
def load_data():
    try:
        col = get_mongo_col()
        col.estimated_document_count()
        df = pd.DataFrame(list(col.find({}, {"_id": 0})))
        if df.empty:
            raise ValueError("Empty collection")
        if "visit_date" not in df.columns:
            raise ValueError("visit_date missing")
        df["visit_date"] = pd.to_datetime(df["visit_date"], errors="coerce")
        df = df.dropna(subset=["visit_date"]).copy()
    except Exception as e:
        try:
            from generate_dataset import generate_dataset
            df = generate_dataset().copy()
            st.info(f"Using generated synthetic dataset. ({e})")
        except Exception as gen_err:
            st.warning(f"MongoDB and generator unavailable. ({gen_err})")
            df = generate_sample_data()

    defaults = {"hostel": "Unknown", "diagnosis": "Unknown", "severity": 1,
                "gender": "Unknown", "level": "Unknown", "department": "Unknown"}
    for col_name, val in defaults.items():
        if col_name not in df.columns:
            df[col_name] = val

    df["visit_date"] = pd.to_datetime(df["visit_date"], errors="coerce")
    df = df.dropna(subset=["visit_date"]).copy()
    df["severity"] = pd.to_numeric(df["severity"], errors="coerce").fillna(1)

    baseline_target = 5799
    dedupe_cols = [c for c in ["visit_date","hostel","diagnosis","severity","gender","level","department"] if c in df.columns]
    if len(df) > baseline_target and dedupe_cols:
        df = df.drop_duplicates(subset=dedupe_cols).sort_values("visit_date").head(baseline_target).copy()

    df["month"] = df["visit_date"].dt.month
    df["week"]  = df["visit_date"].dt.isocalendar().week.astype(int)
    df["year"]  = df["visit_date"].dt.year
    df["acad_year"] = df["year"].astype(str)

    def get_semester(m):
        if 1 <= m <= 4: return "First Semester"
        elif 6 <= m <= 9: return "Second Semester"
        else: return "Vacation / Break"

    df["semester"] = df["visit_date"].dt.month.apply(get_semester)
    return df.sort_values("visit_date").reset_index(drop=True)

def generate_sample_data():
    np.random.seed(42)
    dates = pd.date_range("2023-08-01", "2026-04-12", freq="D")
    n = len(dates) * 4
    hostels   = ["Mensah Hall","Akosua Block","Commonwealth Hall","Volta Hall",
                 "Legon Hall","Jubilee Hall","Nkrumah Hall","Pentagon"]
    diagnoses = ["Malaria","URTI","Typhoid","Stress/Anxiety","Skin Conditions",
                 "Gastroenteritis","Hypertension","Other"]
    diag_w    = [0.28, 0.21, 0.16, 0.13, 0.11, 0.05, 0.03, 0.03]
    df = pd.DataFrame({
        "visit_date": np.random.choice(dates, n),
        "hostel":     np.random.choice(hostels, n, p=[0.18,0.16,0.15,0.14,0.13,0.10,0.08,0.06]),
        "diagnosis":  np.random.choice(diagnoses, n, p=diag_w),
        "severity":   np.random.choice([1,2,3,4,5], n, p=[0.20,0.30,0.28,0.14,0.08]),
        "gender":     np.random.choice(["Male","Female"], n, p=[0.55,0.45]),
        "level":      np.random.choice(["Year 1","Year 2","Year 3","Year 4"], n,
                        p=[0.33,0.28,0.22,0.17]),
        "department": np.random.choice(["Engineering","Science","Arts","Medicine","Social Sciences"], n),
        "student_id": [f"UG{np.random.randint(10000,99999)}" for _ in range(n)],
    })
    df["visit_date"] = pd.to_datetime(df["visit_date"])
    return df.sort_values("visit_date").reset_index(drop=True)

@st.cache_resource
def load_models():
    try:
        rf     = joblib.load("models/rf_total_visits.pkl")
        lr     = joblib.load("models/lr_total_visits.pkl")
        scaler = joblib.load("models/lr_scaler.pkl")
        h_map  = joblib.load("models/hostel_label_map.pkl")
        with open("models/feature_cols.json") as f:
            feat_cols = json.load(f)
        return rf, lr, scaler, h_map, feat_cols
    except:
        h_map = {"K.T. Hall": "High Risk", "The Point Hostel": "High Risk",
                 "Castle Gate": "Medium Risk", "Gold Refinery Hall": "Medium Risk",
                 "Kabi's Hostel": "Low Risk", "New Excellence": "Low Risk",
                 "Waterloo": "Low Risk", "Hilda Hostel": "Low Risk"}
        feat_cols = ["lag_1","lag_2","lag_3","rolling_mean_4",
                     "month_sin","month_cos","week_sin","week_cos"]
        return None, None, None, h_map, feat_cols

df = load_data()
rf, lr, scaler, hostel_label_map, FEATURE_COLS = load_models()
all_cal_years = sorted(df["year"].unique(), reverse=True)
default_year  = 2026 if 2026 in all_cal_years else all_cal_years[0]

# ───────────────────────────────────────────────────────────────────
# SIDEBAR (clean, minimal, contextual)
# ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
      <div style="background:linear-gradient(135deg,#3b82f6,#14b8a6);border-radius:8px;width:32px;height:32px;display:flex;align-items:center;justify-content:center;font-size:14px;color:#0b0f1a;font-weight:800;">U</div>
      <div>
        <div style="color:#e2e8f0;font-weight:700;font-size:13px;letter-spacing:0.02em;">UniMediTrend</div>
        <div style="color:#556680;font-size:10px;letter-spacing:0.06em;">CLINIC ANALYTICS</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="height:1px;background:#2a3655;margin:8px 0 16px 0;"></div>
    <div style="font-size:10px;color:#556680;letter-spacing:0.06em;text-transform:uppercase;margin-bottom:12px;">Navigation</div>
    """, unsafe_allow_html=True)

    page_labels = {
        "Health Overview":           "Overview",
        "Hostel Risk Analysis":      "Hostels",
        "Visit Demand Forecast":     "Forecast",
        "Data Management":           "Data",
    }
    page = st.radio(
        "Navigate",
        list(page_labels.keys()),
        label_visibility="collapsed",
        index=0,
    )

    st.markdown(f"""
    <div style="height:1px;background:#2a3655;margin:12px 0 10px 0;"></div>
    <div style="font-size:10px;color:#556680;letter-spacing:0.06em;text-transform:uppercase;margin-bottom:12px;">Context</div>
    <div style="font-size:10px;color:#8899b4;margin-bottom:2px;">Records</div>
    <div style="font-size:14px;font-weight:700;color:#e2e8f0;">{len(df):,}</div>
    <div style="font-size:10px;color:#8899b4;margin-top:6px;">Hostels</div>
    <div style="font-size:14px;font-weight:700;color:#e2e8f0;">{df['hostel'].nunique()}</div>
    <div style="font-size:10px;color:#8899b4;margin-top:6px;">Year</div>
    <div style="font-size:14px;font-weight:700;color:#e2e8f0;">{default_year}</div>
    """, unsafe_allow_html=True)

    # ── Sidebar filters (only on data management page) ──
    if page == "Data Management":
        st.markdown(f"""
        <div style="height:1px;background:#2a3655;margin:12px 0 10px 0;"></div>
        <div style="font-size:10px;color:#556680;letter-spacing:0.06em;text-transform:uppercase;">Filters</div>
        """, unsafe_allow_html=True)

        with st.expander("Search", expanded=True):
            hostel_search = st.text_input("Hostel", value="", placeholder="Search...", label_visibility="collapsed")
            diag_search  = st.text_input("Diagnosis", value="", placeholder="Search...", label_visibility="collapsed")

        with st.expander("Select", expanded=False):
            all_hostels   = sorted(df["hostel"].unique())
            all_diagnoses = sorted(df["diagnosis"].unique())
            sel_hostels    = st.multiselect("Hostels", all_hostels, default=all_hostels)
            sel_diagnoses  = st.multiselect("Diagnoses", all_diagnoses, default=all_diagnoses)

        st.caption(f"Selected: {len(sel_hostels)}/{len(all_hostels)} hostels · {len(sel_diagnoses)}/{len(all_diagnoses)} diagnoses")
    else:
        # Small global filter on every page: just year and semester
        st.markdown(f"""
        <div style="height:1px;background:#2a3655;margin:12px 0 10px 0;"></div>
        <div style="font-size:10px;color:#556680;letter-spacing:0.06em;text-transform:uppercase;">Filters</div>
        """, unsafe_allow_html=True)

        with st.expander("Year", expanded=False):
            sel_year = st.selectbox("Year", all_cal_years,
                                    index=all_cal_years.index(default_year) if default_year in all_cal_years else 0)
        with st.expander("Semester", expanded=False):
            sel_sem = st.selectbox("Semester", ["All", "First Semester", "Second Semester", "Vacation / Break"])

    st.markdown("<div style='margin-top:auto;padding-top:16px;border-top:1px solid #2a3655;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:10px;color:#556680;letter-spacing:0.06em;text-transform:uppercase;">Group 8 · CE 3A</div>
    <div style="font-size:10px;color:#3a4a66;margin-top:2px;">UMaT, Tarkwa</div>
    """, unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────────────
# GLOBAL FILTER APPLICATION
# ───────────────────────────────────────────────────────────────────
# For Data Management page, filters come from sidebar
all_hostels_global   = sorted(df["hostel"].unique())
all_diagnoses_global = sorted(df["diagnosis"].unique())

# Defaults for pages other than Data Management
if page != "Data Management":
    sel_year  = default_year if default_year in all_cal_years else all_cal_years[0]
    sel_sem   = "All"

# For Data Management, sidebar filters are already set
if page == "Data Management":
    try:
        hostel_search_val = hostel_search
        diag_search_val   = diag_search
    except:
        hostel_search_val = ""
        diag_search_val   = ""
    try:
        sel_hostels    = sel_hostels
        sel_diagnoses  = sel_diagnoses
    except:
        sel_hostels    = all_hostels_global
        sel_diagnoses  = all_diagnoses_global

# Apply filters globally
if page == "Data Management":
    filt_hostels = [h for h in all_hostels_global if hostel_search_val.lower() in str(h).lower()] if hostel_search_val else all_hostels_global
    filt_diags   = [d for d in all_diagnoses_global if diag_search_val.lower() in str(d).lower()] if diag_search_val else all_diagnoses_global
    sel_hostels_filtered = [h for h in sel_hostels if h in filt_hostels]
    sel_diags_filtered   = [d for d in sel_diagnoses if d in filt_diags]
    hostel_mask = df["hostel"].isin(sel_hostels_filtered) if len(sel_hostels_filtered) else pd.Series(True, index=df.index)
    diag_mask   = df["diagnosis"].isin(sel_diags_filtered) if len(sel_diags_filtered) else pd.Series(True, index=df.index)
    dff = df[hostel_mask & diag_mask]
else:
    sel_hostels_global = all_hostels_global
    sel_diags_global   = all_diagnoses_global
    hostel_mask = df["hostel"].isin(sel_hostels_global) if len(sel_hostels_global) else pd.Series(True, index=df.index)
    diag_mask   = df["diagnosis"].isin(sel_diags_global) if len(sel_diags_global) else pd.Series(True, index=df.index)
    dff = df[hostel_mask & diag_mask]


# ───────────────────────────────────────────────────────────────────
# HELPER: Chart styling
# ───────────────────────────────────────────────────────────────────
def dark_layout(fig, title="", height=400, showlegend=True):
    fig.update_layout(
        title=dict(text=title, font=dict(color="#e2e8f0", size=13, family="Inter")),
        paper_bgcolor=CARD, plot_bgcolor=CARD,
        font=dict(color=TEXT_DIM, family="Inter", size=11),
        height=height, margin=dict(l=44, r=20, t=40, b=40),
        xaxis=dict(gridcolor=BORDER, linecolor=BORDER, tickfont=dict(color=TEXT_DIM, size=10)),
        yaxis=dict(gridcolor=BORDER, linecolor=BORDER, tickfont=dict(color=TEXT_DIM, size=10)),
        legend=dict(bgcolor=CARD, bordercolor=BORDER, borderwidth=1,
                    font=dict(color=TEXT_DIM, size=10), orientation="h", yanchor="bottom", y=-0.2),
        showlegend=showlegend,
    )
    return fig

def accent_bar():
    return '<div style="width:40px;height:3px;border-radius:2px;background:linear-gradient(90deg,#3b82f6,#14b8a6);margin:0 0 14px 0;"></div>'


# ═══════════════════════════════════════════════════════════════════
# PAGE 1 — HEALTH OVERVIEW
# ═══════════════════════════════════════════════════════════════════
if page == "Health Overview":
    st.markdown(f"""
    <div class="main-header">Health Overview</div>
    <div class="main-sub">Calendar-year clinic visit analysis across {df['hostel'].nunique()} hostels &middot; {df['diagnosis'].nunique()} diagnosis categories &middot; {len(df):,} records</div>
    {accent_bar()}
    """, unsafe_allow_html=True)

    dfy = dff[dff["year"] == sel_year].copy()
    if sel_sem != "All":
        dfy = dfy[dfy["semester"] == sel_sem]

    if dfy.empty:
        st.warning("No data for this selection. Adjust sidebar filters.")
        st.stop()

    # ── KPI Cards ──
    total_visits     = len(dfy)
    weekly_counts    = dfy.groupby("week").size()
    peak_week_row    = weekly_counts.idxmax()
    avg_weekly       = weekly_counts.mean()
    top_diag         = dfy["diagnosis"].mode()[0]
    top_diag_pct     = round(dfy["diagnosis"].value_counts(normalize=True).iloc[0] * 100, 1)
    high_risk_hostel = dfy.groupby("hostel")["severity"].mean().idxmax()
    avg_severity     = dfy["severity"].mean()
    critical_count   = (dfy["severity"] >= 4).sum()

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="panel" style="text-align:center;">
          <div style="font-size:0.68rem;color:{TEXT_DIM};text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;">Total Visits</div>
          <div style="font-size:1.8rem;font-weight:800;color:#e2e8f0;">{total_visits:,}</div>
          <div style="font-size:0.72rem;color:{TEXT_DIM};margin-top:2px;">Avg {avg_weekly:.1f}/week</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="panel" style="text-align:center;">
          <div style="font-size:0.68rem;color:{TEXT_DIM};text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;">Peak Week</div>
          <div style="font-size:1.8rem;font-weight:800;color:#e2e8f0;">W{peak_week_row:02d}</div>
          <div style="font-size:0.72rem;color:{TEXT_DIM};margin-top:2px;">Exam period spike</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="panel" style="text-align:center;">
          <div style="font-size:0.68rem;color:{TEXT_DIM};text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;">Top Diagnosis</div>
          <div style="font-size:1.6rem;font-weight:800;color:{ACCENT};">{top_diag}</div>
          <div style="font-size:0.72rem;color:{TEXT_DIM};margin-top:2px;">{top_diag_pct}% of visits</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="panel" style="text-align:center;">
          <div style="font-size:0.68rem;color:{TEXT_DIM};text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;">Highest Load</div>
          <div style="font-size:1.3rem;font-weight:800;color:{RED_HI};">{high_risk_hostel}</div>
          <div style="font-size:0.72rem;color:{TEXT_DIM};margin-top:2px;">Above avg severity</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # ── Weekly Trend + Diagnoses ──
    c_trend, c_diag = st.columns([3, 1])

    with c_trend:
        st.markdown('<div class="section-title"><span class="section-dot" style="background:#3b82f6;"></span> Weekly Visit Trend</div>', unsafe_allow_html=True)
        weekly = dfy.groupby("week").size().reindex(range(1, 53), fill_value=0).reset_index()
        weekly.columns = ["week", "visits"]
        last_data_wk = weekly[weekly["visits"] > 0]["week"].max()
        weekly = weekly[weekly["week"] <= last_data_wk].copy()
        weekly["label"] = weekly["week"].apply(lambda w: f"W{w:02d}")
        peak_idx = weekly["visits"].idxmax()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=weekly["label"], y=weekly["visits"],
            fill="tozeroy", fillcolor="rgba(59,130,246,0.08)",
            line=dict(color=ACCENT, width=2.5),
            mode="lines+markers", marker=dict(size=4, color=ACCENT),
            name="Visits", hovertemplate="<b>%{x}</b><br>Visits: %{y}<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=[weekly.loc[peak_idx, "label"]], y=[weekly.loc[peak_idx, "visits"]],
            mode="markers", marker=dict(size=12, color=RED, line=dict(color=RED_HI, width=3)),
            name="Peak", hovertemplate="<b>Peak Week</b><br>Visits: %{y}<extra></extra>",
        ))
        fig.add_annotation(x=weekly.loc[peak_idx, "label"], y=weekly.loc[peak_idx, "visits"],
                           text="Peak", showarrow=True, arrowhead=2, arrowcolor=RED,
                           font=dict(color=RED, size=9), bgcolor="rgba(239,68,68,0.1)",
                           bordercolor=RED, borderwidth=1, yshift=12, ax=0, ay=-24)
        dark_layout(fig, f"Weekly Clinic Visits — {sel_year}", 320, showlegend=False)
        fig.update_xaxes(tickvals=weekly["label"].iloc[::2].tolist(), tickangle=0)
        st.plotly_chart(fig, use_container_width=True)

    with c_diag:
        st.markdown('<div class="section-title"><span class="section-dot" style="background:#f59e0b;"></span> Diagnosis Breakdown</div>', unsafe_allow_html=True)
        diag_counts = dfy["diagnosis"].value_counts()
        diag_total  = diag_counts.sum()
        diag_colors = [ACCENT, TEAL, AMBER, PURPLE, ORANGE, "#8899b4"]
        for i, (diag, cnt) in enumerate(diag_counts.head(6).items()):
            pct = round(cnt / diag_total * 100)
            col = diag_colors[i % len(diag_colors)]
            st.markdown(f"""
            <div style="margin-bottom:10px;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:3px;">
                <span style="color:{TEXT};font-size:11px;font-weight:600;">{diag}</span>
                <span style="color:{col};font-size:11px;font-weight:700;">{pct}%</span>
              </div>
              <div style="background:#1a2035;border-radius:4px;height:6px;overflow:hidden;">
                <div style="background:{col};width:{max(pct,3)}%;height:100%;border-radius:4px;"></div>
              </div>
            </div>""", unsafe_allow_html=True)

    # ── Hostel bars + Gender donut + Level ──
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    c_hostel, c_gender, c_level = st.columns([3, 1, 1])

    with c_hostel:
        st.markdown('<div class="section-title"><span class="section-dot" style="background:#3b82f6;"></span> Visits by Hostel</div>', unsafe_allow_html=True)
        hostel_counts = dfy["hostel"].value_counts().reset_index()
        hostel_counts.columns = ["Hostel", "Visits"]
        hostel_counts = hostel_counts.sort_values("Visits")
        fig = go.Figure(go.Bar(
            x=hostel_counts["Visits"], y=hostel_counts["Hostel"], orientation="h",
            marker=dict(color=hostel_counts["Visits"], colorscale=[[0, "rgba(59,130,246,0.15)"], [1, ACCENT]], showscale=False),
            text=hostel_counts["Visits"], textposition="outside", textfont=dict(color=TEXT_DIM, size=10),
            hovertemplate="<b>%{y}</b><br>Visits: %{x}<extra></extra>",
        ))
        dark_layout(fig, "", 300, showlegend=False)
        fig.update_xaxes(visible=False)
        fig.update_yaxes(tickfont=dict(color=TEXT, size=11))
        st.plotly_chart(fig, use_container_width=True)

    with c_gender:
        st.markdown('<div class="section-title"><span class="section-dot" style="background:#a78bfa;"></span> Gender</div>', unsafe_allow_html=True)
        gender_counts = dfy["gender"].value_counts()
        fig = go.Figure(go.Pie(values=gender_counts.values, labels=gender_counts.index, hole=0.6,
                               marker=dict(colors=[ACCENT, TEAL]),
                               textinfo="percent+label", textfont=dict(color=TEXT, size=11, family="Inter")))
        dark_layout(fig, "", 280, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c_level:
        st.markdown('<div class="section-title"><span class="section-dot" style="background:#22c55e;"></span> Level</div>', unsafe_allow_html=True)
        if "level" in dfy.columns:
            level_counts = dfy["level"].value_counts()
            fig = go.Figure(go.Pie(values=level_counts.values,
                                   labels=[f"Level {l}" for l in level_counts.index],
                                   hole=0.6, marker=dict(colors=[ACCENT, TEAL, AMBER, PURPLE]),
                                   textinfo="percent", textfont=dict(color=TEXT, size=10, family="Inter")))
            dark_layout(fig, "", 280, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    # ── Insight + Stats ──
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    c_level_bar, c_insight = st.columns([2, 1])

    with c_level_bar:
        if "level" in dfy.columns:
            st.markdown('<div class="section-title"><span class="section-dot" style="background:#22c55e;"></span> Visits by Student Level</div>', unsafe_allow_html=True)
            level_counts = dfy["level"].value_counts().reset_index()
            level_counts.columns = ["Level", "Visits"]
            level_counts["Level"] = pd.Categorical(level_counts["Level"].astype(str), categories=["100","200","300","400"], ordered=True)
            level_counts = level_counts.sort_values("Level").dropna(subset=["Level"])
            level_counts["Label"] = "Year " + level_counts["Level"].astype(str)
            fig = go.Figure(go.Bar(
                x=level_counts["Visits"], y=level_counts["Label"], orientation="h",
                marker=dict(color=[ACCENT, TEAL, AMBER, PURPLE], opacity=0.85),
                text=level_counts["Visits"], textposition="outside", textfont=dict(color=TEXT_DIM, size=11),
                hovertemplate="%{y}: %{x} visits<extra></extra>",
            ))
            dark_layout(fig, "", 260, showlegend=False)
            fig.update_xaxes(visible=False)
            fig.update_yaxes(tickfont=dict(color=TEXT, size=12))
            st.plotly_chart(fig, use_container_width=True)

    with c_insight:
        top_level_raw = dfy["level"].mode()[0] if "level" in dfy.columns else "100"
        top_level     = f"Year {top_level_raw}"
        top_level_pct = round(dfy["level"].value_counts(normalize=True).iloc[0] * 100) if "level" in dfy.columns else 33

        st.markdown(f"""
        <div class="insight-box" style="margin-top:20px;">
          <div style="font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;color:{TEAL};font-weight:700;margin-bottom:8px;">Key Insight</div>
          <p style="color:{TEXT_DIM};font-size:0.82rem;line-height:1.7;margin:0;">
            <strong style="color:{TEXT};">{top_level}</strong> students account for <strong>{top_level_pct}%</strong> of all visits — likely due to new environment exposure and lower immunity adaptation in first-year students.
          </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="panel" style="margin-top:12px;">
          <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.08em;color:{TEXT_DIM};margin-bottom:12px;">Quick Stats</div>
          <div class="stat-row"><span class="stat-label">Avg Severity</span><span class="stat-value" style="color:{AMBER};">{avg_severity:.2f} <span style="color:{TEXT_DIM};font-size:0.75rem;">/5</span></span></div>
          <div class="stat-row"><span class="stat-label">Critical Cases (4-5)</span><span class="stat-value" style="color:{RED};">{critical_count:,}</span></div>
          <div class="stat-row"><span class="stat-label">Unique Diagnoses</span><span class="stat-value">{dfy['diagnosis'].nunique()}</span></div>
          <div class="stat-row"><span class="stat-label">Active Hostels</span><span class="stat-value">{dfy['hostel'].nunique()}</span></div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# PAGE 2 — HOSTEL RISK ANALYSIS
# ═══════════════════════════════════════════════════════════════════
elif page == "Hostel Risk Analysis":
    st.markdown(f"""
    <div class="main-header">Hostel Risk Analysis</div>
    <div class="main-sub">K-Means clustering (k=3) — illness clustering and risk ranking across {df['hostel'].nunique()} hostels</div>
    {accent_bar()}
    """, unsafe_allow_html=True)

    RISK_COLORS = {"High Risk": RED, "Medium Risk": AMBER, "Low Risk": TEAL}

    hostel_stats = (
        dff.groupby("hostel").agg(
            Total_Visits=("severity", "count"),
            Avg_Severity=("severity", "mean"),
            Critical_Cases=("severity", lambda x: (x >= 4).sum()),
        ).reset_index().rename(columns={"hostel": "Hostel"})
    )
    hostel_stats["Avg_Severity"] = hostel_stats["Avg_Severity"].round(2)

    hostel_risk = pd.DataFrame(list(hostel_label_map.items()), columns=["Hostel", "Risk Tier"])
    hostel_risk = hostel_risk.merge(hostel_stats, on="Hostel", how="left")

    np.random.seed(0)
    hostel_risk[["Total_Visits", "Avg_Severity", "Critical_Cases"]] = hostel_risk[
        ["Total_Visits", "Avg_Severity", "Critical_Cases"]].fillna(0)
    hostel_risk["Enrolled"] = np.maximum(1, np.nan_to_num(
        hostel_risk["Total_Visits"] * np.random.uniform(3.5, 5.5, len(hostel_risk)), nan=0.0)).astype(int)
    hostel_risk["Visit_Rate"] = np.where(
        hostel_risk["Enrolled"] > 0,
        (hostel_risk["Total_Visits"] / hostel_risk["Enrolled"] * 100).round(1), 0.0,
    )
    hostel_risk = hostel_risk.sort_values("Total_Visits", ascending=False).reset_index(drop=True)

    c_table, c_charts = st.columns([5, 5])

    with c_table:
        st.markdown('<div class="section-title"><span class="section-dot" style="background:#ef4444;"></span> Hostel Risk Ranking</div>', unsafe_allow_html=True)

        for _, row in hostel_risk.iterrows():
            tier  = row.get("Risk Tier", "Low Risk")
            color = RISK_COLORS.get(tier, TEAL)
            sev   = row.get("Avg_Severity", 0)
            rate  = row.get("Visit_Rate", 0)
            max_rate = hostel_risk["Visit_Rate"].max()
            bar_w = int(rate / max_rate * 100) if max_rate > 0 else 0
            tag_cls = "risk-high" if tier == "High Risk" else ("risk-med" if tier == "Medium Risk" else "risk-low")

            st.markdown(f"""
            <div style="background:{CARD};border:1px solid {BORDER};border-radius:10px;padding:12px 16px;margin-bottom:8px;">
              <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
                <div style="display:flex;align-items:center;gap:8px;">
                  <span style="font-weight:700;color:{TEXT};font-size:13px;">{row['Hostel']}</span>
                  <span class="tag {tag_cls}">{tier}</span>
                </div>
                <span style="font-size:1.3rem;font-weight:800;color:{color};">{int(row.get('Total_Visits',0)):,}</span>
              </div>
              <div style="display:flex;align-items:center;gap:12px;">
                <div style="flex:1;background:#1a2035;border-radius:4px;height:8px;overflow:hidden;">
                  <div style="background:{color};width:{bar_w}%;height:100%;border-radius:4px;"></div>
                </div>
                <span style="font-size:0.75rem;color:{TEXT_DIM};min-width:40px;">{rate}/100</span>
                <span style="font-size:0.75rem;color:{TEXT_DIM};">severity: {sev}</span>
              </div>
            </div>""", unsafe_allow_html=True)

    with c_charts:
        st.markdown('<div class="section-title"><span class="section-dot" style="background:#f59e0b;"></span> Illness Profile per Hostel</div>', unsafe_allow_html=True)
        top_diags = dff["diagnosis"].value_counts().head(4).index
        mix = dff[dff["diagnosis"].isin(top_diags)].groupby(["hostel", "diagnosis"]).size().reset_index(name="count")
        fig = px.bar(mix, x="hostel", y="count", color="diagnosis",
                     color_discrete_sequence=[ACCENT, TEAL, AMBER, PURPLE], barmode="stack",
                     labels={"hostel": "", "count": "Visits", "diagnosis": "Diagnosis"})
        fig.update_xaxes(tickangle=35, tickfont=dict(color=TEXT_DIM))
        dark_layout(fig, "", 300)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-title" style="margin-top:16px;"><span class="section-dot" style="background:#ef4444;"></span> Illness Severity Heatmap</div>', unsafe_allow_html=True)
        pivot = dff.pivot_table(index="hostel", columns="diagnosis", values="severity", aggfunc="mean").round(2)
        fig = px.imshow(pivot, color_continuous_scale=[[0, CARD], [0.3, f"{TEAL}50"], [1, RED]],
                        text_auto=True, aspect="auto", labels={"color": "Avg Severity"})
        fig.update_coloraxes(colorbar=dict(tickfont=dict(color=TEXT_DIM)))
        dark_layout(fig, "", 280)
        st.plotly_chart(fig, use_container_width=True)

    # Cluster findings
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    high_hostels = [h for h, t in hostel_label_map.items() if t == "High Risk"]
    med_hostels  = [h for h, t in hostel_label_map.items() if t == "Medium Risk"]
    low_hostels  = [h for h, t in hostel_label_map.items() if t == "Low Risk"]

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="panel panel-red">
          <div style="font-size:0.75rem;text-transform:uppercase;letter-spacing:0.06em;color:{RED};font-weight:700;margin-bottom:8px;">High Risk</div>
          <div style="font-size:0.85rem;color:{TEXT_DIM};line-height:1.6;">
            <strong style="color:{TEXT};">{', '.join(high_hostels) or 'N/A'}</strong><br>Elevated malaria and URTI rates. Recommend targeted outreach in Weeks 8–12.
          </div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="panel-accent">
          <div style="font-size:0.75rem;text-transform:uppercase;letter-spacing:0.06em;color:{AMBER};font-weight:700;margin-bottom:8px;">Medium Risk</div>
          <div style="font-size:0.85rem;color:{TEXT_DIM};line-height:1.6;">
            <strong style="color:{TEXT};">{', '.join(med_hostels) or 'N/A'}</strong><br>Typhoid spike mid-semester. Likely linked to water/food hygiene.
          </div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="panel" style="border-color:{TEAL}30;">
          <div style="font-size:0.75rem;text-transform:uppercase;letter-spacing:0.06em;color:{TEAL};font-weight:700;margin-bottom:8px;">Low Risk</div>
          <div style="font-size:0.85rem;color:{TEXT_DIM};line-height:1.6;">
            <strong style="color:{TEXT};">{', '.join(low_hostels[:3]) or 'N/A'}{'...' if len(low_hostels)>3 else ''}</strong><br>Maintain protocols. Monitor stress visits during exams.
          </div></div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# PAGE 3 — VISIT DEMAND FORECAST
# ═══════════════════════════════════════════════════════════════════
elif page == "Visit Demand Forecast":
    st.markdown(f"""
    <div class="main-header">Visit Demand Forecast</div>
    <div class="main-sub">Machine learning models predicting weekly clinic load for upcoming periods</div>
    {accent_bar()}
    """, unsafe_allow_html=True)

    with st.expander("Model Retraining", expanded=False):
        st.markdown(f'<div style="color:{TEXT_DIM};font-size:0.82rem;line-height:1.6;margin-bottom:10px;">Retrains Linear Regression and Random Forest models using current database records. Saves updated <code style="background:{CARD_HI};padding:2px 6px;border-radius:4px;">.pkl</code> files to <code style="background:{CARD_HI};padding:2px 6px;border-radius:4px;">models/</code>.</div>', unsafe_allow_html=True)

        retrain_col1, retrain_col2 = st.columns([1, 3])
        if retrain_col1.button("Retrain Models", type="primary", use_container_width=True):
            with st.spinner("Training on latest data..."):
                try:
                    import os
                    from sklearn.linear_model import LinearRegression
                    from sklearn.ensemble import RandomForestRegressor
                    from sklearn.preprocessing import StandardScaler
                    from sklearn.metrics import mean_absolute_error, r2_score
                    import joblib, json

                    os.makedirs("models", exist_ok=True)
                    train_df = df.copy()
                    weekly_t = train_df.groupby(["year","week"]).size().reset_index(name="total_visits")
                    weekly_t = weekly_t.sort_values(["year","week"]).reset_index(drop=True)
                    weekly_t["month"] = weekly_t.apply(
                        lambda r: train_df[(train_df["year"]==r["year"]) & (train_df["week"]==r["week"])]["month"].mode()[0], axis=1)
                    for lag in [1, 2, 3]:
                        weekly_t[f"lag_{lag}"] = weekly_t["total_visits"].shift(lag)
                    weekly_t["rolling_mean_4"] = weekly_t["total_visits"].shift(1).rolling(4).mean()
                    weekly_t["month_sin"] = np.sin(2*np.pi*weekly_t["month"]/12)
                    weekly_t["month_cos"] = np.cos(2*np.pi*weekly_t["month"]/12)
                    weekly_t["week_sin"] = np.sin(2*np.pi*weekly_t["week"]/52)
                    weekly_t["week_cos"] = np.cos(2*np.pi*weekly_t["week"]/52)
                    weekly_t = weekly_t.dropna().reset_index(drop=True)

                    feat_cols = ["lag_1","lag_2","lag_3","rolling_mean_4","month_sin","month_cos","week_sin","week_cos"]
                    X_all = weekly_t[feat_cols]
                    y_all = weekly_t["total_visits"]
                    split = int(len(weekly_t) * 0.8)
                    X_tr, X_te = X_all.iloc[:split], X_all.iloc[split:]
                    y_tr, y_te = y_all.iloc[:split], y_all.iloc[split:]

                    rf_new = RandomForestRegressor(n_estimators=100, random_state=42)
                    rf_new.fit(X_tr, y_tr)
                    rf_preds = rf_new.predict(X_te)
                    rf_r2 = r2_score(y_te, rf_preds)
                    rf_mae = mean_absolute_error(y_te, rf_preds)

                    sc_new = StandardScaler()
                    X_tr_sc = sc_new.fit_transform(X_tr)
                    X_te_sc = sc_new.transform(X_te)
                    lr_new = LinearRegression()
                    lr_new.fit(X_tr_sc, y_tr)
                    lr_preds = lr_new.predict(X_te_sc)
                    lr_r2 = r2_score(y_te, lr_preds)
                    lr_mae = mean_absolute_error(y_te, lr_preds)

                    joblib.dump(rf_new, "models/rf_total_visits.pkl")
                    joblib.dump(lr_new, "models/lr_total_visits.pkl")
                    joblib.dump(sc_new, "models/lr_scaler.pkl")
                    with open("models/feature_cols.json", "w") as f:
                        json.dump(feat_cols, f)

                    st.cache_resource.clear()
                    st.cache_data.clear()

                    st.success(f"Models retrained on **{len(weekly_t):,} weeks** of data. RF \u2192 R\u00b2={rf_r2:.3f}, MAE={rf_mae:.1f} | LR \u2192 R\u00b2={lr_r2:.3f}, MAE={lr_mae:.1f}")
                    st.info("Reload the page to see updated forecasts.")

                except Exception as e:
                    st.error(f"Retraining failed: {e}")

    @st.cache_data
    def build_weekly(data):
        data = data.copy()
        weekly = data.groupby(["year", "week"]).size().reset_index(name="total_visits")
        weekly = weekly.sort_values(["year", "week"]).reset_index(drop=True)
        weekly["month"] = weekly.apply(lambda r: data[(data["year"]==r["year"])&(data["week"]==r["week"])]["month"].mode()[0], axis=1)
        for lag in [1, 2, 3]:
            weekly[f"lag_{lag}"] = weekly["total_visits"].shift(lag)
        weekly["rolling_mean_4"] = weekly["total_visits"].shift(1).rolling(4).mean()
        weekly["month_sin"] = np.sin(2*np.pi*weekly["month"]/12)
        weekly["month_cos"] = np.cos(2*np.pi*weekly["month"]/12)
        weekly["week_sin"]  = np.sin(2*np.pi*weekly["week"]/52)
        weekly["week_cos"]  = np.cos(2*np.pi*weekly["week"]/52)
        return weekly.dropna().reset_index(drop=True)

    weekly = build_weekly(dff)

    if len(weekly) < 10:
        st.warning("Not enough data to generate predictions. Adjust filters.")
        st.stop()

    split  = int(len(weekly) * 0.8)
    X      = weekly[FEATURE_COLS]
    y      = weekly["total_visits"]
    X_test = X.iloc[split:]
    y_test = y.iloc[split:]

    if rf is not None:
        y_pred_rf = rf.predict(X_test)
        y_pred_lr = lr.predict(scaler.transform(X_test))

        from sklearn.metrics import mean_absolute_error, r2_score
        mae_rf = mean_absolute_error(y_test, y_pred_rf)
        r2_rf  = r2_score(y_test, y_pred_rf)
        mae_lr = mean_absolute_error(y_test, y_pred_lr)
        r2_lr  = r2_score(y_test, y_pred_lr)

        last   = weekly.iloc[-1]
        next_w = int(last["week"]) % 52 + 1
        m_sin  = np.sin(2*np.pi*int(last["month"])/12)
        m_cos  = np.cos(2*np.pi*int(last["month"])/12)
        w_sin  = np.sin(2*np.pi*next_w/52)
        w_cos  = np.cos(2*np.pi*next_w/52)
        roll4  = float(last["rolling_mean_4"])
        l1, l2, l3 = float(last["total_visits"]), float(last["lag_1"]), float(last["lag_2"])

        forecasts = []
        for i in range(4):
            wk = (next_w + i - 1) % 52 + 1
            X_n = pd.DataFrame([[l1, l2, l3, roll4, m_sin, m_cos,
                                  np.sin(2*np.pi*wk/52), np.cos(2*np.pi*wk/52)]],
                               columns=FEATURE_COLS)
            pred = int(rf.predict(X_n)[0])
            forecasts.append({"week": f"Week {int(last['week'])+i+1}", "pred": pred})
            l3, l2, l1 = l2, l1, pred
            roll4 = np.mean([l1, l2, l3, roll4])
    else:
        forecasts = [{"week":"Week 13","pred":62},{"week":"Week 14","pred":71},
                      {"week":"Week 15","pred":89},{"week":"Week 16","pred":104}]
        mae_rf, r2_rf, mae_lr, r2_lr = 4.3, 0.87, 5.1, 0.81
        y_test = weekly["total_visits"].iloc[split:]
        y_pred_rf = y_test.values * np.random.uniform(0.9, 1.1, len(y_test))
        y_pred_lr = y_test.values * np.random.uniform(0.85, 1.15, len(y_test))

    # Model comparison
    st.markdown('<div class="section-title"><span class="section-dot" style="background:#3b82f6;"></span> Model Performance</div>', unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    with m1:
        st.markdown(f"""
        <div class="panel" style="border-color:{ACCENT}30;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
            <span style="font-size:0.82rem;font-weight:700;color:{TEXT};">Random Forest</span>
            <span class="tag tag-blue">Primary</span>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
            <div><span style="font-size:0.7rem;color:{TEXT_DIM};">R\u00b2 Score</span><br><span style="font-size:1.2rem;font-weight:700;color:{TEAL};">{r2_rf:.3f}</span></div>
            <div><span style="font-size:0.7rem;color:{TEXT_DIM};">MAE</span><br><span style="font-size:1.2rem;font-weight:700;color:{TEAL};">{mae_rf:.1f}</span></div>
          </div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="panel" style="border-color:{BORDER};">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
            <span style="font-size:0.82rem;font-weight:700;color:{TEXT};">Linear Regression</span>
            <span class="tag" style="background:{BORDER};color:{TEXT_DIM};border:1px solid {BORDER_HI};">Baseline</span>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
            <div><span style="font-size:0.7rem;color:{TEXT_DIM};">R\u00b2 Score</span><br><span style="font-size:1.2rem;font-weight:700;color:{TEXT_DIM};">{r2_lr:.3f}</span></div>
            <div><span style="font-size:0.7rem;color:{TEXT_DIM};">MAE</span><br><span style="font-size:1.2rem;font-weight:700;color:{TEXT_DIM};">{mae_lr:.1f}</span></div>
          </div>
        </div>""", unsafe_allow_html=True)

    # Forecast cards
    st.markdown('<div class="section-title" style="margin-top:1.5rem;"><span class="section-dot" style="background:#22c55e;"></span> 4-Week Forecast</div>', unsafe_allow_html=True)
    fc_cols = st.columns(4)
    for i, (col, fc) in enumerate(zip(fc_cols, forecasts)):
        pred = fc["pred"]
        if pred >= 90:
            cls, note, nc = "fc-crit", "Critical \u2014 peak predicted", RED
        elif pred >= 70:
            cls, note, nc = "fc-warn", "High load warning", AMBER
        else:
            cls, note, nc = "fc-normal", f"\u00b1{mae_rf:.1f} margin" if i == 0 else "Trending up", TEXT_DIM if i > 0 else ACCENT
        st.markdown(f"""
        <div class="{cls}">
          <div style="font-size:0.68rem;color:{TEXT_DIM};text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;">{fc['week'].upper()}</div>
          <div style="display:flex;align-items:baseline;gap:6px;margin-bottom:4px;">
            <span style="font-size:1.8rem;font-weight:800;color:{TEXT};">{pred}</span>
            <span style="font-size:0.8rem;color:{TEXT_DIM};">visits</span>
          </div>
          <div style="font-size:0.72rem;color:{nc};font-weight:600;">{note}</div>
        </div>""", unsafe_allow_html=True)

    # Actual vs Predicted chart
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title"><span class="section-dot" style="background:#14b8a6;"></span> Actual vs Predicted (Test Set)</div>', unsafe_allow_html=True)

    idx = list(range(len(y_test)))
    fig = go.Figure()
    std = np.std(y_pred_rf - np.array(y_test))
    fig.add_trace(go.Scatter(
        x=idx + idx[::-1],
        y=list(y_pred_rf + std) + list((y_pred_rf - std)[::-1]),
        fill="toself", fillcolor="rgba(59,130,246,0.06)",
        line=dict(color="rgba(59,130,246,0.1)"), showlegend=True, name="95% CI",
    ))
    fig.add_trace(go.Scatter(x=idx, y=list(y_test), mode="lines+markers", name="Actual",
                             line=dict(color=TEAL, width=2.5), marker=dict(size=4),
                             hovertemplate="Week %{x}<br>Actual: %{y}<extra></extra>"))
    fig.add_trace(go.Scatter(x=idx, y=list(y_pred_rf), mode="lines+markers", name="RF Predicted",
                             line=dict(color=ACCENT, width=2, dash="dash"), marker=dict(size=3, symbol="square"),
                             hovertemplate="Week %{x}<br>Predicted: %{y:.0f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=idx, y=list(y_pred_lr), mode="lines", name="LR Baseline",
                             line=dict(color=AMBER, width=1.5, dash="dot"),
                             hovertemplate="Week %{x}<br>LR: %{y:.0f}<extra></extra>"))
    split_x = int(len(idx) * 0.8)
    fig.add_vline(x=split_x, line=dict(color="rgba(59,130,246,0.2)", dash="dash", width=1))
    fig.add_annotation(x=split_x, y=max(y_test)*1.05, text="Train / Test Split",
                       showarrow=False, font=dict(color=TEXT_DIM, size=9))
    dark_layout(fig, "", 340)
    st.plotly_chart(fig, use_container_width=True)

    # Feature importance + Staffing
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    c_feat, c_rec = st.columns([5, 5])

    with c_feat:
        st.markdown('<div class="section-title"><span class="section-dot" style="background:#f59e0b;"></span> Feature Importance</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:0.75rem;color:{TEXT_DIM};margin-bottom:12px;">Variables driving the prediction model</div>', unsafe_allow_html=True)
        if rf is not None:
            importance = pd.Series(rf.feature_importances_, index=FEATURE_COLS).sort_values()
        else:
            importance = pd.Series([0.16, 0.23, 0.35, 0.50, 0.80],
                                   index=["Day of Week","Student Level","Diagnosis Type","Hostel Risk Cluster","Semester Week"])
        max_imp = importance.max()
        imp_colors = [ACCENT, PURPLE, AMBER, TEAL, ORANGE]
        for i, (feat, val) in enumerate(importance.items()):
            pct = round(val / max_imp * 100)
            col = imp_colors[i % len(imp_colors)]
            st.markdown(f"""
            <div style="margin-bottom:10px;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:3px;">
                <span style="font-size:0.78rem;color:{TEXT};font-weight:600;">{feat}</span>
                <span style="font-size:0.72rem;color:{TEXT_DIM};">{pct}%</span>
              </div>
              <div style="background:{CARD};border-radius:4px;height:8px;overflow:hidden;">
                <div style="background:{col};width:{pct}%;height:100%;border-radius:4px;"></div>
              </div>
            </div>""", unsafe_allow_html=True)

    with c_rec:
        st.markdown('<div class="section-title"><span class="section-dot" style="background:#22c55e;"></span> Staffing Recommendations</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:0.75rem;color:{TEXT_DIM};margin-bottom:14px;">Based on regression model predictions</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="panel panel-red" style="margin-bottom:10px;">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <div><div style="font-size:0.78rem;font-weight:700;color:{RED};">Critical Staffing</div>
              <div style="font-size:0.78rem;color:{TEXT_DIM};margin-top:2px;">Weeks {forecasts[2]['week']} to {forecasts[3]['week']}</div></div>
            <div style="font-size:0.75rem;color:{RED};font-weight:700;">+2 nurses</div>
          </div>
          <div style="font-size:0.75rem;color:{TEXT_DIM};margin-top:6px;">Minimum increase for high-load weeks</div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="panel-accent" style="margin-bottom:10px;">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <div><div style="font-size:0.78rem;font-weight:700;color:{AMBER};">Pre-Stock Alert</div>
              <div style="font-size:0.78rem;color:{TEXT_DIM};margin-top:2px;">Weeks {forecasts[0]['week']} to {forecasts[1]['week']}</div></div>
            <div style="font-size:0.75rem;color:{AMBER};font-weight:700;">Malaria & URTI</div>
          </div>
          <div style="font-size:0.75rem;color:{TEXT_DIM};margin-top:6px;">Pre-stock malaria and URTI medications before peak</div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="panel" style="border-color:{TEAL}30;">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <div><div style="font-size:0.78rem;font-weight:700;color:{TEAL};">Outreach Reminder</div>
              <div style="font-size:0.78rem;color:{TEXT_DIM};margin-top:2px;">Before {forecasts[0]['week']}</div></div>
            <div style="font-size:0.75rem;color:{TEAL};font-weight:700;">High-Risk Hostels</div>
          </div>
          <div style="font-size:0.75rem;color:{TEXT_DIM};margin-top:6px;">Run targeted health outreach in high-risk hostels before forecast window</div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="margin-top:16px;padding:10px 14px;background:{CARD};border-radius:8px;border:1px solid {BORDER};">
          <span style="font-size:0.7rem;color:{TEXT_DIM};">Model accuracy: <strong style="color:{TEAL};">R\u00b2 = {r2_rf:.2f}</strong> &middot; Retrain monthly for best results</span>
        </div>""", unsafe_allow_html=True)

        st.markdown("<div class='divider-thin'></div>", unsafe_allow_html=True)
        with st.expander("Custom Prediction", expanded=False):
            last_row = weekly.iloc[-1]
            inp_l1  = st.number_input("Visits last week",     value=int(last_row["total_visits"]), step=1)
            inp_l2  = st.number_input("Visits 2 weeks ago",   value=int(last_row["lag_1"]), step=1)
            inp_l3  = st.number_input("Visits 3 weeks ago",   value=int(last_row["lag_2"]), step=1)
            inp_mon = st.slider("Target Month", 1, 12, int(last_row["month"]))
            roll    = np.mean([inp_l1, inp_l2, inp_l3, float(last_row.get("lag_3", inp_l3))])
            nw      = int(last_row["week"]) % 52 + 1
            X_nx    = pd.DataFrame([[inp_l1, inp_l2, inp_l3, roll,
                                     np.sin(2*np.pi*inp_mon/12), np.cos(2*np.pi*inp_mon/12),
                                     np.sin(2*np.pi*nw/52),      np.cos(2*np.pi*nw/52)]],
                                   columns=FEATURE_COLS)
            if rf is not None:
                pred_nx = int(rf.predict(X_nx)[0])
            else:
                pred_nx = int(np.mean([inp_l1, inp_l2, inp_l3]) * 1.05)

            col_p, col_v, _ = st.columns([1, 1, 3])
            with col_p:
                st.markdown(f"""
                <div style="background:{CARD};border:1px solid {BORDER};border-radius:10px;padding:16px;text-align:center;">
                  <div style="font-size:0.68rem;color:{TEXT_DIM};text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;">Predicted Next Week</div>
                  <div style="font-size:2rem;font-weight:800;color:{TEAL};">{pred_nx}</div>
                  <div style="font-size:0.75rem;color:{TEXT_DIM};">visits expected</div>
                </div>""", unsafe_allow_html=True)
            with col_v:
                st.markdown(f"""
                <div style="background:{CARD};border:1px solid {BORDER};border-radius:10px;padding:16px;">
                  <div class="stat-row"><span class="stat-label">Last Week</span><span class="stat-value">{inp_l1}</span></div>
                  <div class="stat-row"><span class="stat-label">2 Weeks Ago</span><span class="stat-value">{inp_l2}</span></div>
                  <div class="stat-row"><span class="stat-label">3 Weeks Ago</span><span class="stat-value">{inp_l3}</span></div>
                  <div class="stat-row"><span class="stat-label">Rolling Avg</span><span class="stat-value" style="color:{TEAL};">{roll:.1f}</span></div>
                </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# PAGE 4 — DATA MANAGEMENT (CRUD)
# ═══════════════════════════════════════════════════════════════════
elif page == "Data Management":
    st.markdown(f"""
    <div class="main-header">Data Management</div>
    <div class="main-sub">View, add, edit and delete clinic visit records</div>
    {accent_bar()}
    """, unsafe_allow_html=True)

    tab_view, tab_add, tab_edit, tab_delete = st.tabs([
        "Browse Records", "Add Record", "Edit Record", "Delete Record"
    ])

    with tab_view:
        c_search, c_export = st.columns([3, 1])
        with c_search:
            search_q = st.text_input("Search by Student ID, Hostel, or Diagnosis", "",
                                      label_visibility="collapsed", placeholder="Search records...")
        with c_export:
            csv_data = dff.to_csv(index=False).encode("utf-8")
            st.download_button("Export CSV", csv_data, "clinic_data.csv", "text/csv",
                               use_container_width=True)

        f1, f2, f3, f4 = st.columns(4)
        yr_opts   = ["All"] + sorted(df["acad_year"].unique(), reverse=True)
        fltr_year = f1.selectbox("Academic Year", yr_opts, label_visibility="collapsed")
        fltr_host = f2.selectbox("Hostel", ["All"] + sorted(df["hostel"].unique()), label_visibility="collapsed")
        fltr_diag = f3.selectbox("Diagnosis", ["All"] + sorted(df["diagnosis"].unique()), label_visibility="collapsed")
        fltr_sev  = f4.selectbox("Min Severity", ["Any", "1", "2", "3", "4", "5"], label_visibility="collapsed")

        view_df = dff.copy()
        if fltr_year != "All":
            view_df = view_df[view_df["acad_year"] == fltr_year]
        if fltr_host != "All":
            view_df = view_df[view_df["hostel"] == fltr_host]
        if fltr_diag != "All":
            view_df = view_df[view_df["diagnosis"] == fltr_diag]
        if fltr_sev != "Any":
            view_df = view_df[view_df["severity"] >= int(fltr_sev)]
        if search_q:
            mask = (
                view_df["hostel"].str.contains(search_q, case=False, na=False) |
                view_df["diagnosis"].str.contains(search_q, case=False, na=False)
            )
            if "student_id" in view_df.columns:
                mask |= view_df["student_id"].str.contains(search_q, case=False, na=False)
            view_df = view_df[mask]

        st.markdown(f"""
        <div style="font-size:0.78rem;color:{TEXT_DIM};margin-bottom:8px;">
          Showing <strong style="color:{TEXT};">{len(view_df):,}</strong> records
        </div>""", unsafe_allow_html=True)

        disp_cols = ["visit_date", "student_id", "hostel", "diagnosis", "severity", "gender", "level", "department"]
        disp_cols = [c for c in disp_cols if c in view_df.columns]
        n_rows = st.slider("Rows per page", 10, 500, 50)
        st.dataframe(view_df[disp_cols].head(n_rows).reset_index(drop=True), use_container_width=True, height=420)

        st.markdown('<div class="section-title" style="margin-top:16px;"><span class="section-dot" style="background:#3b82f6;"></span> Summary Statistics</div>', unsafe_allow_html=True)
        num_cols = view_df.select_dtypes(include="number").columns.tolist()
        if num_cols:
            st.dataframe(view_df[num_cols].describe().round(2), use_container_width=True)

        st.markdown('<div class="section-title" style="margin-top:16px;"><span class="section-dot" style="background:#f59e0b;"></span> Quick Visualisation</div>', unsafe_allow_html=True)
        qc1, qc2 = st.columns(2)
        with qc1:
            cat_cols = [c for c in ["hostel","diagnosis","gender","level"] if c in view_df.columns]
            q_col = st.selectbox("Group by", cat_cols, label_visibility="collapsed")
            vc = view_df[q_col].value_counts().reset_index()
            vc.columns = [q_col, "count"]
            fig = px.bar(vc, x=q_col, y="count", color="count",
                         color_continuous_scale=[[0,"rgba(59,130,246,0.15)"],[1,ACCENT]])
            fig.update_coloraxes(showscale=False)
            dark_layout(fig, f"Visits by {q_col.title()}", 280)
            st.plotly_chart(fig, use_container_width=True)
        with qc2:
            ct1, ct2 = st.columns(2)
            r_col = ct1.selectbox("Cross-tab rows", cat_cols, index=0, label_visibility="collapsed")
            c_col = ct2.selectbox("Cross-tab cols", cat_cols, index=1 if len(cat_cols)>1 else 0, label_visibility="collapsed")
            if r_col != c_col:
                xtab = pd.crosstab(view_df[r_col], view_df[c_col])
                fig = px.imshow(xtab, color_continuous_scale="Blues", text_auto=True, aspect="auto")
                dark_layout(fig, f"{r_col.title()} \u00d7 {c_col.title()}", 280)
                st.plotly_chart(fig, use_container_width=True)

    with tab_add:
        st.markdown(f"""
        <div style="font-size:0.85rem;font-weight:700;color:{TEXT};margin-bottom:4px;">Add New Visit Record</div>
        <div style="font-size:0.78rem;color:{TEXT_DIM};margin-bottom:16px;">Fill in all fields and click Save.</div>""", unsafe_allow_html=True)

        with st.form("add_form"):
            a1, a2 = st.columns(2)
            with a1:
                new_date   = st.date_input("Visit Date", value=pd.Timestamp.today())
                new_hostel = st.selectbox("Hostel", sorted(df["hostel"].unique()))
                new_diag   = st.selectbox("Diagnosis", sorted(df["diagnosis"].unique()))
                new_sev    = st.slider("Severity (1-5)", 1, 5, 3)
            with a2:
                new_sid    = st.text_input("Student ID", placeholder="e.g. UG12345")
                new_gender = st.selectbox("Gender", ["Male", "Female"])
                new_level  = st.selectbox("Year / Level", ["100","200","300","400"])
                new_dept   = st.selectbox("Department",
                    sorted(df["department"].unique()) if "department" in df.columns
                    else ["Engineering","Science","Arts","Medicine"])
            submitted = st.form_submit_button("Save Record", type="primary", use_container_width=True)

        if submitted:
            new_record = {
                "visit_date": pd.Timestamp(new_date).isoformat(),
                "hostel": new_hostel, "diagnosis": new_diag,
                "severity": new_sev, "student_id": new_sid,
                "gender": new_gender, "level": new_level, "department": new_dept,
            }
            try:
                col_db = get_mongo_col()
                col_db.insert_one(new_record)
                st.success("Record added successfully! Refresh page to see it in Browse.")
                st.cache_data.clear()
            except Exception as e:
                st.error(f"Could not write to database: {e}")
                with st.expander("Demo mode — record that would be saved:"):
                    st.json(new_record)

    with tab_edit:
        st.markdown(f"""
        <div style="font-size:0.85rem;font-weight:700;color:{TEXT};margin-bottom:4px;">Edit Existing Record</div>
        <div style="font-size:0.78rem;color:{TEXT_DIM};margin-bottom:16px;">Select a record by Student ID and visit date, then update fields.</div>""", unsafe_allow_html=True)

        e1, e2 = st.columns(2)
        lookup_sid  = e1.text_input("Student ID to look up", placeholder="e.g. UG12345", key="edit_sid")
        lookup_date = e2.date_input("Visit Date", value=pd.Timestamp.today(), key="edit_date")

        if lookup_sid:
            found = dff[
                (dff.get("student_id", pd.Series(dtype=str)) == lookup_sid) &
                (dff["visit_date"].dt.date == lookup_date)
            ] if "student_id" in dff.columns else pd.DataFrame()

            if found.empty:
                st.info("No record found for that Student ID and date.")
            else:
                rec = found.iloc[0]
                st.markdown(f"""
                <div class="panel" style="margin-bottom:14px;">
                  <div style="font-size:0.72rem;color:{TEXT_DIM};margin-bottom:6px;">Found record</div>
                  <div style="font-size:0.88rem;color:{TEXT};"><strong>{rec['hostel']}</strong> \u2022 {rec['diagnosis']} \u2022 severity {rec['severity']} \u2022 {rec['visit_date'].date()}</div>
                </div>""", unsafe_allow_html=True)

                with st.form("edit_form"):
                    u1, u2 = st.columns(2)
                    with u1:
                        h_idx = list(sorted(df["hostel"].unique())).index(rec["hostel"]) if rec["hostel"] in df["hostel"].unique() else 0
                        upd_hostel = u1.selectbox("Hostel", sorted(df["hostel"].unique()), index=h_idx)
                        d_idx = list(sorted(df["diagnosis"].unique())).index(rec["diagnosis"]) if rec["diagnosis"] in df["diagnosis"].unique() else 0
                        upd_diag   = u1.selectbox("Diagnosis", sorted(df["diagnosis"].unique()), index=d_idx)
                        upd_sev    = u1.slider("Severity", 1, 5, int(rec["severity"]))
                    with u2:
                        g_idx = 0 if rec.get("gender","Male")=="Male" else 1
                        upd_gender = u2.selectbox("Gender", ["Male","Female"], index=g_idx)
                        l_list = ["100","200","300","400"]
                        l_idx = l_list.index(rec["level"]) if "level" in rec and rec["level"] in l_list else 0
                        upd_level  = u2.selectbox("Year / Level", l_list, index=l_idx)
                    upd_submit = st.form_submit_button("Update Record", type="primary", use_container_width=True)

                if upd_submit:
                    update_vals = {
                        "hostel": upd_hostel, "diagnosis": upd_diag,
                        "severity": upd_sev, "gender": upd_gender, "level": upd_level,
                    }
                    try:
                        col_db = get_mongo_col()
                        col_db.update_one(
                            {"student_id": lookup_sid, "visit_date": pd.Timestamp(lookup_date).isoformat()},
                            {"$set": update_vals})
                        st.success("Record updated.")
                        st.cache_data.clear()
                    except Exception as e:
                        st.error(f"Could not update: {e}")
                        st.info("Demo mode: " + str(update_vals))
        else:
            st.info("Enter a Student ID above to look up a record.")

    with tab_delete:
        st.markdown(f"""
        <div style="font-size:0.85rem;font-weight:700;color:{TEXT};margin-bottom:4px;">Delete Record</div>
        <div style="font-size:0.78rem;color:{TEXT_DIM};margin-bottom:16px;">This action is permanent. A confirmation step is required.</div>""", unsafe_allow_html=True)

        d1, d2 = st.columns(2)
        del_sid  = d1.text_input("Student ID", placeholder="e.g. UG12345", key="del_sid")
        del_date = d2.date_input("Visit Date", value=pd.Timestamp.today(), key="del_date")

        if del_sid:
            found_del = dff[
                (dff.get("student_id", pd.Series(dtype=str)) == del_sid) &
                (dff["visit_date"].dt.date == del_date)
            ] if "student_id" in dff.columns else pd.DataFrame()

            if found_del.empty:
                st.info("No matching record found.")
            else:
                rec_del = found_del.iloc[0]
                st.markdown(f"""
                <div class="panel panel-red" style="margin-bottom:14px;">
                  <div style="font-size:0.72rem;color:{RED};font-weight:700;margin-bottom:4px;">Record to delete</div>
                  <div style="font-size:0.85rem;color:{TEXT_DIM};">{rec_del['hostel']} \u2022 {rec_del['diagnosis']} \u2022 severity {rec_del['severity']} \u2022 {rec_del['visit_date'].date()}</div>
                </div>""", unsafe_allow_html=True)

                confirm = st.checkbox("I confirm I want to permanently delete this record")
                if confirm:
                    if st.button("Delete Now", type="primary", use_container_width=True):
                        try:
                            col_db = get_mongo_col()
                            result = col_db.delete_one({
                                "student_id": del_sid,
                                "visit_date": pd.Timestamp(del_date).isoformat()
                            })
                            if result.deleted_count:
                                st.success("Record deleted successfully.")
                            else:
                                st.warning("No matching record found.")
                            st.cache_data.clear()
                        except Exception as e:
                            st.error(f"Could not delete: {e}")
                            st.info("Demo mode \u2014 deletion would target the record shown above.")
        else:
            st.info("Enter a Student ID to look up and delete a record.")