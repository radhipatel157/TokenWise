
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os

# Set page configuration with a custom theme and title
st.set_page_config(page_title="TokenWise: Solana Analytics", layout="wide", initial_sidebar_state="auto")

# Custom CSS for neon-themed styling
st.markdown("""
    <style>
    .stApp {
        background-color: #0a0a1f;
        color: #e0e0ff;
    }
    .main-title {
        font-size: 40px;
        font-weight: bold;
        color: #a100ff;
        text-align: center;
        padding: 20px;
        background: linear-gradient(90deg, #1c0b3a, #2a1a5e);
        border-radius: 8px;
        box-shadow: 0 0 15px rgba(161, 0, 255, 0.5);
        margin-bottom: 20px;
    }
    .metric-box {
        background: #1c0b3a;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #a100ff;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 0 10px rgba(161, 0, 255, 0.3);
    }
    .metric-box h4 {
        color: #e0e0ff;
        margin: 0;
        font-size: 16px;
    }
    .metric-box p {
        color: #00ffaa;
        font-size: 28px;
        font-weight: bold;
        margin: 5px 0;
    }
    .stButton>button {
        background-color: #a100ff;
        color: #e0e0ff;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #8000cc;
        box-shadow: 0 0 10px rgba(161, 0, 255, 0.7);
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1c0b3a;
        color: #e0e0ff;
        border-radius: 8px;
        margin: 0 5px;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #2a1a5e;
        color: #00ffaa;
    }
    .stTabs [aria-selected="true"] {
        background-color: #a100ff;
        color: #e0e0ff;
    }
    .filter-panel {
        background: #1c0b3a;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #a100ff;
    }
    </style>
""", unsafe_allow_html=True)

# Custom header
st.markdown('<div class="main-title">TokenWise: Solana Blockchain Analytics</div>', unsafe_allow_html=True)

# Connect to SQLite database
conn = sqlite3.connect("../backend/tokenwise.db")

# Filter panel (toggleable)
with st.expander("Filter Transactions", expanded=False):
    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
    st.subheader("Time Range Filter")
    days = st.slider("Select time range (days)", 1, 30, 7, help="Filter transactions by time range")
    start_time = (datetime.now() - timedelta(days=days)).isoformat()
    end_time = datetime.now().isoformat()
    st.markdown('</div>', unsafe_allow_html=True)

# Fetch data
query = f"SELECT * FROM transactions WHERE timestamp BETWEEN ? AND ?"
df = pd.read_sql_query(query, conn, params=(start_time, end_time))
holders = pd.read_sql_query("SELECT * FROM holders", conn)

# Tabbed interface
tab1, tab2, tab3 = st.tabs(["Market Metrics", "Visual Insights", "Data Export"])

# Tab 1: Market Metrics
with tab1:
    st.subheader("Market Activity Overview")
    col1, col2, col3 = st.columns(3)
    buys = len(df[df["isBuy"] == 1])
    sells = len(df[df["isBuy"] == 0])
    net_direction = "Buy-Heavy" if buys > sells else "Sell-Heavy"
    with col1:
        st.markdown(f'<div class="metric-box"><h4>Total Buys</h4><p>{buys}</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-box"><h4>Total Sells</h4><p>{sells}</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-box"><h4>Net Direction</h4><p>{net_direction}</p></div>', unsafe_allow_html=True)

# Tab 2: Visual Insights
with tab2:
    st.subheader("Transaction Analytics")
    col4, col5 = st.columns([1, 1])

    # Protocol usage (custom pie chart)
    with col4:
        protocol_counts = df["protocol"].value_counts().reset_index()
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=protocol_counts["protocol"],
                    values=protocol_counts["count"],
                    textinfo="label+percent",
                    marker=dict(
                        colors=["#a100ff", "#00ffaa", "#ff007a"],
                        line=dict(color="#e0e0ff", width=1.5)
                    ),
                    hovertemplate="%{label}: %{value} txs (%{percent})<extra></extra>",
                    pull=[0.1, 0, 0],  # Slightly explode first slice
                )
            ]
        )
        fig.update_layout(
            title="Protocol Usage",
            title_font_color="#00ffaa",
            paper_bgcolor="#0a0a1f",
            font_color="#e0e0ff",
            showlegend=True,
            margin=dict(t=50, b=20, l=20, r=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Active wallets (custom bar chart)
    with col5:
        wallet_activity = df["wallet"].value_counts().head(10).reset_index()
        fig2 = go.Figure(
            data=[
                go.Bar(
                    x=wallet_activity["wallet"],
                    y=wallet_activity["count"],
                    marker=dict(
                        colorscale="Plasma",
                        showscale=True,
                        color=wallet_activity["count"],
                        colorbar=dict(title="Tx Count"),
                    ),
                    hovertemplate="Wallet: %{x}<br>Tx Count: %{y}<extra></extra>",
                )
            ]
        )
        fig2.update_layout(
            title="Top Active Wallets",
            title_font_color="#00ffaa",
            xaxis_title="Wallet Address",
            yaxis_title="Transaction Count",
            paper_bgcolor="#0a0a1f",
            font_color="#e0e0ff",
            xaxis=dict(tickangle=45, tickfont=dict(size=9)),
            margin=dict(t=50, b=50, l=20, r=20),
        )
        st.plotly_chart(fig2, use_container_width=True)

# Tab 3: Data Export
with tab3:
    st.subheader("Export Transaction Data")
    col6, col7 = st.columns(2)
    with col6:
        if st.button("Export as CSV", key="csv_export"):
            df.to_csv("../data/transactions.csv", index=False)
            st.success("Exported to data/transactions.csv")
    with col7:
        if st.button("Export as JSON", key="json_export"):
            df.to_json("../data/transactions.json", orient="records", indent=2)
            st.success("Exported to data/transactions.json")

# Close database connection
conn.close()