import streamlit as st
import pandas as pd
import plotly.express as px
import random
import time
from collections import deque

st.set_page_config(page_title="Network Dashboard", layout="wide")
st.title("📊 Live Network Performance Dashboard (Simulated)")

# Use deque for efficient data storage (max 500 data points)
# Initialize in session_state so it doesn't get cleared
if 'data' not in st.session_state:
    st.session_state.data = deque(maxlen=500)

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

# --- Live update loop ---
while True:
    # --- SIMULATE A BURST OF PACKETS ---
    # This will make your charts look full, like your video
    num_new_packets = random.randint(5, 30)
    
    for _ in range(num_new_packets):
        new_row = {
            "timestamp": pd.Timestamp.now(),
            "src_ip": f"192.168.1.{random.randint(1, 50)}",
            "length": random.randint(50, 1500),
            "protocol": random.choice(['TCP', 'UDP', 'ICMP'])
        }
        st.session_state.data.append(new_row)
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(list(st.session_state.data))

    # --- KPIs ---
    total_packets_placeholder.metric("Total Packets (Last 500)", len(df))
    avg_size_placeholder.metric("Avg. Size (bytes)", f"{df['length'].mean():.0f}")
    unique_ips_placeholder.metric("Unique IPs", df['src_ip'].nunique())

    # --- Packet Count Over Time ---
    if not df.empty and len(df) > 1:
        time_series = df.set_index("timestamp").resample("1s").size().reset_index(name="count")
        
        if not time_series.empty:
            fig = px.line(
                time_series, 
                x="timestamp", 
                y="count", 
                title="Packets per Second (Live)"
            )
            # FIX: Removed the 'key' argument
            time_chart_placeholder.plotly_chart(fig, use_container_width=True) 

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
        # FIX: Removed the 'key' argument
        top_ips_placeholder.plotly_chart(bar_fig, use_container_width=True)

    # --- PROTOCOL PIE CHART ---
if not df.empty:
        proto_counts = df['protocol'].value_counts().reset_index()
        proto_counts.columns = ['protocol', 'count']
        
        proto_fig = px.pie(
            proto_counts, 
            names='protocol', 
            values='count', 
            title="Protocol Distribution"
        )
        # FIX: Removed the 'key' argument
        proto_dist_placeholder.plotly_chart(proto_fig, use_container_width=True)

    # Refresh every 2 seconds
    time.sleep(2)
