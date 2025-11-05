# dashboard_streamlit.py
import streamlit as st
import pandas as pd
import plotly.express as px
import random
import time

st.set_page_config(page_title="Network Dashboard", layout="wide")
st.title("📊 Live Network Performance Dashboard")

data = []

kpi_cols = st.columns(3)
total_packets_placeholder = kpi_cols[0].empty()
avg_size_placeholder = kpi_cols[1].empty()
unique_ips_placeholder = kpi_cols[2].empty()
time_chart_placeholder = st.empty()
top_ips_placeholder = st.empty()

# Simple demo loop that generates simulated data so you can deploy/test without packet capture
while True:
    new_row = {
        "timestamp": pd.Timestamp.now(),
        "src_ip": f"192.168.0.{random.randint(1, 50)}",
        "length": random.randint(50, 1500)
    }
    data.append(new_row)
    df = pd.DataFrame(data[-500:])

    total_packets_placeholder.metric("Total Packets", len(df))
    avg_size_placeholder.metric("Avg. Size (bytes)", f"{df['length'].mean():.0f}")
    unique_ips_placeholder.metric("Unique IPs", df['src_ip'].nunique())

    # packets per second (resample)
    if len(df) > 1:
        time_series = df.set_index("timestamp").resample("1s").size().reset_index(name="count")
    else:
        time_series = pd.DataFrame({"timestamp":[pd.Timestamp.now()], "count":[0]})

    fig = px.line(time_series, x="timestamp", y="count", title="Packets per Second (Live)")
    time_chart_placeholder.plotly_chart(fig, use_container_width=True, key="time_chart")

    top_src_ips = df['src_ip'].value_counts().head(10).reset_index()
    top_src_ips.columns = ['src_ip', 'count']
    bar_fig = px.bar(top_src_ips, x='src_ip', y='count', title="Top 10 Source IPs")
    top_ips_placeholder.plotly_chart(bar_fig, use_container_width=True, key="bar_chart")

    time.sleep(2)
