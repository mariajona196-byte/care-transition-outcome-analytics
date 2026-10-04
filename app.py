import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Care Transition Efficiency Analytics",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "HHS_Unaccompanied_Alien_Children_Program.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)

    # Remove completely empty rows
    df = df.dropna(how="all").copy()

    # Convert Date column
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Remove rows where date is unavailable
    df = df.dropna(subset=["Date"]).copy()

    # Sort chronologically
    df = df.sort_values("Date")

    return df


df = load_data()

# --------------------------------------------------
# TITLE
# --------------------------------------------------
st.title("Care Transition Efficiency & Placement Outcome Analytics")

st.markdown(
    """
    **UAC Care Pipeline:**  
    CBP Custody → HHS Care → Sponsor Placement
    """
)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.header("Dashboard Filters")

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range

    filtered = df[
        (df["Date"].dt.date >= start_date)
        & (df["Date"].dt.date <= end_date)
    ].copy()
else:
    filtered = df.copy()

# --------------------------------------------------
# COLUMN NAMES
# --------------------------------------------------
APPREHENDED = "Children apprehended and placed in CBP custody"
CBP_CUSTODY = "Children in CBP custody"
TRANSFERRED = "Children transferred out of CBP custody"
HHS_CARE = "Children in HHS Care"
DISCHARGED = "Children discharged from HHS Care"

# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------
total_apprehended = filtered[APPREHENDED].sum()
total_transferred = filtered[TRANSFERRED].sum()
total_discharged = filtered[DISCHARGED].sum()

avg_cbp = filtered[CBP_CUSTODY].mean()
avg_hhs = filtered[HHS_CARE].mean()

transfer_ratio = (
    total_transferred / filtered[CBP_CUSTODY].sum() * 100
    if filtered[CBP_CUSTODY].sum() != 0
    else 0
)

discharge_ratio = (
    total_discharged / filtered[HHS_CARE].sum() * 100
    if filtered[HHS_CARE].sum() != 0
    else 0
)

total_entries = total_apprehended + total_transferred
total_exits = total_transferred + total_discharged

throughput = (
    total_exits / total_entries * 100
    if total_entries != 0
    else 0
)

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------
st.subheader("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Transfer Efficiency",
        f"{transfer_ratio:.1f}%"
    )

with col2:
    st.metric(
        "Discharge Effectiveness",
        f"{discharge_ratio:.1f}%"
    )

with col3:
    st.metric(
        "Pipeline Throughput",
        f"{throughput:.1f}%"
    )

with col4:
    st.metric(
        "Average HHS Care Load",
        f"{avg_hhs:,.0f}"
    )

# --------------------------------------------------
# PIPELINE SUMMARY
# --------------------------------------------------
st.subheader("Care Pipeline Summary")

pipeline_data = pd.DataFrame({
    "Stage": [
        "CBP Custody",
        "Transferred to HHS",
        "HHS Care",
        "Discharged"
    ],
    "Volume": [
        filtered[CBP_CUSTODY].sum(),
        total_transferred,
        filtered[HHS_CARE].sum(),
        total_discharged
    ]
})

fig_pipeline = px.bar(
    pipeline_data,
    x="Stage",
    y="Volume",
    text="Volume",
    title="Care Pipeline Movement"
)

fig_pipeline.update_traces(texttemplate="%{text:,.0f}")

st.plotly_chart(fig_pipeline, use_container_width=True)

# --------------------------------------------------
# DAILY FLOW TREND
# --------------------------------------------------
st.subheader("Daily Care Transition Trends")

daily = filtered.copy()

fig_flow = px.line(
    daily,
    x="Date",
    y=[
        APPREHENDED,
        TRANSFERRED,
        DISCHARGED
    ],
    title="Daily Inflow, Transfers and Discharges"
)

st.plotly_chart(fig_flow, use_container_width=True)

# --------------------------------------------------
# ACTIVE CARE LOAD
# --------------------------------------------------
st.subheader("Active Care Load")

fig_load = px.line(
    filtered,
    x="Date",
    y=[
        CBP_CUSTODY,
        HHS_CARE
    ],
    title="CBP and HHS Active Care Loads"
)

st.plotly_chart(fig_load, use_container_width=True)

# --------------------------------------------------
# BACKLOG ANALYSIS
# --------------------------------------------------
st.subheader("Backlog / Accumulation Analysis")

backlog = filtered.copy()

backlog["Total Active Care Load"] = (
    backlog[CBP_CUSTODY] +
    backlog[HHS_CARE]
)

fig_backlog = px.line(
    backlog,
    x="Date",
    y="Total Active Care Load",
    title="Combined Active Care Load"
)

st.plotly_chart(fig_backlog, use_container_width=True)

# --------------------------------------------------
# WEEKDAY VS WEEKEND
# --------------------------------------------------
st.subheader("Weekday vs Weekend Analysis")

weekday_data = filtered.copy()

weekday_data["Day Type"] = weekday_data["Date"].dt.dayofweek.map(
    lambda x: "Weekend" if x >= 5 else "Weekday"
)

weekday_summary = (
    weekday_data
    .groupby("Day Type")[
        [TRANSFERRED, DISCHARGED]
    ]
    .mean()
    .reset_index()
)

fig_weekday = px.bar(
    weekday_summary,
    x="Day Type",
    y=[TRANSFERRED, DISCHARGED],
    barmode="group",
    title="Average Transfers and Discharges"
)

st.plotly_chart(fig_weekday, use_container_width=True)

# --------------------------------------------------
# MONTHLY OUTCOME TREND
# --------------------------------------------------
st.subheader("Monthly Placement Trend")

monthly = filtered.copy()

monthly["Month"] = monthly["Date"].dt.to_period("M").astype(str)

monthly_summary = (
    monthly
    .groupby("Month")[
        [TRANSFERRED, DISCHARGED]
    ]
    .sum()
    .reset_index()
)

fig_monthly = px.line(
    monthly_summary,
    x="Month",
    y=[TRANSFERRED, DISCHARGED],
    markers=True,
    title="Monthly Transfers and Discharges"
)

st.plotly_chart(fig_monthly, use_container_width=True)

# --------------------------------------------------
# ALERTS
# --------------------------------------------------
st.subheader("System Alerts")

recent = filtered.tail(7)

recent_inflow = recent[APPREHENDED].sum()
recent_discharge = recent[DISCHARGED].sum()

if recent_inflow > recent_discharge:
    st.warning(
        "⚠️ Recent inflows are higher than successful discharges. "
        "This may indicate increasing pressure on the care pipeline."
    )
else:
    st.success(
        "✅ Recent discharges are keeping pace with or exceeding "
        "recent apprehension inflows."
    )

# --------------------------------------------------
# DATA TABLE
# --------------------------------------------------
with st.expander("View Dataset"):
    st.dataframe(
        filtered,
        use_container_width=True
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")

st.caption(
    "Care Transition Efficiency & Placement Outcome Analytics | "
    "Python + Pandas + Plotly + Streamlit"
)
