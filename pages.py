import streamlit as st
import pandas as pd
import altair as alt
import os
import json
from datetime import datetime

from auth import login_page, signup_page, check_user_login, check_user_role, check_session_validity
from charts import show as show_charts
from advanced_charts import show_advanced_charts
from historical_dashboard import show_historical_dashboard
from real_time_monitor import show_real_time_monitor
from ml_engine import show_anomaly_detection, show_time_series_forecasting
from geo_visualization import show_geospatial_analysis
from correlation_engine import show_correlation_analysis
from performance import show_performance_dashboard, optimized_parse_file
from config import DEFAULT_LOG_DIR, EXAMPLE_LOG_FILE, DEFAULT_THEME
from utils import create_download_link

def home_page():
    """Display the home page with login/signup options."""
    st.title("Welcome to Log Analyser")
    st.markdown("""
    ### A comprehensive tool for analyzing various types of logs

    This application helps cybersecurity professionals analyze different types of logs including:
    - Browsing logs
    - Virus detection logs
    - Mail logs
    - And more...

    **Features:**
    - Interactive visualizations
    - Real-time analysis
    - Custom report generation
    - Multiple log format support

    Please log in or sign up to get started.
    """)

    # Display login/signup options in tabs
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        login_page()

    with tab2:
        signup_page()

    # Check if user is already logged in
    check_user_login()

def charts_page():
    """Display the charts page with log analysis visualizations."""
    # Check if user is logged in
    if not st.session_state.logged_in:
        st.warning("Please log in to view charts.")
        login_page()
        return

    # Check if session is still valid
    if not check_session_validity():
        return

    # Show charts
    show_charts()

def report_preview_page():
    """Display the report preview page."""
    # Check if user is logged in
    if not st.session_state.logged_in:
        st.warning("Please log in to view the report preview.")
        login_page()
        return

    # Check if session is still valid
    if not check_session_validity():
        return

    # Check if user has the required role
    if not check_user_role('analyst') and not check_user_role('admin'):
        st.error("You don't have permission to access this page.")
        return

    st.title("Report Generator")

    # Check if log data is available
    if 'log_data' not in st.session_state or st.session_state.log_data is None or st.session_state.log_data.empty:
        st.warning("No log data available. Please analyze logs in the Charts section first.")
        return

    # Get the log data
    df = st.session_state.log_data
    log_type = st.session_state.log_type if 'log_type' in st.session_state else "browsing"

    # Report configuration
    st.subheader("Configure Report")

    col1, col2 = st.columns(2)

    with col1:
        report_title = st.text_input("Report Title", f"{log_type.capitalize()} Log Analysis Report")
        report_description = st.text_area("Report Description", "Analysis of log data for security monitoring.")

    with col2:
        include_summary = st.checkbox("Include Summary Statistics", value=True)
        include_charts = st.checkbox("Include Visualizations", value=True)
        include_raw_data = st.checkbox("Include Raw Data", value=False)

    # Generate report
    if st.button("Generate Report"):
        generate_report(df, log_type, report_title, report_description, include_summary, include_charts, include_raw_data)

def advanced_charts_page():
    """Display the advanced charts page with Plotly visualizations."""
    # Check if user is logged in
    if not st.session_state.logged_in:
        st.warning("Please log in to view advanced charts.")
        login_page()
        return

    # Check if session is still valid
    if not check_session_validity():
        return

    # Show advanced charts
    show_advanced_charts()

def historical_dashboard_page():
    """Display the historical dashboard page."""
    # Check if user is logged in
    if not st.session_state.logged_in:
        st.warning("Please log in to view the historical dashboard.")
        login_page()
        return

    # Check if session is still valid
    if not check_session_validity():
        return

    # Show historical dashboard
    show_historical_dashboard()

def real_time_monitor_page():
    """Display the real-time monitoring page."""
    # Check if user is logged in
    if not st.session_state.logged_in:
        st.warning("Please log in to access the real-time monitor.")
        login_page()
        return

    # Check if session is still valid
    if not check_session_validity():
        return

    # Show real-time monitor
    show_real_time_monitor()

def anomaly_detection_page():
    """Display the anomaly detection page."""
    # Check if user is logged in
    if not st.session_state.logged_in:
        st.warning("Please log in to access anomaly detection.")
        login_page()
        return

    # Check if session is still valid
    if not check_session_validity():
        return

    # Check if user has the required role
    if not check_user_role('analyst') and not check_user_role('admin'):
        st.error("You don't have permission to access this page.")
        return

    # Show anomaly detection
    show_anomaly_detection()

def forecasting_page():
    """Display the time series forecasting page."""
    # Check if user is logged in
    if not st.session_state.logged_in:
        st.warning("Please log in to access forecasting.")
        login_page()
        return

    # Check if session is still valid
    if not check_session_validity():
        return

    # Check if user has the required role
    if not check_user_role('analyst') and not check_user_role('admin'):
        st.error("You don't have permission to access this page.")
        return

    # Show time series forecasting
    show_time_series_forecasting()

def geospatial_analysis_page():
    """Display the geospatial analysis page."""
    # Check if user is logged in
    if not st.session_state.logged_in:
        st.warning("Please log in to access geospatial analysis.")
        login_page()
        return

    # Check if session is still valid
    if not check_session_validity():
        return

    # Show geospatial analysis
    show_geospatial_analysis()

def correlation_analysis_page():
    """Display the correlation analysis page."""
    # Check if user is logged in
    if not st.session_state.logged_in:
        st.warning("Please log in to access correlation analysis.")
        login_page()
        return

    # Check if session is still valid
    if not check_session_validity():
        return

    # Check if user has the required role
    if not check_user_role('analyst') and not check_user_role('admin'):
        st.error("You don't have permission to access this page.")
        return

    # Show correlation analysis
    show_correlation_analysis()

def performance_dashboard_page():
    """Display the performance dashboard page."""
    # Check if user is logged in
    if not st.session_state.logged_in:
        st.warning("Please log in to access the performance dashboard.")
        login_page()
        return

    # Check if session is still valid
    if not check_session_validity():
        return

    # Check if user has the required role
    if not check_user_role('admin'):
        st.error("You don't have permission to access this page. Admin role required.")
        return

    # Show performance dashboard
    show_performance_dashboard()

def settings_page():
    """Display the settings page."""
    # Check if user is logged in
    if not st.session_state.logged_in:
        st.warning("Please log in to access settings.")
        login_page()
        return

    # Check if session is still valid
    if not check_session_validity():
        return

    st.title("Settings")

    # User preferences
    st.subheader("User Preferences")

    # Theme selection with toggle
    col1, col2 = st.columns([3, 1])

    with col1:
        theme = st.selectbox(
            "Theme",
            options=["Light", "Dark"],
            index=1 if st.session_state.get('theme', DEFAULT_THEME) == 'dark' else 0
        )

    with col2:
        # Add a toggle switch for dark/light mode
        is_dark = st.toggle("Dark Mode", value=st.session_state.get('theme', DEFAULT_THEME) == 'dark')
        # Sync the toggle with the selectbox
        if is_dark and theme == "Light":
            theme = "Dark"
        elif not is_dark and theme == "Dark":
            theme = "Light"

    # Default chart type
    default_chart_type = st.selectbox(
        "Default Chart Type",
        options=["Bar", "Pie", "Line", "Area"],
        index=0 if st.session_state.get('chart_type', 'bar') == 'bar' else
              1 if st.session_state.get('chart_type', 'bar') == 'pie' else
              2 if st.session_state.get('chart_type', 'bar') == 'line' else 3
    )

    # Real-time monitoring settings
    st.subheader("Real-time Monitoring Settings")

    # Syslog port
    syslog_port = st.number_input(
        "Syslog Port",
        min_value=1,
        max_value=65535,
        value=st.session_state.get('syslog_port', 514),
        help="Standard syslog port is 514"
    )

    # Save settings
    if st.button("Save Settings"):
        # Save settings to session state
        st.session_state.theme = theme.lower()
        st.session_state.chart_type = default_chart_type.lower()
        st.session_state.syslog_port = syslog_port
        st.success("Settings saved successfully!")

def generate_report(df, log_type, title, description, include_summary, include_charts, include_raw_data):
    """Generate a report based on the log data and configuration."""
    st.subheader("Generated Report")

    # Create a container for the report
    report_container = st.container()

    with report_container:
        # Report header
        st.markdown(f"# {title}")
        st.markdown(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        st.markdown(f"*Generated by: {st.session_state.username}*")
        st.markdown("---")

        # Report description
        st.markdown(f"## Description")
        st.markdown(description)
        st.markdown("---")

        # Summary statistics
        if include_summary:
            st.markdown(f"## Summary Statistics")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Logs", len(df))

            with col2:
                if log_type == "browsing":
                    unique_users = df['username'].nunique()
                    st.metric("Unique Users", unique_users)
                elif log_type == "virus":
                    unique_viruses = df['virus_name'].nunique() if 'virus_name' in df.columns else 0
                    st.metric("Unique Viruses", unique_viruses)
                elif log_type == "mail":
                    unique_senders = df['sender'].nunique() if 'sender' in df.columns else 0
                    st.metric("Unique Senders", unique_senders)

            with col3:
                if log_type == "browsing":
                    avg_bandwidth = df['bandwidth'].mean() if 'bandwidth' in df.columns else 0
                    st.metric("Avg Bandwidth", f"{avg_bandwidth:.2f}")
                elif log_type == "virus":
                    high_severity = df[df['severity'] == 'high'].shape[0] if 'severity' in df.columns else 0
                    st.metric("High Severity", high_severity)
                elif log_type == "mail":
                    avg_size = df['size'].mean() if 'size' in df.columns else 0
                    st.metric("Avg Mail Size", f"{avg_size:.2f}")

            with col4:
                if log_type == "browsing":
                    error_count = df[df['status_code'] >= 400].shape[0] if 'status_code' in df.columns else 0
                    st.metric("Error Responses", error_count)
                elif log_type == "virus":
                    quarantined = df[df['action_taken'] == 'quarantined'].shape[0] if 'action_taken' in df.columns else 0
                    st.metric("Quarantined", quarantined)
                elif log_type == "mail":
                    spam_count = df[df['spam_score'] > 0.5].shape[0] if 'spam_score' in df.columns else 0
                    st.metric("Spam Detected", spam_count)

            st.markdown("---")

        # Visualizations
        if include_charts:
            st.markdown(f"## Visualizations")

            if log_type == "browsing":
                # IP address distribution
                st.markdown("### IP Address Distribution")
                ip_count = df["ip_address"].value_counts().reset_index()
                ip_count.columns = ["IP Address", "Count"]

                chart = alt.Chart(ip_count).mark_bar().encode(
                    x=alt.X('IP Address:N', sort='-y', title="IP Address"),
                    y=alt.Y('Count:Q', title="Number of Requests"),
                    color=alt.Color('IP Address:N')
                ).properties(width=700, height=400)

                st.altair_chart(chart)

                # Status code distribution
                st.markdown("### Status Code Distribution")
                status_count = df["status_code"].value_counts().reset_index()
                status_count.columns = ["Status Code", "Count"]

                chart = alt.Chart(status_count).mark_bar().encode(
                    x=alt.X('Status Code:N', sort='-y', title="Status Code"),
                    y=alt.Y('Count:Q', title="Number of Requests"),
                    color=alt.Color('Status Code:N')
                ).properties(width=700, height=400)

                st.altair_chart(chart)

                # Category distribution
                st.markdown("### Category Distribution")
                category_count = df["category"].value_counts().reset_index()
                category_count.columns = ["Category", "Count"]

                chart = alt.Chart(category_count).mark_bar().encode(
                    x=alt.X('Category:N', sort='-y', title="Category"),
                    y=alt.Y('Count:Q', title="Number of Requests"),
                    color=alt.Color('Category:N')
                ).properties(width=700, height=400)

                st.altair_chart(chart)

            elif log_type == "virus":
                # Placeholder for virus log charts
                st.markdown("### Virus Detection Distribution")
                if 'virus_name' in df.columns:
                    virus_count = df["virus_name"].value_counts().reset_index()
                    virus_count.columns = ["Virus Name", "Count"]

                    chart = alt.Chart(virus_count).mark_bar().encode(
                        x=alt.X('Virus Name:N', sort='-y', title="Virus Name"),
                        y=alt.Y('Count:Q', title="Occurrences"),
                        color=alt.Color('Virus Name:N')
                    ).properties(width=700, height=400)

                    st.altair_chart(chart)

            elif log_type == "mail":
                # Placeholder for mail log charts
                st.markdown("### Email Sender Distribution")
                if 'sender' in df.columns:
                    sender_count = df["sender"].value_counts().reset_index()
                    sender_count.columns = ["Sender", "Count"]

                    chart = alt.Chart(sender_count).mark_bar().encode(
                        x=alt.X('Sender:N', sort='-y', title="Sender"),
                        y=alt.Y('Count:Q', title="Number of Emails"),
                        color=alt.Color('Sender:N')
                    ).properties(width=700, height=400)

                    st.altair_chart(chart)

            st.markdown("---")

        # Raw data
        if include_raw_data:
            st.markdown(f"## Raw Data")
            st.dataframe(df)
            st.markdown("---")

        # Export options
        st.markdown(f"## Export Options")

        # Create download links
        st.markdown(create_download_link(df, f"{log_type}_report.csv"), unsafe_allow_html=True)

        # In a real app, you would add options to export as PDF, etc.
