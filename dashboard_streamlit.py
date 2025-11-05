<<<<<<< HEAD
# ---- DEBUG PLOT BLOCK (remove after verifying) ----
import streamlit as st
import pandas as pd
import plotly.express as px

st.markdown("## DEBUG: Plot tests (remove after debugging)")

test_df = pd.DataFrame({
    "time": pd.date_range("2025-01-01", periods=6, freq="T"),
    "value": [1, 3, 2, 5, 4, 6],
    "category": ["A","B","A","B","A","B"]
})

fig_line = px.line(test_df, x="time", y="value", title="Line test")
st.plotly_chart(fig_line, use_container_width=True)

fig_bar = px.bar(test_df.groupby("category").value.mean().reset_index(), x="category", y="value", title="Bar test")
st.plotly_chart(fig_bar, use_container_width=True)

fig_pie = px.pie(test_df, names="category", title="Pie test")
st.plotly_chart(fig_pie, use_container_width=True)
# ---- END DEBUG BLOCK ----

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
=======
import streamlit as st
import pandas as pd
from scapy.all import sniff, conf
import plotly.express as px
import threading
import time
from collections import deque

# --- FIX for Windows Layer-3 sniffing ---
conf.L3socket = True

# --- Streamlit Setup ---
st.set_page_config(page_title="Live Network Dashboard", layout="wide")
st.title("📊 Live Network Performance Dashboard")

# --- Data Storage ---
packet_data = deque(maxlen=500)
data_lock = threading.Lock()

# --- Packet Sniffer Function ---
def process_packet(packet):
    timestamp = time.time()
    if 'IP' in packet:
        with data_lock:
            packet_data.append({
                "timestamp": timestamp,
                "src_ip": packet['IP'].src,
                "dst_ip": packet['IP'].dst,
                "protocol": packet['IP'].proto,
                "length": len(packet)
            })

def start_sniffer():
    sniff(prn=process_packet, store=False, stop_filter=lambda x: st.session_state.get('stop_sniffing', False))

# --- Streamlit Placeholders ---
kpi_cols = st.columns(3)
total_packets_placeholder = kpi_cols[0].empty()
avg_size_placeholder = kpi_cols[1].empty()
unique_ips_placeholder = kpi_cols[2].empty()

st.subheader("📈 Packet Count Over Time (Last 500 Packets)")
time_chart_placeholder = st.empty()

chart_cols = st.columns(2)
top_ips_placeholder = chart_cols[0].empty()
proto_dist_placeholder = chart_cols[1].empty()

# --- Start Sniffer in Background Thread ---
if 'sniffer_thread' not in st.session_state:
    st.session_state.stop_sniffing = False
    st.session_state.sniffer_thread = threading.Thread(target=start_sniffer, daemon=True)
    st.session_state.sniffer_thread.start()
    st.success("✅ Packet sniffer started in the background!")

# --- Live Update Loop ---
# Streamlit reruns the script automatically, so we use st.empty() containers for updates
placeholder = st.empty()

while True:
    with data_lock:
        if not packet_data:
            st.warning("No packets captured yet... listening...")
            time.sleep(2)
            continue

        df = pd.DataFrame(list(packet_data))

    if df.empty:
        time.sleep(2)
        continue

    # --- KPIs ---
    total_packets = len(df)
    avg_packet_size = df['length'].mean()
    unique_ips = df['src_ip'].nunique()

    total_packets_placeholder.metric(label="Total Packets", value=f"{total_packets}")
    avg_size_placeholder.metric(label="Avg. Size (bytes)", value=f"{avg_packet_size:,.0f}")
    unique_ips_placeholder.metric(label="Unique IPs", value=f"{unique_ips}")

    # --- Packet Count Over Time ---
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    time_series = df.set_index('timestamp').resample('1S').size().reset_index(name='count')

    if not time_series.empty:
        time_fig = px.line(
            time_series,
            x='timestamp',
            y='count',
            title="Packets per Second (Live)",
            labels={'timestamp': 'Time', 'count': 'Packets'}
        )
        time_chart_placeholder.plotly_chart(time_fig, use_container_width=True)

    # --- Top Source IPs ---
    top_src_ips = df['src_ip'].value_counts().head(10).reset_index()
    top_src_ips.columns = ['src_ip', 'count']  # ✅ rename properly

    if not top_src_ips.empty:
        ip_fig = px.bar(
            top_src_ips,
            x='src_ip',
            y='count',
            title="Top 10 Source IPs",
            labels={'src_ip': 'Source IP', 'count': 'Packets'}
        )
        top_ips_placeholder.plotly_chart(ip_fig, use_container_width=True)

    # --- Protocol Distribution ---
    proto_counts = df['protocol'].map({6: 'TCP', 17: 'UDP', 1: 'ICMP'}).fillna('Other').value_counts().reset_index()
    proto_counts.columns = ['protocol', 'count']  # ✅ rename properly

    if not proto_counts.empty:
        proto_fig = px.pie(
            proto_counts,
            names='protocol',
            values='count',
            title="Protocol Distribution"
        )
        proto_dist_placeholder.plotly_chart(proto_fig, use_container_width=True)

    # --- Update Interval ---
    time.sleep(2)

>>>>>>> 95587995bf9b35260da35052dfd7c297b530db18
