"""
Real-time log monitoring module for the Log Analyzer application.
"""
import streamlit as st
import socket
import threading
import queue
import pandas as pd
from datetime import datetime
import time
import re
from typing import Dict, List, Optional, Union, Any, Tuple, Generator

from config import LOG_TYPES
from log_parser import LogParser
from utils import format_timestamp

# Create a queue to store logs from the listener
log_queue = queue.Queue()

# Define the IP and port for syslog listening
SYSLOG_IP = "0.0.0.0"  # Listens on all available IPs
SYSLOG_PORT = 514      # Standard syslog port

def start_syslog_listener() -> Generator[str, None, None]:
    """
    Start a UDP socket listener for syslog messages.
    
    Yields:
        str: Decoded syslog message
    """
    try:
        # Create a UDP socket for syslog
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((SYSLOG_IP, SYSLOG_PORT))
        st.sidebar.success(f"Listening for syslog messages on {SYSLOG_IP}:{SYSLOG_PORT}")
        
        while True:
            data, addr = sock.recvfrom(4096)  # Buffer size of 4096 bytes
            message = data.decode('utf-8', errors='ignore')  # Convert bytes to string
            yield message
    except Exception as e:
        st.sidebar.error(f"Error in syslog listener: {e}")
        yield f"Error: {e}"

def capture_logs() -> None:
    """
    Capture logs from the syslog listener and push them into the queue.
    """
    for log in start_syslog_listener():
        log_queue.put(log)
        time.sleep(0.1)  # Small delay to prevent CPU overuse

def parse_syslog_message(message: str, log_type: str = "browsing") -> Dict[str, Any]:
    """
    Parse a syslog message into a structured format.
    
    Args:
        message: The syslog message to parse
        log_type: The type of log (browsing, virus, mail)
        
    Returns:
        Dict: Parsed log entry
    """
    # Extract timestamp from syslog format
    timestamp_match = re.match(r'^(\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2})', message)
    timestamp = datetime.now()
    if timestamp_match:
        try:
            timestamp_str = timestamp_match.group(1)
            timestamp = datetime.strptime(timestamp_str, "%b %d %H:%M:%S")
            # Add current year since syslog doesn't include it
            timestamp = timestamp.replace(year=datetime.now().year)
        except Exception:
            pass
    
    # Extract IP address using regex
    ip_match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', message)
    ip_address = ip_match.group(0) if ip_match else "Unknown"
    
    # Basic parsing based on log type
    if log_type == "browsing":
        # Try to extract URL
        url_match = re.search(r'https?://[^\s]+', message)
        url = url_match.group(0) if url_match else "Unknown"
        
        # Try to extract status code
        status_match = re.search(r'\b[1-5][0-9]{2}\b', message)
        status_code = int(status_match.group(0)) if status_match else 0
        
        return {
            "timestamp": timestamp,
            "ip_address": ip_address,
            "username": "Unknown",
            "url": url,
            "bandwidth": 0,
            "status_code": status_code,
            "content_type": "Unknown",
            "category": "Unknown",
            "device_info": "Unknown",
            "raw_message": message
        }
    
    elif log_type == "virus":
        # Try to extract virus name
        virus_match = re.search(r'virus|malware|trojan|infected|quarantine', message, re.IGNORECASE)
        virus_name = virus_match.group(0) if virus_match else "Unknown"
        
        return {
            "timestamp": timestamp,
            "ip_address": ip_address,
            "username": "Unknown",
            "virus_name": virus_name,
            "file_path": "Unknown",
            "action_taken": "Unknown",
            "scan_engine": "Unknown",
            "severity": "Unknown",
            "raw_message": message
        }
    
    elif log_type == "mail":
        # Try to extract email addresses
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', message)
        email = email_match.group(0) if email_match else "Unknown"
        
        return {
            "timestamp": timestamp,
            "sender": email,
            "recipient": "Unknown",
            "subject": "Unknown",
            "size": 0,
            "status": "Unknown",
            "attachment_count": 0,
            "spam_score": 0.0,
            "raw_message": message
        }
    
    # Generic log format
    return {
        "timestamp": timestamp,
        "message": message
    }

def show_real_time_monitor():
    """
    Display the real-time log monitoring interface.
    """
    st.title("Real-time Log Monitoring")
    
    # Check if user is logged in
    if not st.session_state.logged_in:
        st.warning("Please log in to access the real-time monitor.")
        return
    
    # Sidebar controls
    with st.sidebar:
        st.subheader("Monitor Settings")
        
        # Log type selection
        log_type = st.selectbox(
            "Log Type to Monitor",
            options=["browsing", "virus", "mail", "auto-detect"],
            index=0
        )
        
        # Start/Stop monitoring
        if 'monitoring_active' not in st.session_state:
            st.session_state.monitoring_active = False
            
        if st.session_state.monitoring_active:
            if st.button("Stop Monitoring"):
                st.session_state.monitoring_active = False
                st.success("Monitoring stopped")
        else:
            if st.button("Start Monitoring"):
                st.session_state.monitoring_active = True
                # Start the monitoring thread
                if 'monitor_thread' not in st.session_state or not st.session_state.monitor_thread.is_alive():
                    st.session_state.monitor_thread = threading.Thread(target=capture_logs, daemon=True)
                    st.session_state.monitor_thread.start()
                st.success("Monitoring started")
        
        # Clear logs button
        if st.button("Clear Logs"):
            if 'real_time_logs' in st.session_state:
                st.session_state.real_time_logs = pd.DataFrame()
            st.success("Logs cleared")
        
        # Max logs to display
        max_logs = st.slider("Max Logs to Display", 10, 1000, 100)
    
    # Initialize logs DataFrame if not exists
    if 'real_time_logs' not in st.session_state:
        st.session_state.real_time_logs = pd.DataFrame()
    
    # Display current status
    status_container = st.empty()
    if st.session_state.monitoring_active:
        status_container.success("Monitoring Active - Listening for logs...")
    else:
        status_container.warning("Monitoring Inactive - Click 'Start Monitoring' to begin")
    
    # Create containers for logs and visualizations
    log_container = st.container()
    viz_container = st.container()
    
    # Process any logs in the queue
    if st.session_state.monitoring_active:
        while not log_queue.empty():
            log_message = log_queue.get()
            
            # Parse the log message
            parsed_log = parse_syslog_message(log_message, log_type)
            
            # Convert to DataFrame row
            log_df = pd.DataFrame([parsed_log])
            
            # Append to existing logs
            if st.session_state.real_time_logs.empty:
                st.session_state.real_time_logs = log_df
            else:
                st.session_state.real_time_logs = pd.concat([st.session_state.real_time_logs, log_df], ignore_index=True)
            
            # Keep only the most recent logs
            if len(st.session_state.real_time_logs) > max_logs:
                st.session_state.real_time_logs = st.session_state.real_time_logs.tail(max_logs)
    
    # Display logs
    with log_container:
        st.subheader("Recent Logs")
        if not st.session_state.real_time_logs.empty:
            st.dataframe(st.session_state.real_time_logs)
        else:
            st.info("No logs received yet. Start monitoring to see logs.")
    
    # Display visualizations if we have logs
    with viz_container:
        if not st.session_state.real_time_logs.empty and len(st.session_state.real_time_logs) > 1:
            st.subheader("Log Visualizations")
            
            # Create tabs for different visualizations
            tab1, tab2 = st.tabs(["IP Analysis", "Time Analysis"])
            
            with tab1:
                # IP address distribution
                if "ip_address" in st.session_state.real_time_logs.columns:
                    ip_counts = st.session_state.real_time_logs["ip_address"].value_counts().reset_index()
                    ip_counts.columns = ["IP Address", "Count"]
                    
                    st.bar_chart(ip_counts.set_index("IP Address"))
            
            with tab2:
                # Time-based analysis
                if "timestamp" in st.session_state.real_time_logs.columns:
                    # Group by hour
                    st.session_state.real_time_logs['hour'] = st.session_state.real_time_logs['timestamp'].dt.hour
                    hour_counts = st.session_state.real_time_logs['hour'].value_counts().sort_index().reset_index()
                    hour_counts.columns = ["Hour", "Count"]
                    
                    st.line_chart(hour_counts.set_index("Hour"))

# Run the monitor if this file is executed directly
if __name__ == "__main__":
    show_real_time_monitor()
