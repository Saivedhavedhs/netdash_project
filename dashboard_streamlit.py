import streamlit as st
import pandas as pd
from scapy.all import sniff, conf
import plotly.express as px
import threading
import time
from collections import deque

conf.L3socket = True

st.set_page_config(page_title="Live Network Dashboard", layout="wide")
st.title("📊 Live Network Performance Dashboard")

packet_data = deque(maxlen=500)
data_lock = threading.Lock()

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

kpi_cols = st.columns(3)
total_packets_placeholder = kpi_cols[0].empty()
avg_size_placeholder = kpi_cols[1].empty()
unique_ips_placeholder = kpi_cols[2].empty()

st.subheader("📈 Packet Count Over Time (Last 500 Packets)")
time_chart_placeholder = st.empty()

chart_cols = st.columns(2)
top_ips_placeholder = chart_cols[0].empty()
proto_dist_placeholder = chart_cols[1].empty()

if 'sniffer_thread' not in st.session_state:
    st.session_state.stop_sniffing = False
    st.session_state.sniffer_thread = threading.Thread(target=start_sniffer, daemon=True)
    st.session_state.sniffer_thread.start()
    st.success("✅ Packet sniffer started in the background!")

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

    total_packets = len(df)
    avg_packet_size = df['length'].mean()
    unique_ips = df['src_ip'].nunique()

    total_packets_placeholder.metric(label="Total Packets", value=f"{total_packets}")
    avg_size_placeholder.metric(label="Avg. Size (bytes)", value=f"{avg_packet_size:,.0f}")
    unique_ips_placeholder.metric(label="Unique IPs", value=f"{unique_ips}")

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

    top_src_ips = df['src_ip'].value_counts().head(10).reset_index()
    top_src_ips.columns = ['src_ip', 'count']

    if not top_src_ips.empty:
        ip_fig = px.bar(
            top_src_ips,
            x='src_ip',
            y='count',
            title="Top 10 Source IPs",
            labels={'src_ip': 'Source IP', 'count': 'Packets'}
        )
        top_ips_placeholder.plotly_chart(ip_fig, use_container_width=True)

    proto_counts = df['protocol'].map({6: 'TCP', 17: 'UDP', 1: 'ICMP'}).fillna('Other').value_counts().reset_index()
    proto_counts.columns = ['protocol', 'count']

    if not proto_counts.empty:
        proto_fig = px.pie(
            proto_counts,
            names='protocol',
            values='count',
            title="Protocol Distribution"
        )
        proto_dist_placeholder.plotly_chart(proto_fig, use_container_width=True)

    time.sleep(2)

