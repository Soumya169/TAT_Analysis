import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LogiSense – Transport Analytics",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp { background: #0a0e1a; color: #e2e8f0; }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background: #111827 !important;
        border-right: 1px solid #1e2d45;
    }
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 { color: #00d4ff; }

    /* METRIC CARDS */
    [data-testid="stMetric"] {
        background: #111827;
        border: 1px solid #1e2d45;
        border-radius: 12px;
        padding: 16px !important;
    }
    [data-testid="stMetricLabel"] { color: #64748b !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 1px; }
    [data-testid="stMetricValue"] { color: #00d4ff !important; font-family: 'JetBrains Mono', monospace !important; font-size: 26px !important; }
    [data-testid="stMetricDelta"] { font-size: 11px !important; }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        background: #111827;
        border-radius: 10px;
        padding: 4px;
        gap: 4px;
        border: 1px solid #1e2d45;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #64748b;
        border-radius: 8px;
        font-weight: 500;
        font-size: 13px;
        padding: 8px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #7c3aed, #5b21b6) !important;
        color: white !important;
    }

    /* DATAFRAME */
    [data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
    .dataframe { background: #111827 !important; }

    /* SELECTBOX / MULTISELECT */
    [data-baseweb="select"] > div {
        background: #111827 !important;
        border-color: #1e2d45 !important;
        color: #e2e8f0 !important;
        border-radius: 8px !important;
    }

    /* UPLOAD */
    [data-testid="stFileUploader"] {
        background: #111827;
        border: 2px dashed #1e2d45;
        border-radius: 14px;
        padding: 12px;
    }

    /* HEADERS */
    h1 { color: #00d4ff !important; font-weight: 700 !important; }
    h2 { color: #e2e8f0 !important; font-weight: 600 !important; }
    h3 { color: #94a3b8 !important; font-weight: 500 !important; font-size: 14px !important; text-transform: uppercase; letter-spacing: 1px; }

    /* DIVIDER */
    hr { border-color: #1e2d45 !important; }

    /* BUTTON */
    .stDownloadButton button {
        background: linear-gradient(135deg, #10b981, #059669) !important;
        color: #000 !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
    }

    /* SECTION BOX */
    .section-box {
        background: #111827;
        border: 1px solid #1e2d45;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .calc-tag {
        display: inline-block;
        background: rgba(0,212,255,0.1);
        color: #00d4ff;
        border: 1px solid rgba(0,212,255,0.3);
        border-radius: 6px;
        padding: 2px 10px;
        font-size: 11px;
        font-family: 'JetBrains Mono', monospace;
        margin: 3px;
    }
    .hero-title {
        font-size: 36px;
        font-weight: 800;
        background: linear-gradient(90deg, #00d4ff, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
        margin-bottom: 6px;
    }
    .hero-sub { color: #64748b; font-size: 14px; margin-bottom: 24px; }
    .badge-green { background: #052e16; color: #10b981; border-radius: 999px; padding: 2px 10px; font-size: 11px; font-weight: 600; }
    .badge-amber { background: #451a03; color: #f59e0b; border-radius: 999px; padding: 2px 10px; font-size: 11px; font-weight: 600; }
    .badge-red   { background: #450a0a; color: #ef4444; border-radius: 999px; padding: 2px 10px; font-size: 11px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────
ALL_COLUMNS = [
    "Trip ID", "Vehicle Number", "Transporter Code", "Transporter Name",
    "Challan Number", "Challan Quantity", "Material Code", "Mat. Group",
    "Material Group", "Mat. Des", "Unloader Alias", "Gate Entry No.", "PO No",
    "Supplier Code", "Supplier Name", "First Weight", "First Weighbridge No",
    "Second Weight", "Second WeighBridge No", "PO line no", "Challan Date",
    "OBD No", "LR No", "LR Date", "Lease/Stock Holder Code", "Gate Entry Type",
    "Ref Doc Type", "Driver Name", "Driver License No", "Driver Contact No",
    "Material Reg Datetime", "Shift", "WT Type", "Net Weight",
    "Ready Queue Date Time", "Yard TAT", "Plant TAT", "Total TAT",
    "ParkIn", "YardIn", "YardOut", "GateIn", "GrossWeight", "TareWeight",
    "GateOut", "Plant GO Hour", "YI-GI", "GI-GW", "GW-TW", "TW-GO", "GI-GO"
]

DATETIME_COLS = ["ParkIn", "YardIn", "YardOut", "GateIn", "GateOut",
                 "Material Reg Datetime", "Ready Queue Date Time",
                 "Challan Date", "LR Date"]

CALC_DEFINITIONS = {
    "YI-GI": ("GateIn − YardIn",       "Yard In to Gate In (hrs)"),
    "GI-GW": ("GrossWeight − GateIn",  "Gate In to Gross Weighment (hrs)"),
    "GW-TW": ("TareWeight − GrossWeight","Gross to Tare Weighment (hrs)"),
    "TW-GO": ("GateOut − TareWeight",  "Tare Weighment to Gate Out (hrs)"),
    "GI-GO": ("GateOut − GateIn",      "Total Plant Processing Time (hrs)"),
    "Net Weight": ("GrossWeight − TareWeight", "Delivered material weight"),
}

COLORS = ["#00d4ff","#7c3aed","#10b981","#f59e0b","#ef4444",
          "#3b82f6","#ec4899","#8b5cf6","#14b8a6","#f97316",
          "#a78bfa","#34d399","#fbbf24","#f87171","#60a5fa"]

PLOTLY_THEME = dict(
    paper_bgcolor="#111827",
    plot_bgcolor="#0f172a",
    font=dict(family="Inter", color="#94a3b8", size=12),
    xaxis=dict(gridcolor="#1e2d45", zerolinecolor="#1e2d45"),
    yaxis=dict(gridcolor="#1e2d45", zerolinecolor="#1e2d45"),
    legend=dict(bgcolor="#111827", bordercolor="#1e2d45", borderwidth=1)
)

# ─────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────
def parse_datetime(series):
    try:
        return pd.to_datetime(series, dayfirst=True, errors='coerce')
    except:
        return pd.NaT

def hours_diff(a, b):
    diff = (b - a).dt.total_seconds() / 3600
    diff[diff < 0] = None
    return diff.round(3)

def fmt_hours(val):
    if pd.isna(val): return "–"
    return f"{val:.2f} hrs"

def color_tat(val):
    if pd.isna(val): return ""
    if val < 2: return "background-color:#052e16;color:#10b981"
    if val < 6: return "background-color:#451a03;color:#f59e0b"
    return "background-color:#450a0a;color:#ef4444"

@st.cache_data
def load_and_process(file_bytes, file_name):
    if file_name.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(file_bytes))
    else:
        df = pd.read_excel(io.BytesIO(file_bytes))

    # Parse datetime columns
    for col in DATETIME_COLS:
        if col in df.columns:
            df[col] = parse_datetime(df[col])

    # Auto-calculate TAT columns
    col_map = {c.lower().replace(' ','').replace('-','').replace('_',''):c for c in df.columns}

    def get_col(*names):
        for n in names:
            key = n.lower().replace(' ','').replace('-','').replace('_','')
            if key in col_map:
                return df[col_map[key]]
        return None

    yardin  = get_col("YardIn", "Yard In", "YARDIN")
    gatein  = get_col("GateIn",  "Gate In",  "GATEIN")
    grosswt = get_col("GrossWeight", "Gross Weight", "GrossWt")
    tarewt  = get_col("TareWeight",  "Tare Weight",  "TareWt")
    gateout = get_col("GateOut", "Gate Out", "GATEOUT")

    # Only calculate if columns are datetime
    def safe_diff(a, b, col_name):
        if a is not None and b is not None:
            try:
                if pd.api.types.is_datetime64_any_dtype(a) and pd.api.types.is_datetime64_any_dtype(b):
                    if col_name not in df.columns or df[col_name].isna().all():
                        df[col_name] = hours_diff(a, b)
            except: pass

    safe_diff(yardin,  gatein,  "YI-GI")
    safe_diff(gatein,  grosswt, "GI-GW")
    safe_diff(grosswt, tarewt,  "GW-TW")
    safe_diff(tarewt,  gateout, "TW-GO")
    safe_diff(gatein,  gateout, "GI-GO")

    # Net Weight
    if "Net Weight" not in df.columns or df["Net Weight"].isna().all():
        gw_col = get_col("GrossWeight", "First Weight")
        tw_col = get_col("TareWeight",  "Second Weight")
        if gw_col is not None and tw_col is not None:
            try:
                df["Net Weight"] = pd.to_numeric(gw_col, errors='coerce') - pd.to_numeric(tw_col, errors='coerce')
            except: pass

    # Force numeric on TAT cols
    for c in ["YI-GI","GI-GW","GW-TW","TW-GO","GI-GO","Yard TAT","Plant TAT","Total TAT","Net Weight"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')

    return df

def plotly_bar(df_grp, x, y, title, color=None, h=380):
    fig = px.bar(df_grp, x=x, y=y, title=title, color=color,
                 color_discrete_sequence=COLORS, height=h)
    fig.update_layout(**PLOTLY_THEME, title_font_color="#e2e8f0",
                      title_font_size=14, margin=dict(t=40,b=10,l=10,r=10))
    fig.update_traces(marker_line_width=0)
    return fig

def plotly_pie(df_grp, names, values, title, h=380):
    fig = px.pie(df_grp, names=names, values=values, title=title,
                 color_discrete_sequence=COLORS, height=h, hole=0.4)
    fig.update_layout(**PLOTLY_THEME, title_font_color="#e2e8f0",
                      title_font_size=14, margin=dict(t=40,b=10,l=10,r=10))
    fig.update_traces(textfont_color="#e2e8f0")
    return fig

def plotly_line(df_grp, x, y, title, h=340):
    fig = px.line(df_grp, x=x, y=y, title=title,
                  color_discrete_sequence=["#00d4ff"], height=h, markers=True)
    fig.update_layout(**PLOTLY_THEME, title_font_color="#e2e8f0",
                      title_font_size=14, margin=dict(t=40,b=10,l=10,r=10))
    fig.update_traces(line_width=2.5, marker_size=5)
    return fig

def plotly_box(df, y_col, x_col, title, h=380):
    fig = px.box(df, x=x_col, y=y_col, title=title,
                 color=x_col, color_discrete_sequence=COLORS, height=h)
    fig.update_layout(**PLOTLY_THEME, title_font_color="#e2e8f0",
                      title_font_size=14, margin=dict(t=40,b=10,l=10,r=10),
                      showlegend=False)
    return fig

def plotly_hist(series, title, h=340):
    fig = px.histogram(series.dropna(), title=title, nbins=20,
                       color_discrete_sequence=["#7c3aed"], height=h)
    fig.update_layout(**PLOTLY_THEME, title_font_color="#e2e8f0",
                      title_font_size=14, margin=dict(t=40,b=10,l=10,r=10))
    return fig

def kpi(col, label, value, delta=None, unit=""):
    col.metric(label, f"{value}{unit}" if value != '–' else '–', delta)

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚛 LogiSense")
    st.markdown("**Transport Analytics Platform**")
    st.markdown("---")

    uploaded = st.file_uploader(
        "📂 Upload Excel / CSV",
        type=["xlsx", "xls", "csv"],
        help="Upload your transport trip data file"
    )

    st.markdown("---")
    st.markdown("### 📐 Auto-Calculated Columns")
    for col, (formula, desc) in CALC_DEFINITIONS.items():
        st.markdown(f"""
        <div style='margin-bottom:10px;'>
            <span class='calc-tag'>{col} = {formula}</span><br>
            <span style='font-size:11px;color:#64748b;padding-left:4px'>{desc}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⏱ TAT Color Guide")
    st.markdown("""
    <span class='badge-green'>🟢 &lt; 2 hrs — Good</span><br><br>
    <span class='badge-amber'>🟡 2–6 hrs — Normal</span><br><br>
    <span class='badge-red'>🔴 &gt; 6 hrs — Delayed</span>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# MAIN AREA — NO FILE
# ─────────────────────────────────────────────────────────────
if uploaded is None:
    st.markdown("""
    <div style='text-align:center;padding:60px 20px'>
        <div style='font-size:72px;margin-bottom:16px'>🚛</div>
        <div class='hero-title'>LogiSense</div>
        <div class='hero-sub'>Upload your transport Excel file to begin instant analysis</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""<div class='section-box'>
            <h3>📊 Auto Analysis</h3>
            <p style='color:#94a3b8;font-size:13px;margin-top:8px'>
            Upload any Excel with trip data. All TAT calculations (YI-GI, GI-GW, GW-TW, TW-GO, GI-GO) 
            are done automatically — no formulas needed.
            </p></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class='section-box'>
            <h3>📈 Smart Charts</h3>
            <p style='color:#94a3b8;font-size:13px;margin-top:8px'>
            Bar charts, pie charts, line trends, box plots, histograms — 
            all driven by dropdown selections. Change grouping or metric in one click.
            </p></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class='section-box'>
            <h3>⬇️ Export Results</h3>
            <p style='color:#94a3b8;font-size:13px;margin-top:8px'>
            Download the processed Excel file with all calculated columns 
            filled in — ready to share or use in further analysis.
            </p></div>""", unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────
with st.spinner("⚙️ Processing your data..."):
    df = load_and_process(uploaded.read(), uploaded.name)

st.success(f"✅ Loaded **{len(df):,} rows** from `{uploaded.name}`")

# ─────────────────────────────────────────────────────────────
# GLOBAL FILTERS (top bar)
# ─────────────────────────────────────────────────────────────
st.markdown("### 🎛 Global Filters")
fc1, fc2, fc3, fc4 = st.columns(4)

with fc1:
    trans_opts = ["All"] + sorted(df["Transporter Name"].dropna().unique().tolist()) if "Transporter Name" in df.columns else ["All"]
    sel_trans = st.selectbox("🏢 Transporter", trans_opts)

with fc2:
    shift_opts = ["All"] + sorted(df["Shift"].dropna().unique().tolist()) if "Shift" in df.columns else ["All"]
    sel_shift = st.selectbox("🕐 Shift", shift_opts)

with fc3:
    matgrp_opts = ["All"] + sorted(df["Mat. Group"].dropna().unique().tolist()) if "Mat. Group" in df.columns else ["All"]
    sel_mat = st.selectbox("📦 Material Group", matgrp_opts)

with fc4:
    gate_opts = ["All"] + sorted(df["Gate Entry Type"].dropna().unique().tolist()) if "Gate Entry Type" in df.columns else ["All"]
    sel_gate = st.selectbox("🚪 Gate Entry Type", gate_opts)

# Apply filters
fdf = df.copy()
if sel_trans != "All" and "Transporter Name" in fdf.columns: fdf = fdf[fdf["Transporter Name"]==sel_trans]
if sel_shift != "All" and "Shift" in fdf.columns:           fdf = fdf[fdf["Shift"]==sel_shift]
if sel_mat   != "All" and "Mat. Group" in fdf.columns:      fdf = fdf[fdf["Mat. Group"]==sel_mat]
if sel_gate  != "All" and "Gate Entry Type" in fdf.columns: fdf = fdf[fdf["Gate Entry Type"]==sel_gate]

st.markdown(f"<p style='color:#64748b;font-size:12px'>Showing {len(fdf):,} of {len(df):,} records after filters</p>", unsafe_allow_html=True)
st.markdown("---")

# ─────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", "⏱ TAT Analysis", "📈 Charts", "📋 Data Table", "⬇️ Export"
])

# ══════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### 📌 Key Performance Indicators")
    k1,k2,k3,k4,k5,k6 = st.columns(6)

    total_trips = len(fdf)
    unique_vehicles = fdf["Vehicle Number"].nunique() if "Vehicle Number" in fdf.columns else "–"
    unique_trans = fdf["Transporter Name"].nunique() if "Transporter Name" in fdf.columns else "–"
    avg_net = fdf["Net Weight"].mean() if "Net Weight" in fdf.columns else None
    avg_gigo = fdf["GI-GO"].mean() if "GI-GO" in fdf.columns else None
    avg_plant = fdf["Plant TAT"].mean() if "Plant TAT" in fdf.columns else None

    kpi(k1, "Total Trips", f"{total_trips:,}")
    kpi(k2, "Unique Vehicles", unique_vehicles)
    kpi(k3, "Transporters", unique_trans)
    kpi(k4, "Avg Net Weight", f"{avg_net:.1f}" if avg_net else "–")
    kpi(k5, "Avg GI-GO (hrs)", f"{avg_gigo:.2f}" if avg_gigo else "–")
    kpi(k6, "Avg Plant TAT", f"{avg_plant:.2f}" if avg_plant else "–")

    st.markdown("---")

    # Row 1 charts
    col1, col2 = st.columns(2)
    with col1:
        if "Transporter Name" in fdf.columns:
            top_trans = fdf["Transporter Name"].value_counts().head(10).reset_index()
            top_trans.columns = ["Transporter","Trips"]
            st.plotly_chart(plotly_bar(top_trans,"Transporter","Trips","Top 10 Transporters by Trip Count"), use_container_width=True)

    with col2:
        if "Shift" in fdf.columns:
            shift_cnt = fdf["Shift"].value_counts().reset_index()
            shift_cnt.columns = ["Shift","Count"]
            st.plotly_chart(plotly_pie(shift_cnt,"Shift","Count","Trip Distribution by Shift"), use_container_width=True)

    # Daily trend
    date_col = None
    for c in ["GateIn","Material Reg Datetime","Challan Date"]:
        if c in fdf.columns and pd.api.types.is_datetime64_any_dtype(fdf[c]):
            date_col = c
            break

    if date_col:
        daily = fdf.copy()
        daily["Date"] = daily[date_col].dt.date
        daily_cnt = daily.groupby("Date").size().reset_index(name="Trips")
        daily_cnt = daily_cnt.sort_values("Date").tail(60)
        st.plotly_chart(plotly_line(daily_cnt,"Date","Trips","Daily Trip Volume (Last 60 Days)"), use_container_width=True)

    # Supplier / Unloader
    col3, col4 = st.columns(2)
    with col3:
        if "Supplier Name" in fdf.columns:
            sup = fdf["Supplier Name"].value_counts().head(8).reset_index()
            sup.columns = ["Supplier","Trips"]
            st.plotly_chart(plotly_bar(sup,"Supplier","Trips","Top 8 Suppliers"), use_container_width=True)
    with col4:
        if "Unloader Alias" in fdf.columns:
            unl = fdf["Unloader Alias"].value_counts().head(8).reset_index()
            unl.columns = ["Unloader","Trips"]
            st.plotly_chart(plotly_pie(unl,"Unloader","Trips","Trips by Unloader"), use_container_width=True)


# ══════════════════════════════════════════════════════════════
# TAB 2 — TAT ANALYSIS
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### ⏱ TAT Stage Breakdown")

    tat_stages = ["YI-GI","GI-GW","GW-TW","TW-GO","GI-GO"]
    avail_tat = [s for s in tat_stages if s in fdf.columns]

    if avail_tat:
        tc = st.columns(len(avail_tat))
        for i, stage in enumerate(avail_tat):
            val = fdf[stage].mean()
            tc[i].metric(stage, f"{val:.2f} hrs" if not pd.isna(val) else "–")

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            avg_vals = {s: fdf[s].mean() for s in avail_tat if not pd.isna(fdf[s].mean())}
            fig_bar = go.Figure(go.Bar(
                x=list(avg_vals.keys()),
                y=list(avg_vals.values()),
                marker_color=COLORS[:len(avg_vals)],
                text=[f"{v:.2f}h" for v in avg_vals.values()],
                textposition="outside"
            ))
            fig_bar.update_layout(**PLOTLY_THEME, title="Average Hours per TAT Stage",
                                  title_font_color="#e2e8f0", height=380,
                                  margin=dict(t=40,b=10,l=10,r=10))
            st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            st.plotly_chart(plotly_hist(fdf["GI-GO"], "GI-GO Distribution (Total Plant Time)"), use_container_width=True)

        # Transporter-wise TAT
        st.markdown("### 🏢 Transporter-wise TAT")

        tat_col_sel = st.selectbox("Select TAT Stage", avail_tat, key="trans_tat_sel")
        group_by_sel = st.selectbox("Group By", ["Transporter Name","Shift","Unloader Alias","Gate Entry Type","Mat. Group"],
                                    key="tat_grp_sel")

        if group_by_sel in fdf.columns and tat_col_sel in fdf.columns:
            col1, col2 = st.columns(2)
            with col1:
                avg_by = fdf.groupby(group_by_sel)[tat_col_sel].mean().dropna().sort_values(ascending=False).head(12).reset_index()
                avg_by.columns = [group_by_sel, "Avg TAT (hrs)"]
                st.plotly_chart(plotly_bar(avg_by, group_by_sel, "Avg TAT (hrs)",
                                           f"Avg {tat_col_sel} by {group_by_sel}"), use_container_width=True)
            with col2:
                top_groups = fdf[group_by_sel].value_counts().head(8).index.tolist()
                box_df = fdf[fdf[group_by_sel].isin(top_groups)]
                st.plotly_chart(plotly_box(box_df, tat_col_sel, group_by_sel,
                                           f"{tat_col_sel} Spread by {group_by_sel}"), use_container_width=True)

        # Summary table
        st.markdown("### 📋 TAT Summary Table")
        if "Transporter Name" in fdf.columns:
            summary = fdf.groupby("Transporter Name")[avail_tat].agg(['mean','min','max','count']).round(2)
            summary.columns = [f"{s}_{m}" for s,m in summary.columns]
            st.dataframe(summary, use_container_width=True)
    else:
        st.warning("⚠️ No TAT columns found. Make sure your file has GateIn, GateOut, YardIn, GrossWeight, TareWeight columns.")


# ══════════════════════════════════════════════════════════════
# TAB 3 — CHARTS (CUSTOM)
# ══════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 📈 Custom Chart Builder")

    # Dropdowns
    cc1, cc2, cc3, cc4 = st.columns(4)

    cat_cols = [c for c in ["Transporter Name","Shift","Unloader Alias","Gate Entry Type",
                             "Mat. Group","Material Group","WT Type","Ref Doc Type",
                             "Supplier Name","Vehicle Number"] if c in fdf.columns]
    num_cols = [c for c in ["Net Weight","GI-GO","GW-TW","TW-GO","YI-GI","GI-GW",
                             "Plant TAT","Yard TAT","Total TAT","Challan Quantity",
                             "GrossWeight","TareWeight"] if c in fdf.columns]

    with cc1:
        group_col = st.selectbox("📂 Group By (X-Axis / Slice)", cat_cols, key="cust_grp")
    with cc2:
        metric_options = ["Trip Count"] + num_cols
        metric_col = st.selectbox("📏 Metric (Y-Axis)", metric_options, key="cust_met")
    with cc3:
        agg_fn = st.selectbox("∑ Aggregation", ["Mean","Sum","Count","Max","Min"], key="cust_agg")
    with cc4:
        chart_type = st.selectbox("📊 Chart Type", ["Bar","Horizontal Bar","Pie","Donut","Line","Box Plot"], key="cust_chart")

    top_n = st.slider("Show Top N groups", 5, 30, 12, key="cust_topn")

    # Build grouped data
    if metric_col == "Trip Count":
        grp = fdf[group_col].value_counts().head(top_n).reset_index()
        grp.columns = [group_col, "Value"]
        y_label = "Trip Count"
    else:
        agg_map = {"Mean":"mean","Sum":"sum","Count":"count","Max":"max","Min":"min"}
        grp = fdf.groupby(group_col)[metric_col].agg(agg_map[agg_fn]).dropna().sort_values(ascending=False).head(top_n).reset_index()
        grp.columns = [group_col, "Value"]
        y_label = f"{agg_fn} {metric_col}"

    grp[group_col] = grp[group_col].astype(str).str[:25]

    chart_title = f"{y_label} by {group_col}"

    if chart_type == "Bar":
        fig = plotly_bar(grp, group_col, "Value", chart_title)
    elif chart_type == "Horizontal Bar":
        fig = px.bar(grp.sort_values("Value"), x="Value", y=group_col, orientation='h',
                     title=chart_title, color_discrete_sequence=COLORS, height=420)
        fig.update_layout(**PLOTLY_THEME, title_font_color="#e2e8f0", margin=dict(t=40,b=10,l=10,r=10))
    elif chart_type in ["Pie","Donut"]:
        hole = 0.4 if chart_type=="Donut" else 0
        fig = px.pie(grp, names=group_col, values="Value", title=chart_title,
                     color_discrete_sequence=COLORS, height=420, hole=hole)
        fig.update_layout(**PLOTLY_THEME, title_font_color="#e2e8f0", margin=dict(t=40,b=10,l=10,r=10))
    elif chart_type == "Line":
        fig = px.line(grp, x=group_col, y="Value", title=chart_title,
                      color_discrete_sequence=["#00d4ff"], height=420, markers=True)
        fig.update_layout(**PLOTLY_THEME, title_font_color="#e2e8f0", margin=dict(t=40,b=10,l=10,r=10))
    elif chart_type == "Box Plot":
        if metric_col != "Trip Count" and metric_col in fdf.columns:
            top_g = fdf[group_col].value_counts().head(top_n).index.tolist()
            box_df = fdf[fdf[group_col].isin(top_g)]
            fig = plotly_box(box_df, metric_col, group_col, chart_title)
        else:
            st.warning("Box Plot requires a numeric metric (not Trip Count).")
            fig = None

    if fig:
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Weight Analysis
    st.markdown("### ⚖️ Weight Analysis")
    wc1, wc2 = st.columns(2)
    with wc1:
        if all(c in fdf.columns for c in ["GrossWeight","TareWeight","Net Weight"]):
            weight_grp = st.selectbox("Group Weight by", cat_cols, key="wt_grp")
            wdf = fdf.groupby(weight_grp)[["GrossWeight","TareWeight","Net Weight"]].mean().dropna().head(12).reset_index()
            fig_w = go.Figure()
            for col_w, color_w in [("GrossWeight","#00d4ff"),("TareWeight","#7c3aed"),("Net Weight","#10b981")]:
                fig_w.add_trace(go.Bar(name=col_w, x=wdf[weight_grp].astype(str).str[:20],
                                       y=wdf[col_w], marker_color=color_w))
            fig_w.update_layout(**PLOTLY_THEME, barmode='group', title="Avg Weight by Group",
                                 title_font_color="#e2e8f0", height=380, margin=dict(t=40,b=10,l=10,r=10))
            st.plotly_chart(fig_w, use_container_width=True)
    with wc2:
        if "Net Weight" in fdf.columns:
            st.plotly_chart(plotly_hist(fdf["Net Weight"], "Net Weight Distribution"), use_container_width=True)

    # Scatter
    st.markdown("---")
    st.markdown("### 🔵 Scatter / Correlation")
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        scatter_x = st.selectbox("X Axis", num_cols, key="sc_x")
    with sc2:
        scatter_y = st.selectbox("Y Axis", num_cols[::-1], key="sc_y")
    with sc3:
        scatter_color = st.selectbox("Color by", ["None"] + cat_cols, key="sc_c")

    scatter_df = fdf[[scatter_x, scatter_y] + ([scatter_color] if scatter_color != "None" else [])].dropna()
    fig_sc = px.scatter(scatter_df, x=scatter_x, y=scatter_y,
                        color=scatter_color if scatter_color != "None" else None,
                        color_discrete_sequence=COLORS, height=400,
                        title=f"{scatter_y} vs {scatter_x}",
                        opacity=0.7)
    fig_sc.update_layout(**PLOTLY_THEME, title_font_color="#e2e8f0", margin=dict(t=40,b=10,l=10,r=10))
    st.plotly_chart(fig_sc, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# TAB 4 — DATA TABLE
# ══════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 📋 Data Table")

    dt1, dt2, dt3 = st.columns([2,1,1])
    with dt1:
        search_text = st.text_input("🔍 Search (Vehicle No, Trip ID, Transporter...)", "", key="search")
    with dt2:
        show_cols = st.multiselect(
            "📌 Select Columns to Show",
            options=fdf.columns.tolist(),
            default=[c for c in ["Trip ID","Vehicle Number","Transporter Name","Challan Number",
                                  "Shift","GrossWeight","TareWeight","Net Weight",
                                  "GateIn","GateOut","YI-GI","GI-GW","GW-TW","TW-GO","GI-GO",
                                  "Plant TAT","Total TAT"] if c in fdf.columns],
            key="col_sel"
        )
    with dt3:
        sort_col = st.selectbox("↕ Sort By", [""] + fdf.columns.tolist(), key="sort_col")
        sort_asc = st.checkbox("Ascending", value=False, key="sort_asc")

    # Apply search
    display_df = fdf.copy()
    if search_text:
        mask = display_df.astype(str).apply(lambda col: col.str.contains(search_text, case=False, na=False)).any(axis=1)
        display_df = display_df[mask]

    if show_cols:
        display_df = display_df[show_cols]

    if sort_col and sort_col in display_df.columns:
        display_df = display_df.sort_values(sort_col, ascending=sort_asc)

    st.markdown(f"<p style='color:#64748b;font-size:12px'>{len(display_df):,} rows shown</p>", unsafe_allow_html=True)
    st.dataframe(display_df.head(1000), use_container_width=True, height=520)


# ══════════════════════════════════════════════════════════════
# TAB 5 — EXPORT
# ══════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### ⬇️ Export Processed Data")

    ex1, ex2 = st.columns(2)

    with ex1:
        st.markdown("""<div class='section-box'>
        <h3>📥 Full Processed Dataset</h3>
        <p style='color:#94a3b8;font-size:13px;margin:10px 0'>
        Download the complete dataset with all auto-calculated TAT columns filled in.
        All original columns preserved + calculated columns added.
        </p></div>""", unsafe_allow_html=True)

        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as writer:
            fdf.to_excel(writer, index=False, sheet_name="Processed Data")
        buf.seek(0)
        st.download_button(
            "⬇️ Download Full Excel",
            data=buf,
            file_name=f"LogiSense_Processed_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with ex2:
        st.markdown("""<div class='section-box'>
        <h3>📊 TAT Summary Report</h3>
        <p style='color:#94a3b8;font-size:13px;margin:10px 0'>
        Download a summarized TAT report grouped by Transporter — 
        includes mean, min, max for each TAT stage.
        </p></div>""", unsafe_allow_html=True)

        tat_cols_avail = [c for c in ["YI-GI","GI-GW","GW-TW","TW-GO","GI-GO","Plant TAT","Total TAT"] if c in fdf.columns]
        if "Transporter Name" in fdf.columns and tat_cols_avail:
            summary_exp = fdf.groupby("Transporter Name")[tat_cols_avail].agg(['mean','min','max','count']).round(2)
            summary_exp.columns = [f"{s}_{m.upper()}" for s,m in summary_exp.columns]
            summary_exp = summary_exp.reset_index()

            buf2 = io.BytesIO()
            with pd.ExcelWriter(buf2, engine='openpyxl') as writer:
                summary_exp.to_excel(writer, index=False, sheet_name="TAT Summary")
            buf2.seek(0)
            st.download_button(
                "⬇️ Download TAT Summary",
                data=buf2,
                file_name=f"LogiSense_TAT_Summary_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    st.markdown("---")
    st.markdown("### 📋 Quick Stats")
    if tat_cols_avail:
        st.dataframe(fdf[tat_cols_avail].describe().round(2), use_container_width=True)