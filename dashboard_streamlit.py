import streamlit as st
import pandas as pd
import plotly.express as px
import random
import time
from collections import deque

st.set_page_config(page_title="Network Dashboard", layout="wide")
st.title("📊 Live Network Performance Dashboard (Simulated)")

# Use deque for efficient data storage (max 500 data points)
data = deque(maxlen=500)

# --- Streamlit Placeholders ---
kpi_cols = st.columns(3)
total_packets_placeholder = kpi_cols[0].empty()
avg_size_placeholder = kpi_cols[1].empty()
unique_ips_placeholder = kpi_cols[2].empty()

st.subheader("📈 Packet Count Over Time (Live)")
time_chart_placeholder = st.empty()

chart_cols = st.columns(2)
top_ips_placeholder = chart_cols[0].empty()
proto_dist_placeholder = chart_cols[1].empty()

# Simple demo loop that generates simulated data
while True:
    # Simulate a new packet
    new_row = {
        "timestamp": pd.Timestamp.now(),
        "src_ip": f"192.168.1.{random.randint(1, 50)}",
        "length": random.randint(50, 1500),
        "protocol": random.choice(['TCP', 'UDP', 'ICMP']) # <-- ADDED THIS
    }
    data.append(new_row)
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(list(data))

    # --- KPIs ---
    total_packets_placeholder.metric("Total Packets (Last 500)", len(df))
    avg_size_placeholder.metric("Avg. Size (bytes)", f"{df['length'].mean():.0f}")
    unique_ips_placeholder.metric("Unique IPs", df['src_ip'].nunique())

    # --- Packet Count Over Time ---
    if not df.empty:
        time_series = df.set_index("timestamp").resample("1s").size().reset_index(name="count")
        
        if not time_series.empty:
            fig = px.line(
                time_series, 
                x="timestamp", 
                y="count", 
                title="Packets per Second (Live)"
            )
            # This is the line that had the IndentationError. It is now correct.
            time_chart_placeholder.plotly_chart(fig, use_container_width=True, key="time_chart") 

    # --- Top Source IPs ---
    if not df.empty:
        top_src_ips = df['src_ip'].value_counts().head(10).reset_index()
        top_src_ips.columns = ['src_ip', 'count']
        
        bar_fig = px.bar(
            top_src_ips, 
            x='src_ip', 
            y='count', 
            title="Top 10 Source IPs"
        )
        # This is the other line I told you to fix.
        top_ips_placeholder.plotly_chart(bar_fig, use_container_width=True, key="bar_chart")

    # --- PROTOCOL PIE CHART (TO MATCH YOUR VIDEO) ---
    if not df.empty:
        proto_counts = df['protocol'].value_counts().reset_index()
        proto_counts.columns = ['protocol', 'count']
        
        proto_fig = px.pie(
            proto_counts, 
            names='protocol', 
            values='count', 
            title="Protocol Distribution"
        )
        proto_dist_placeholder.plotly_chart(proto_fig, use_container_width=True, key="proto_chart")

    # Refresh every 2 seconds
    time.sleep(2)
