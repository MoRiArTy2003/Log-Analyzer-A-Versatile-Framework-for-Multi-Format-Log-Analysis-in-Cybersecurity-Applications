# import streamlit as st
# import pandas as pd
# import altair as alt
# import time

# def show():
#     st.title("Table Conversion to Charts")

#     # File uploader to accept external text file
#     uploaded_file = st.file_uploader("Choose a text file", type="txt")

#     # Check if file is being uploaded
#     if uploaded_file is not None:
#         with st.spinner("Processing file..."):
#             time.sleep(2)

#         try:
#             # Read and decode the file content
#             file_content = uploaded_file.read().decode("utf-8")

#             # Split the file content by lines
#             lines = file_content.splitlines()

#             # Initialize an empty list to store each row of the table
#             data_list = []

#             # Function to validate if a line contains valid data
#             def is_valid_row(data_parts):
#                 return len(data_parts) >= 9

#             # Process each line and extract data if it's valid
#             for line in lines:
#                 data_parts = line.split()
#                 if is_valid_row(data_parts):
#                     data_list.append(data_parts[:9])  # Limit to 9 fields to prevent unexpected formats

#             # Check if any valid data was processed
#             if not data_list:
#                 st.error("No valid data found in the file. Ensure the file is formatted correctly.")
#                 return

#             # Define column names
#             columns = ["ID", "IP Address", "Name", "Domain:Port", "Bandwidth", "Status Code", "Unknown", "Category", "Additional Info"]

#             # Convert the list of rows into a DataFrame
#             df = pd.DataFrame(data_list, columns=columns)

#             # Convert "Bandwidth" and "Status Code" columns to numeric for plotting
#             df["Bandwidth"] = pd.to_numeric(df["Bandwidth"], errors='coerce')
#             df["Status Code"] = pd.to_numeric(df["Status Code"], errors='coerce')

#             # Show the data in a table
#             st.dataframe(df)

#             # Validate if numeric data exists for plotting
#             if df["Bandwidth"].isnull().all() or df["Status Code"].isnull().all():
#                 st.error("The file contains invalid numeric data for 'Bandwidth' or 'Status Code'. Please check the data.")
#                 return

#             # Define a fixed width for the charts
#             chart_width = 700  # Fixed pixel width for charts

#             # Section: Create charts for specific columns
#             st.subheader("Charts for IP Address, Bandwidth, and Status Code")

#             # Bar Chart for IP Address occurrences
#             st.write("### Bar Chart: Occurrences of each IP Address")
#             ip_count = df["IP Address"].value_counts().reset_index()
#             ip_count.columns = ["IP Address", "Count"]

#             ip_chart = alt.Chart(ip_count).mark_bar().encode(
#                 x=alt.X('IP Address:N', sort='-y', title="IP Address"),
#                 y=alt.Y('Count:Q', title="Occurrences"),
#                 color=alt.Color('IP Address:N', legend=alt.Legend(title="IP Address"))  # Add legend for IP Addresses
#             ).properties(
#                 width=chart_width,
#                 height=400
#             )
#             st.altair_chart(ip_chart)

#             # Pie Chart for IP Address occurrences
#             st.write("### Pie Chart: IP Address Distribution")
#             ip_pie = alt.Chart(ip_count).mark_arc().encode(
#                 theta=alt.Theta(field="Count", type="quantitative", title="Occurrences"),
#                 color=alt.Color(field="IP Address", type="nominal", legend=alt.Legend(title="IP Address"))
#             ).properties(
#                 width=chart_width,
#                 height=400
#             )
#             st.altair_chart(ip_pie)

#             # Histogram for "Bandwidth" column
#             st.write("### Histogram: Distribution of Bandwidth")
#             bandwidth_hist = alt.Chart(df).mark_bar().encode(
#                 alt.X("Bandwidth:Q", bin=alt.Bin(maxbins=30), title="Bandwidth"),
#                 y='count()',
#                 color=alt.Color('Bandwidth:Q', legend=alt.Legend(title="Bandwidth"))  # Add legend for Bandwidth
#             ).properties(
#                 width=chart_width,
#                 height=400
#             )
#             st.altair_chart(bandwidth_hist)

#             # Pie Chart for Bandwidth occurrences
#             st.write("### Pie Chart: Bandwidth Distribution")
#             bandwidth_count = df["Bandwidth"].value_counts().reset_index()
#             bandwidth_count.columns = ["Bandwidth", "Count"]

#             bandwidth_pie = alt.Chart(bandwidth_count).mark_arc().encode(
#                 theta=alt.Theta(field="Count", type="quantitative", title="Occurrences"),
#                 color=alt.Color(field="Bandwidth", type="quantitative", legend=alt.Legend(title="Bandwidth"))
#             ).properties(
#                 width=chart_width,
#                 height=400
#             )
#             st.altair_chart(bandwidth_pie)

#             # Bar Chart for "Status Code" occurrences
#             st.write("### Bar Chart: Status Code Frequencies")
#             status_count = df["Status Code"].value_counts().reset_index()
#             status_count.columns = ["Status Code", "Count"]

#             status_chart = alt.Chart(status_count).mark_bar().encode(
#                 x=alt.X('Status Code:O', title="Status Code"),
#                 y=alt.Y('Count:Q', title="Occurrences"),
#                 color=alt.Color('Status Code:O', legend=alt.Legend(title="Status Code"))  # Add legend for Status Codes
#             ).properties(
#                 width=chart_width,
#                 height=400
#             )
#             st.altair_chart(status_chart)

#             # Pie Chart for Status Code occurrences
#             st.write("### Pie Chart: Status Code Distribution")
#             status_pie = alt.Chart(status_count).mark_arc().encode(
#                 theta=alt.Theta(field="Count", type="quantitative", title="Occurrences"),
#                 color=alt.Color(field="Status Code", type="nominal", legend=alt.Legend(title="Status Code"))
#             ).properties(
#                 width=chart_width,
#                 height=400
#             )
#             st.altair_chart(status_pie)

#         except Exception as e:
#             st.error(f"An error occurred while processing the file: {e}")

#     else:
#         st.info("Please upload a text file.")

#     st.button("Rerun")

# import streamlit as st
# import pandas as pd
# import altair as alt
# import time
# import boto3
# import io

# # Load AWS credentials from secrets
# def create_s3_client():
#     return boto3.client(
#         's3',
#         aws_access_key_id=st.secrets["aws"]["aws_access_key_id"],
#         aws_secret_access_key=st.secrets["aws"]["aws_secret_access_key"],
#         region_name=st.secrets["aws"]["aws_region"]
#     )

# def read_s3_file(bucket_name, file_key):
#     s3 = create_s3_client()
#     obj = s3.get_object(Bucket=bucket_name, Key=file_key)
#     file_content = obj['Body'].read().decode('utf-8')
#     return file_content

# def show():
#     st.title("Table Conversion to Charts")

#     bucket_name = st.text_input("Enter S3 Bucket Name")
#     file_key = st.text_input("Enter S3 File Key (Path)")

#     if bucket_name and file_key:
#         with st.spinner("Fetching file from S3..."):
#             time.sleep(2)

#         try:
#             # Fetch the file content from S3
#             file_content = read_s3_file(bucket_name, file_key)

#             # Split and process the file content
#             lines = file_content.splitlines()

#             data_list = []
#             def is_valid_row(data_parts):
#                 return len(data_parts) >= 9

#             for line in lines:
#                 data_parts = line.split()
#                 if is_valid_row(data_parts):
#                     data_list.append(data_parts[:9])

#             if not data_list:
#                 st.error("No valid data found in the file. Ensure the file is formatted correctly.")
#                 return

#             columns = ["ID", "IP Address", "Name", "Domain:Port", "Bandwidth", "Status Code", "Unknown", "Category", "Additional Info"]
#             df = pd.DataFrame(data_list, columns=columns)
#             df["Bandwidth"] = pd.to_numeric(df["Bandwidth"], errors='coerce')
#             df["Status Code"] = pd.to_numeric(df["Status Code"], errors='coerce')
#             st.dataframe(df)

#             if df["Bandwidth"].isnull().all() or df["Status Code"].isnull().all():
#                 st.error("The file contains invalid numeric data for 'Bandwidth' or 'Status Code'.")
#                 return

#             chart_width = 700

#             st.subheader("Charts for IP Address, Bandwidth, and Status Code")
#             st.write("### Bar Chart: Occurrences of each IP Address")
#             ip_count = df["IP Address"].value_counts().reset_index()
#             ip_count.columns = ["IP Address", "Count"]

#             ip_chart = alt.Chart(ip_count).mark_bar().encode(
#                 x=alt.X('IP Address:N', sort='-y', title="IP Address"),
#                 y=alt.Y('Count:Q', title="Occurrences"),
#                 color=alt.Color('IP Address:N', legend=alt.Legend(title="IP Address"))
#             ).properties(width=chart_width, height=400)
#             st.altair_chart(ip_chart)

#             st.write("### Pie Chart: IP Address Distribution")
#             ip_pie = alt.Chart(ip_count).mark_arc().encode(
#                 theta=alt.Theta(field="Count", type="quantitative", title="Occurrences"),
#                 color=alt.Color(field="IP Address", type="nominal", legend=alt.Legend(title="IP Address"))
#             ).properties(width=chart_width, height=400)
#             st.altair_chart(ip_pie)

#             st.write("### Histogram: Distribution of Bandwidth")
#             bandwidth_hist = alt.Chart(df).mark_bar().encode(
#                 alt.X("Bandwidth:Q", bin=alt.Bin(maxbins=30), title="Bandwidth"),
#                 y='count()',
#                 color=alt.Color('Bandwidth:Q', legend=alt.Legend(title="Bandwidth"))
#             ).properties(width=chart_width, height=400)
#             st.altair_chart(bandwidth_hist)

#             st.write("### Pie Chart: Bandwidth Distribution")
#             bandwidth_count = df["Bandwidth"].value_counts().reset_index()
#             bandwidth_count.columns = ["Bandwidth", "Count"]

#             bandwidth_pie = alt.Chart(bandwidth_count).mark_arc().encode(
#                 theta=alt.Theta(field="Count", type="quantitative", title="Occurrences"),
#                 color=alt.Color(field="Bandwidth", type="quantitative", legend=alt.Legend(title="Bandwidth"))
#             ).properties(width=chart_width, height=400)
#             st.altair_chart(bandwidth_pie)

#             st.write("### Bar Chart: Status Code Frequencies")
#             status_count = df["Status Code"].value_counts().reset_index()
#             status_count.columns = ["Status Code", "Count"]

#             status_chart = alt.Chart(status_count).mark_bar().encode(
#                 x=alt.X('Status Code:O', title="Status Code"),
#                 y=alt.Y('Count:Q', title="Occurrences"),
#                 color=alt.Color('Status Code:O', legend=alt.Legend(title="Status Code"))
#             ).properties(width=chart_width, height=400)
#             st.altair_chart(status_chart)

#             st.write("### Pie Chart: Status Code Distribution")
#             status_pie = alt.Chart(status_count).mark_arc().encode(
#                 theta=alt.Theta(field="Count", type="quantitative", title="Occurrences"),
#                 color=alt.Color(field="Status Code", type="nominal", legend=alt.Legend(title="Status Code"))
#             ).properties(width=chart_width, height=400)
#             st.altair_chart(status_pie)

#         except Exception as e:
#             st.error(f"An error occurred: {e}")

#     else:
#         st.info("Please enter S3 bucket details.")

#     st.button("Rerun")

import streamlit as st
import pandas as pd
import altair as alt
import time
import os
import io
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple

from config import CHART_WIDTH, CHART_HEIGHT, COLOR_SCHEME, DEFAULT_LOG_TYPE, EXAMPLE_LOG_FILE
from log_parser import LogParser
from utils import get_time_periods, create_download_link, format_timestamp

# Cache for storing parsed log data
if 'log_data' not in st.session_state:
    st.session_state.log_data = None

if 'log_type' not in st.session_state:
    st.session_state.log_type = DEFAULT_LOG_TYPE

if 'time_period' not in st.session_state:
    st.session_state.time_period = "All Time"

if 'chart_type' not in st.session_state:
    st.session_state.chart_type = "bar"

def show():
    """Main function to display the charts page."""
    st.title("Log Analysis Dashboard")

    # Sidebar for controls
    with st.sidebar:
        st.subheader("Analysis Controls")

        # File source selection
        source_tab1, source_tab2, source_tab3 = st.tabs(["Upload File", "Remote Fetch", "Example"])

        with source_tab1:
            # File uploader
            uploaded_file = st.file_uploader("Choose a log file",
                                            type=["txt", "log", "csv", "json", "xml", "gz", "bz2", "zip"])
            use_example = False
            remote_file_path = None

        with source_tab2:
            # Import the remote UI module
            from remote_ui import show_remote_fetch_ui

            # Show the remote fetch UI
            remote_file_path = show_remote_fetch_ui()

            # If a file was fetched, use it
            if remote_file_path:
                uploaded_file = None
                use_example = False
                st.session_state.remote_file_path = remote_file_path

        with source_tab3:
            # Example file option
            use_example = st.checkbox("Use example file", value=not uploaded_file and not remote_file_path)
            if use_example:
                uploaded_file = None
                remote_file_path = None

        # Get all log types from config
        from config import LOG_TYPES
        log_type_options = list(LOG_TYPES.keys()) + ["auto-detect"]

        # Log type selection
        log_type = st.selectbox(
            "Log Type",
            options=log_type_options,
            index=log_type_options.index(st.session_state.log_type) if st.session_state.log_type in log_type_options else log_type_options.index("auto-detect")
        )

        # Time period selection
        time_period = st.selectbox(
            "Time Period",
            options=["Last Hour", "Last Day", "Last Week", "Last Month", "All Time"],
            index=4  # Default to "All Time"
        )

        # Chart type selection
        chart_type = st.selectbox(
            "Chart Type",
            options=["bar", "pie", "line", "area"],
            index=0 if st.session_state.chart_type == "bar" else
                  1 if st.session_state.chart_type == "pie" else
                  2 if st.session_state.chart_type == "line" else 3
        )

        # Apply button
        apply_button = st.button("Apply Settings")

        if apply_button:
            st.session_state.log_type = "auto-detect" if log_type == "auto-detect" else log_type
            st.session_state.time_period = time_period
            st.session_state.chart_type = chart_type

    # Main content area
    if uploaded_file or use_example or remote_file_path:
        with st.spinner("Processing log file..."):
            # Parse the log file
            if uploaded_file:
                # Detect file format
                file_format = uploaded_file.name.split('.')[-1].lower() if '.' in uploaded_file.name else 'unknown'
                st.session_state.file_format = file_format

                # Create a status indicator for file format
                format_indicator = st.empty()
                format_indicator.info(f"File Format: {file_format.upper()}")

                # Parse the file
                log_parser = LogParser(log_type if log_type != "auto-detect" else None)
                df = log_parser.parse_uploaded_file(uploaded_file)
                st.session_state.log_type = log_parser.log_type

            elif remote_file_path:
                # Detect file format
                file_format = remote_file_path.split('.')[-1].lower() if '.' in remote_file_path else 'unknown'
                st.session_state.file_format = file_format

                # Create a status indicator for file format
                format_indicator = st.empty()
                format_indicator.info(f"File Format: {file_format.upper()} (Remote)")

                # Parse the file
                log_parser = LogParser(log_type if log_type != "auto-detect" else None)
                df = log_parser.parse_file(remote_file_path)
                st.session_state.log_type = log_parser.log_type

            elif use_example:
                # Detect file format
                file_format = EXAMPLE_LOG_FILE.split('.')[-1].lower() if '.' in EXAMPLE_LOG_FILE else 'unknown'
                st.session_state.file_format = file_format

                # Create a status indicator for file format
                format_indicator = st.empty()
                format_indicator.info(f"File Format: {file_format.upper()} (Example)")

                # Parse the file
                log_parser = LogParser(log_type if log_type != "auto-detect" else None)
                df = log_parser.parse_file(EXAMPLE_LOG_FILE)
                st.session_state.log_type = log_parser.log_type

            # Optimize memory usage
            from utils import optimize_dataframe, get_dataframe_memory_usage

            # Show memory usage before optimization
            original_memory = get_dataframe_memory_usage(df)

            # Optimize the DataFrame
            df_optimized = optimize_dataframe(df)

            # Show memory usage after optimization
            optimized_memory = get_dataframe_memory_usage(df_optimized)

            # Display memory savings in the sidebar
            with st.sidebar:
                st.write("### Memory Optimization")
                st.write(f"Original size: {original_memory}")
                st.write(f"Optimized size: {optimized_memory}")

                # Calculate percentage saved
                original_bytes = df.memory_usage(deep=True).sum()
                optimized_bytes = df_optimized.memory_usage(deep=True).sum()
                if original_bytes > 0:
                    percent_saved = (1 - optimized_bytes / original_bytes) * 100
                    st.write(f"Memory saved: {percent_saved:.1f}%")

            # Store the optimized data in session state
            st.session_state.log_data = df_optimized

        # Display the data and charts
        if st.session_state.log_data is not None and not st.session_state.log_data.empty:
            display_data_and_charts(st.session_state.log_data, st.session_state.log_type, st.session_state.time_period, st.session_state.chart_type)
        else:
            st.warning("No valid data found in the log file.")
    else:
        st.info("Please upload a log file, fetch a remote log, or use the example file.")

def display_data_and_charts(df: pd.DataFrame, log_type: str, time_period: str, chart_type: str):
    """Display the data and charts for the selected log type."""
    # Get the data for the selected time period
    time_periods = get_time_periods(df, 'raw_timestamp' if 'raw_timestamp' in df.columns else 'timestamp')
    period_df = time_periods.get(time_period, df)

    # Display basic stats
    st.subheader("Log Summary")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Logs", len(period_df))

    with col2:
        if log_type == "browsing":
            unique_users = period_df['username'].nunique()
            st.metric("Unique Users", unique_users)
        elif log_type == "virus":
            unique_viruses = period_df['virus_name'].nunique() if 'virus_name' in period_df.columns else 0
            st.metric("Unique Viruses", unique_viruses)
        elif log_type == "mail":
            unique_senders = period_df['sender'].nunique() if 'sender' in period_df.columns else 0
            st.metric("Unique Senders", unique_senders)

    with col3:
        if log_type == "browsing":
            avg_bandwidth = period_df['bandwidth'].mean() if 'bandwidth' in period_df.columns else 0
            st.metric("Avg Bandwidth", f"{avg_bandwidth:.2f}")
        elif log_type == "virus":
            high_severity = period_df[period_df['severity'] == 'high'].shape[0] if 'severity' in period_df.columns else 0
            st.metric("High Severity", high_severity)
        elif log_type == "mail":
            avg_size = period_df['size'].mean() if 'size' in period_df.columns else 0
            st.metric("Avg Mail Size", f"{avg_size:.2f}")

    with col4:
        if log_type == "browsing":
            error_count = period_df[period_df['status_code'] >= 400].shape[0] if 'status_code' in period_df.columns else 0
            st.metric("Error Responses", error_count)
        elif log_type == "virus":
            quarantined = period_df[period_df['action_taken'] == 'quarantined'].shape[0] if 'action_taken' in period_df.columns else 0
            st.metric("Quarantined", quarantined)
        elif log_type == "mail":
            spam_count = period_df[period_df['spam_score'] > 0.5].shape[0] if 'spam_score' in period_df.columns else 0
            st.metric("Spam Detected", spam_count)

    # Display the data table with filters
    st.subheader("Log Data")

    # Add search/filter functionality
    search_term = st.text_input("Search in logs", "")

    # Filter the data based on the search term
    if search_term:
        filtered_df = period_df[period_df.astype(str).apply(lambda row: row.str.contains(search_term, case=False).any(), axis=1)]
    else:
        filtered_df = period_df

    # Display the filtered data
    st.dataframe(filtered_df)

    # Add download button for the data
    st.markdown(create_download_link(filtered_df, f"{log_type}_logs.csv"), unsafe_allow_html=True)

    # Display charts based on log type
    st.subheader("Visualizations")

    if log_type == "browsing":
        display_browsing_charts(filtered_df, chart_type)
    elif log_type == "virus":
        display_virus_charts(filtered_df, chart_type)
    elif log_type == "mail":
        display_mail_charts(filtered_df, chart_type)
    elif log_type == "firewall":
        display_firewall_charts(filtered_df, chart_type)
    elif log_type == "auth":
        display_auth_charts(filtered_df, chart_type)
    else:
        st.warning(f"No specific visualizations available for {log_type} log type. Using generic charts.")
        display_generic_charts(filtered_df, chart_type)

def display_browsing_charts(df: pd.DataFrame, chart_type: str):
    """Display charts for browsing logs."""
    # Create tabs for different chart categories
    tab1, tab2, tab3, tab4 = st.tabs(["User Activity", "Status Codes", "Categories", "Devices"])

    with tab1:
        st.write("### User Activity Analysis")

        # User activity by IP address
        st.write("#### IP Address Distribution")
        ip_count = df["ip_address"].value_counts().reset_index()
        ip_count.columns = ["IP Address", "Count"]

        if chart_type == "bar":
            chart = alt.Chart(ip_count).mark_bar().encode(
                x=alt.X('IP Address:N', sort='-y', title="IP Address"),
                y=alt.Y('Count:Q', title="Number of Requests"),
                color=alt.Color('IP Address:N', scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
        elif chart_type == "pie":
            chart = alt.Chart(ip_count).mark_arc().encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="IP Address", type="nominal", scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
        else:  # Default to bar for other chart types
            chart = alt.Chart(ip_count).mark_bar().encode(
                x=alt.X('IP Address:N', sort='-y', title="IP Address"),
                y=alt.Y('Count:Q', title="Number of Requests"),
                color=alt.Color('IP Address:N', scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)

        st.altair_chart(chart)

        # User activity by username
        st.write("#### Username Distribution")
        user_count = df["username"].value_counts().reset_index()
        user_count.columns = ["Username", "Count"]

        if chart_type == "bar":
            chart = alt.Chart(user_count).mark_bar().encode(
                x=alt.X('Username:N', sort='-y', title="Username"),
                y=alt.Y('Count:Q', title="Number of Requests"),
                color=alt.Color('Username:N', scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
        elif chart_type == "pie":
            chart = alt.Chart(user_count).mark_arc().encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Username", type="nominal", scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
        else:  # Default to bar for other chart types
            chart = alt.Chart(user_count).mark_bar().encode(
                x=alt.X('Username:N', sort='-y', title="Username"),
                y=alt.Y('Count:Q', title="Number of Requests"),
                color=alt.Color('Username:N', scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)

        st.altair_chart(chart)

    with tab2:
        st.write("### Status Code Analysis")

        # Status code distribution
        status_count = df["status_code"].value_counts().reset_index()
        status_count.columns = ["Status Code", "Count"]

        if chart_type == "bar":
            chart = alt.Chart(status_count).mark_bar().encode(
                x=alt.X('Status Code:N', sort='-y', title="Status Code"),
                y=alt.Y('Count:Q', title="Number of Requests"),
                color=alt.Color('Status Code:N', scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
        elif chart_type == "pie":
            chart = alt.Chart(status_count).mark_arc().encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Status Code", type="nominal", scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
        else:  # Default to bar for other chart types
            chart = alt.Chart(status_count).mark_bar().encode(
                x=alt.X('Status Code:N', sort='-y', title="Status Code"),
                y=alt.Y('Count:Q', title="Number of Requests"),
                color=alt.Color('Status Code:N', scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)

        st.altair_chart(chart)

        # Group status codes by class (2xx, 3xx, 4xx, 5xx)
        df['status_class'] = df['status_code'].apply(lambda x: f"{x // 100}xx")
        status_class_count = df["status_class"].value_counts().reset_index()
        status_class_count.columns = ["Status Class", "Count"]

        if chart_type == "bar":
            chart = alt.Chart(status_class_count).mark_bar().encode(
                x=alt.X('Status Class:N', sort='-y', title="Status Class"),
                y=alt.Y('Count:Q', title="Number of Requests"),
                color=alt.Color('Status Class:N', scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
        elif chart_type == "pie":
            chart = alt.Chart(status_class_count).mark_arc().encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Status Class", type="nominal", scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
        else:  # Default to bar for other chart types
            chart = alt.Chart(status_class_count).mark_bar().encode(
                x=alt.X('Status Class:N', sort='-y', title="Status Class"),
                y=alt.Y('Count:Q', title="Number of Requests"),
                color=alt.Color('Status Class:N', scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)

        st.altair_chart(chart)

    with tab3:
        st.write("### Category Analysis")

        # Category distribution
        category_count = df["category"].value_counts().reset_index()
        category_count.columns = ["Category", "Count"]

        if chart_type == "bar":
            chart = alt.Chart(category_count).mark_bar().encode(
                x=alt.X('Category:N', sort='-y', title="Category"),
                y=alt.Y('Count:Q', title="Number of Requests"),
                color=alt.Color('Category:N', scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
        elif chart_type == "pie":
            chart = alt.Chart(category_count).mark_arc().encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Category", type="nominal", scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
        else:  # Default to bar for other chart types
            chart = alt.Chart(category_count).mark_bar().encode(
                x=alt.X('Category:N', sort='-y', title="Category"),
                y=alt.Y('Count:Q', title="Number of Requests"),
                color=alt.Color('Category:N', scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)

        st.altair_chart(chart)

        # Category by user
        if len(df["username"].unique()) <= 10:  # Only show if there are 10 or fewer users
            category_user = df.groupby(["username", "category"], observed=True).size().reset_index(name="Count")

            chart = alt.Chart(category_user).mark_bar().encode(
                x=alt.X('username:N', title="Username"),
                y=alt.Y('Count:Q', title="Number of Requests"),
                color=alt.Color('category:N', scale=alt.Scale(scheme=COLOR_SCHEME)),
                tooltip=['username', 'category', 'Count']
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)

            st.altair_chart(chart)

    with tab4:
        st.write("### Device Analysis")

        # Extract device type from device_info
        df['device_type'] = df['device_info'].apply(lambda x: x.split('#')[0] if '#' in str(x) else x)
        device_count = df["device_type"].value_counts().reset_index()
        device_count.columns = ["Device Type", "Count"]

        if chart_type == "bar":
            chart = alt.Chart(device_count).mark_bar().encode(
                x=alt.X('Device Type:N', sort='-y', title="Device Type"),
                y=alt.Y('Count:Q', title="Number of Requests"),
                color=alt.Color('Device Type:N', scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
        elif chart_type == "pie":
            chart = alt.Chart(device_count).mark_arc().encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Device Type", type="nominal", scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
        else:  # Default to bar for other chart types
            chart = alt.Chart(device_count).mark_bar().encode(
                x=alt.X('Device Type:N', sort='-y', title="Device Type"),
                y=alt.Y('Count:Q', title="Number of Requests"),
                color=alt.Color('Device Type:N', scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)

        st.altair_chart(chart)

        # Extract browser from device_info
        df['browser'] = df['device_info'].apply(lambda x: x.split('#')[2].split('_')[0] if '#' in str(x) and len(x.split('#')) > 2 else 'Unknown')
        browser_count = df["browser"].value_counts().reset_index()
        browser_count.columns = ["Browser", "Count"]

        if chart_type == "bar":
            chart = alt.Chart(browser_count).mark_bar().encode(
                x=alt.X('Browser:N', sort='-y', title="Browser"),
                y=alt.Y('Count:Q', title="Number of Requests"),
                color=alt.Color('Browser:N', scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
        elif chart_type == "pie":
            chart = alt.Chart(browser_count).mark_arc().encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Browser", type="nominal", scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
        else:  # Default to bar for other chart types
            chart = alt.Chart(browser_count).mark_bar().encode(
                x=alt.X('Browser:N', sort='-y', title="Browser"),
                y=alt.Y('Count:Q', title="Number of Requests"),
                color=alt.Color('Browser:N', scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)

        st.altair_chart(chart)

    # Add a new tab for Site Visit Analysis
    tab5 = st.tabs(["Site Visit Analysis"])[0]
    with tab5:
        st.write("### Site Visit Analysis")

        # Extract domains from URLs
        if 'url' in df.columns:
            from utils import analyze_site_visits

            # Get site visit analysis
            site_analysis = analyze_site_visits(df)

            # Display top domains
            if 'top_domains' in site_analysis:
                st.write("#### Top Visited Domains")
                top_domains_df = pd.DataFrame(list(site_analysis['top_domains'].items()),
                                             columns=['Domain', 'Visits'])

                if chart_type == "bar":
                    chart = alt.Chart(top_domains_df).mark_bar().encode(
                        x=alt.X('Domain:N', sort='-y', title="Domain"),
                        y=alt.Y('Visits:Q', title="Number of Visits"),
                        color=alt.Color('Domain:N', scale=alt.Scale(scheme=COLOR_SCHEME))
                    ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
                elif chart_type == "pie":
                    chart = alt.Chart(top_domains_df).mark_arc().encode(
                        theta=alt.Theta(field="Visits", type="quantitative"),
                        color=alt.Color(field="Domain", type="nominal", scale=alt.Scale(scheme=COLOR_SCHEME))
                    ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
                else:  # Default to bar for other chart types
                    chart = alt.Chart(top_domains_df).mark_bar().encode(
                        x=alt.X('Domain:N', sort='-y', title="Domain"),
                        y=alt.Y('Visits:Q', title="Number of Visits"),
                        color=alt.Color('Domain:N', scale=alt.Scale(scheme=COLOR_SCHEME))
                    ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)

                st.altair_chart(chart)

                # Show the data table
                st.write("#### Top Domains Data")
                st.dataframe(top_domains_df)

            # Display visits by category
            if 'category_visits' in site_analysis:
                st.write("#### Visits by Category")
                category_df = pd.DataFrame(list(site_analysis['category_visits'].items()),
                                          columns=['Category', 'Visits'])

                if chart_type == "bar":
                    chart = alt.Chart(category_df).mark_bar().encode(
                        x=alt.X('Category:N', sort='-y', title="Category"),
                        y=alt.Y('Visits:Q', title="Number of Visits"),
                        color=alt.Color('Category:N', scale=alt.Scale(scheme=COLOR_SCHEME))
                    ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
                elif chart_type == "pie":
                    chart = alt.Chart(category_df).mark_arc().encode(
                        theta=alt.Theta(field="Visits", type="quantitative"),
                        color=alt.Color(field="Category", type="nominal", scale=alt.Scale(scheme=COLOR_SCHEME))
                    ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
                else:  # Default to bar for other chart types
                    chart = alt.Chart(category_df).mark_bar().encode(
                        x=alt.X('Category:N', sort='-y', title="Category"),
                        y=alt.Y('Visits:Q', title="Number of Visits"),
                        color=alt.Color('Category:N', scale=alt.Scale(scheme=COLOR_SCHEME))
                    ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)

                st.altair_chart(chart)

            # Display user visits
            if 'user_visits' in site_analysis:
                st.write("#### User Browsing Patterns")

                # Create a selectbox for users
                users = list(site_analysis['user_visits'].keys())
                selected_user = st.selectbox("Select User", users)

                if selected_user:
                    user_data = site_analysis['user_visits'][selected_user]
                    st.write(f"Total visits: {user_data['total_visits']}")

                    # Show top domains for the selected user
                    st.write(f"#### Top Domains for {selected_user}")
                    user_domains_df = pd.DataFrame(list(user_data['top_domains'].items()),
                                                 columns=['Domain', 'Visits'])

                    if chart_type == "bar":
                        chart = alt.Chart(user_domains_df).mark_bar().encode(
                            x=alt.X('Domain:N', sort='-y', title="Domain"),
                            y=alt.Y('Visits:Q', title="Number of Visits"),
                            color=alt.Color('Domain:N', scale=alt.Scale(scheme=COLOR_SCHEME))
                        ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
                    elif chart_type == "pie":
                        chart = alt.Chart(user_domains_df).mark_arc().encode(
                            theta=alt.Theta(field="Visits", type="quantitative"),
                            color=alt.Color(field="Domain", type="nominal", scale=alt.Scale(scheme=COLOR_SCHEME))
                        ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
                    else:  # Default to bar for other chart types
                        chart = alt.Chart(user_domains_df).mark_bar().encode(
                            x=alt.X('Domain:N', sort='-y', title="Domain"),
                            y=alt.Y('Visits:Q', title="Number of Visits"),
                            color=alt.Color('Domain:N', scale=alt.Scale(scheme=COLOR_SCHEME))
                        ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)

                    st.altair_chart(chart)

def display_virus_charts(df: pd.DataFrame, chart_type: str):
    """Display charts for virus logs."""
    # Placeholder for virus log charts
    st.write("Virus log analysis charts will be displayed here.")

    # Example chart (to be replaced with actual virus log charts)
    if 'virus_name' in df.columns:
        virus_count = df["virus_name"].value_counts().reset_index()
        virus_count.columns = ["Virus Name", "Count"]

        if chart_type == "bar":
            chart = alt.Chart(virus_count).mark_bar().encode(
                x=alt.X('Virus Name:N', sort='-y', title="Virus Name"),
                y=alt.Y('Count:Q', title="Occurrences"),
                color=alt.Color('Virus Name:N', scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
        elif chart_type == "pie":
            chart = alt.Chart(virus_count).mark_arc().encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Virus Name", type="nominal", scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
        else:  # Default to bar for other chart types
            chart = alt.Chart(virus_count).mark_bar().encode(
                x=alt.X('Virus Name:N', sort='-y', title="Virus Name"),
                y=alt.Y('Count:Q', title="Occurrences"),
                color=alt.Color('Virus Name:N', scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)

        st.altair_chart(chart)

def display_mail_charts(df: pd.DataFrame, chart_type: str):
    """Display charts for mail logs."""
    # Placeholder for mail log charts
    st.write("Mail log analysis charts will be displayed here.")

    # Example chart (to be replaced with actual mail log charts)
    if 'sender' in df.columns:
        sender_count = df["sender"].value_counts().reset_index()
        sender_count.columns = ["Sender", "Count"]

        if chart_type == "bar":
            chart = alt.Chart(sender_count).mark_bar().encode(
                x=alt.X('Sender:N', sort='-y', title="Sender"),
                y=alt.Y('Count:Q', title="Number of Emails"),
                color=alt.Color('Sender:N', scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
        elif chart_type == "pie":
            chart = alt.Chart(sender_count).mark_arc().encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Sender", type="nominal", scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
        else:  # Default to bar for other chart types
            chart = alt.Chart(sender_count).mark_bar().encode(
                x=alt.X('Sender:N', sort='-y', title="Sender"),
                y=alt.Y('Count:Q', title="Number of Emails"),
                color=alt.Color('Sender:N', scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)

        st.altair_chart(chart)

# Display functions for additional log types
def display_firewall_charts(df: pd.DataFrame, chart_type: str):
    """Display charts for firewall logs."""
    # Create tabs for different chart categories
    tab1, tab2, tab3 = st.tabs(["Traffic Analysis", "Action Analysis", "Protocol Analysis"])

    with tab1:
        st.write("### Traffic Analysis")

        # Source IP distribution
        if 'src_ip' in df.columns:
            st.write("#### Source IP Distribution")
            src_ip_count = df["src_ip"].value_counts().reset_index()
            src_ip_count.columns = ["Source IP", "Count"]

            if chart_type == "bar":
                chart = alt.Chart(src_ip_count.head(20)).mark_bar().encode(
                    x=alt.X('Source IP:N', sort='-y', title="Source IP"),
                    y=alt.Y('Count:Q', title="Number of Connections"),
                    color=alt.Color('Source IP:N', scale=alt.Scale(scheme=COLOR_SCHEME))
                ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
            elif chart_type == "pie":
                chart = alt.Chart(src_ip_count.head(10)).mark_arc().encode(
                    theta=alt.Theta(field="Count", type="quantitative"),
                    color=alt.Color(field="Source IP", type="nominal", scale=alt.Scale(scheme=COLOR_SCHEME))
                ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
            else:  # Default to bar for other chart types
                chart = alt.Chart(src_ip_count.head(20)).mark_bar().encode(
                    x=alt.X('Source IP:N', sort='-y', title="Source IP"),
                    y=alt.Y('Count:Q', title="Number of Connections"),
                    color=alt.Color('Source IP:N', scale=alt.Scale(scheme=COLOR_SCHEME))
                ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)

            st.altair_chart(chart)

        # Destination IP distribution
        if 'dst_ip' in df.columns:
            st.write("#### Destination IP Distribution")
            dst_ip_count = df["dst_ip"].value_counts().reset_index()
            dst_ip_count.columns = ["Destination IP", "Count"]

            if chart_type == "bar":
                chart = alt.Chart(dst_ip_count.head(20)).mark_bar().encode(
                    x=alt.X('Destination IP:N', sort='-y', title="Destination IP"),
                    y=alt.Y('Count:Q', title="Number of Connections"),
                    color=alt.Color('Destination IP:N', scale=alt.Scale(scheme=COLOR_SCHEME))
                ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
            elif chart_type == "pie":
                chart = alt.Chart(dst_ip_count.head(10)).mark_arc().encode(
                    theta=alt.Theta(field="Count", type="quantitative"),
                    color=alt.Color(field="Destination IP", type="nominal", scale=alt.Scale(scheme=COLOR_SCHEME))
                ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
            else:  # Default to bar for other chart types
                chart = alt.Chart(dst_ip_count.head(20)).mark_bar().encode(
                    x=alt.X('Destination IP:N', sort='-y', title="Destination IP"),
                    y=alt.Y('Count:Q', title="Number of Connections"),
                    color=alt.Color('Destination IP:N', scale=alt.Scale(scheme=COLOR_SCHEME))
                ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)

            st.altair_chart(chart)

    with tab2:
        st.write("### Action Analysis")

        # Action distribution
        if 'action' in df.columns:
            st.write("#### Action Distribution")
            action_count = df["action"].value_counts().reset_index()
            action_count.columns = ["Action", "Count"]

            if chart_type == "bar":
                chart = alt.Chart(action_count).mark_bar().encode(
                    x=alt.X('Action:N', sort='-y', title="Action"),
                    y=alt.Y('Count:Q', title="Number of Events"),
                    color=alt.Color('Action:N', scale=alt.Scale(scheme=COLOR_SCHEME))
                ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
            elif chart_type == "pie":
                chart = alt.Chart(action_count).mark_arc().encode(
                    theta=alt.Theta(field="Count", type="quantitative"),
                    color=alt.Color(field="Action", type="nominal", scale=alt.Scale(scheme=COLOR_SCHEME))
                ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
            else:  # Default to bar for other chart types
                chart = alt.Chart(action_count).mark_bar().encode(
                    x=alt.X('Action:N', sort='-y', title="Action"),
                    y=alt.Y('Count:Q', title="Number of Events"),
                    color=alt.Color('Action:N', scale=alt.Scale(scheme=COLOR_SCHEME))
                ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)

            st.altair_chart(chart)

    with tab3:
        st.write("### Protocol Analysis")

        # Protocol distribution
        if 'protocol' in df.columns:
            st.write("#### Protocol Distribution")
            protocol_count = df["protocol"].value_counts().reset_index()
            protocol_count.columns = ["Protocol", "Count"]

            if chart_type == "bar":
                chart = alt.Chart(protocol_count).mark_bar().encode(
                    x=alt.X('Protocol:N', sort='-y', title="Protocol"),
                    y=alt.Y('Count:Q', title="Number of Connections"),
                    color=alt.Color('Protocol:N', scale=alt.Scale(scheme=COLOR_SCHEME))
                ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
            elif chart_type == "pie":
                chart = alt.Chart(protocol_count).mark_arc().encode(
                    theta=alt.Theta(field="Count", type="quantitative"),
                    color=alt.Color(field="Protocol", type="nominal", scale=alt.Scale(scheme=COLOR_SCHEME))
                ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
            else:  # Default to bar for other chart types
                chart = alt.Chart(protocol_count).mark_bar().encode(
                    x=alt.X('Protocol:N', sort='-y', title="Protocol"),
                    y=alt.Y('Count:Q', title="Number of Connections"),
                    color=alt.Color('Protocol:N', scale=alt.Scale(scheme=COLOR_SCHEME))
                ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)

            st.altair_chart(chart)

def display_auth_charts(df: pd.DataFrame, chart_type: str):
    """Display charts for authentication logs."""
    # Create tabs for different chart categories
    tab1, tab2, tab3 = st.tabs(["User Activity", "Authentication Status", "Service Analysis"])

    with tab1:
        st.write("### User Activity")

        # Username distribution
        if 'username' in df.columns:
            st.write("#### Username Distribution")
            username_count = df["username"].value_counts().reset_index()
            username_count.columns = ["Username", "Count"]

            if chart_type == "bar":
                chart = alt.Chart(username_count.head(20)).mark_bar().encode(
                    x=alt.X('Username:N', sort='-y', title="Username"),
                    y=alt.Y('Count:Q', title="Number of Events"),
                    color=alt.Color('Username:N', scale=alt.Scale(scheme=COLOR_SCHEME))
                ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
            elif chart_type == "pie":
                chart = alt.Chart(username_count.head(10)).mark_arc().encode(
                    theta=alt.Theta(field="Count", type="quantitative"),
                    color=alt.Color(field="Username", type="nominal", scale=alt.Scale(scheme=COLOR_SCHEME))
                ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
            else:  # Default to bar for other chart types
                chart = alt.Chart(username_count.head(20)).mark_bar().encode(
                    x=alt.X('Username:N', sort='-y', title="Username"),
                    y=alt.Y('Count:Q', title="Number of Events"),
                    color=alt.Color('Username:N', scale=alt.Scale(scheme=COLOR_SCHEME))
                ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)

            st.altair_chart(chart)

        # Source IP distribution
        if 'source_ip' in df.columns:
            st.write("#### Source IP Distribution")
            source_ip_count = df["source_ip"].value_counts().reset_index()
            source_ip_count.columns = ["Source IP", "Count"]

            if chart_type == "bar":
                chart = alt.Chart(source_ip_count.head(20)).mark_bar().encode(
                    x=alt.X('Source IP:N', sort='-y', title="Source IP"),
                    y=alt.Y('Count:Q', title="Number of Events"),
                    color=alt.Color('Source IP:N', scale=alt.Scale(scheme=COLOR_SCHEME))
                ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
            elif chart_type == "pie":
                chart = alt.Chart(source_ip_count.head(10)).mark_arc().encode(
                    theta=alt.Theta(field="Count", type="quantitative"),
                    color=alt.Color(field="Source IP", type="nominal", scale=alt.Scale(scheme=COLOR_SCHEME))
                ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
            else:  # Default to bar for other chart types
                chart = alt.Chart(source_ip_count.head(20)).mark_bar().encode(
                    x=alt.X('Source IP:N', sort='-y', title="Source IP"),
                    y=alt.Y('Count:Q', title="Number of Events"),
                    color=alt.Color('Source IP:N', scale=alt.Scale(scheme=COLOR_SCHEME))
                ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)

            st.altair_chart(chart)

    with tab2:
        st.write("### Authentication Status")

        # Status distribution
        if 'status' in df.columns:
            st.write("#### Authentication Status Distribution")
            status_count = df["status"].value_counts().reset_index()
            status_count.columns = ["Status", "Count"]

            if chart_type == "bar":
                chart = alt.Chart(status_count).mark_bar().encode(
                    x=alt.X('Status:N', sort='-y', title="Status"),
                    y=alt.Y('Count:Q', title="Number of Events"),
                    color=alt.Color('Status:N', scale=alt.Scale(scheme=COLOR_SCHEME))
                ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
            elif chart_type == "pie":
                chart = alt.Chart(status_count).mark_arc().encode(
                    theta=alt.Theta(field="Count", type="quantitative"),
                    color=alt.Color(field="Status", type="nominal", scale=alt.Scale(scheme=COLOR_SCHEME))
                ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
            else:  # Default to bar for other chart types
                chart = alt.Chart(status_count).mark_bar().encode(
                    x=alt.X('Status:N', sort='-y', title="Status"),
                    y=alt.Y('Count:Q', title="Number of Events"),
                    color=alt.Color('Status:N', scale=alt.Scale(scheme=COLOR_SCHEME))
                ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)

            st.altair_chart(chart)

    with tab3:
        st.write("### Service Analysis")

        # Service distribution
        if 'service' in df.columns:
            st.write("#### Service Distribution")
            service_count = df["service"].value_counts().reset_index()
            service_count.columns = ["Service", "Count"]

            if chart_type == "bar":
                chart = alt.Chart(service_count).mark_bar().encode(
                    x=alt.X('Service:N', sort='-y', title="Service"),
                    y=alt.Y('Count:Q', title="Number of Events"),
                    color=alt.Color('Service:N', scale=alt.Scale(scheme=COLOR_SCHEME))
                ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
            elif chart_type == "pie":
                chart = alt.Chart(service_count).mark_arc().encode(
                    theta=alt.Theta(field="Count", type="quantitative"),
                    color=alt.Color(field="Service", type="nominal", scale=alt.Scale(scheme=COLOR_SCHEME))
                ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
            else:  # Default to bar for other chart types
                chart = alt.Chart(service_count).mark_bar().encode(
                    x=alt.X('Service:N', sort='-y', title="Service"),
                    y=alt.Y('Count:Q', title="Number of Events"),
                    color=alt.Color('Service:N', scale=alt.Scale(scheme=COLOR_SCHEME))
                ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)

            st.altair_chart(chart)

def display_generic_charts(df: pd.DataFrame, chart_type: str):
    """Display generic charts for any log type."""
    st.write("### Generic Log Analysis")

    # Display column distributions for the first 5 non-timestamp columns
    columns_to_analyze = [col for col in df.columns if col not in ['timestamp', 'datetime', 'raw_timestamp']][:5]

    for col in columns_to_analyze:
        st.write(f"#### {col} Distribution")

        # Skip if column has too many unique values
        if df[col].nunique() > 50:
            st.write(f"Too many unique values ({df[col].nunique()}) to display a meaningful chart.")
            continue

        # Get value counts
        value_counts = df[col].value_counts().reset_index()
        value_counts.columns = [col, "Count"]

        # Create chart
        if chart_type == "bar":
            chart = alt.Chart(value_counts.head(20)).mark_bar().encode(
                x=alt.X(f'{col}:N', sort='-y', title=col),
                y=alt.Y('Count:Q', title="Count"),
                color=alt.Color(f'{col}:N', scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
        elif chart_type == "pie":
            chart = alt.Chart(value_counts.head(10)).mark_arc().encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field=col, type="nominal", scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)
        else:  # Default to bar for other chart types
            chart = alt.Chart(value_counts.head(20)).mark_bar().encode(
                x=alt.X(f'{col}:N', sort='-y', title=col),
                y=alt.Y('Count:Q', title="Count"),
                color=alt.Color(f'{col}:N', scale=alt.Scale(scheme=COLOR_SCHEME))
            ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)

        st.altair_chart(chart)

    # Time-based analysis if datetime column exists
    if 'datetime' in df.columns:
        st.write("#### Time-based Analysis")

        # Add hour and day columns
        df['hour'] = df['datetime'].dt.hour
        df['day'] = df['datetime'].dt.day_name()

        # Events by hour
        hour_counts = df['hour'].value_counts().reset_index()
        hour_counts.columns = ['Hour', 'Count']
        hour_counts = hour_counts.sort_values('Hour')

        hour_chart = alt.Chart(hour_counts).mark_line().encode(
            x=alt.X('Hour:O', title="Hour of Day"),
            y=alt.Y('Count:Q', title="Number of Events"),
            tooltip=['Hour', 'Count']
        ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)

        st.altair_chart(hour_chart)

        # Events by day
        day_counts = df['day'].value_counts().reset_index()
        day_counts.columns = ['Day', 'Count']

        # Define day order
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_counts['Day'] = pd.Categorical(day_counts['Day'], categories=days, ordered=True)
        day_counts = day_counts.sort_values('Day')

        day_chart = alt.Chart(day_counts).mark_bar().encode(
            x=alt.X('Day:O', title="Day of Week", sort=days),
            y=alt.Y('Count:Q', title="Number of Events"),
            color=alt.Color('Day:N', scale=alt.Scale(scheme=COLOR_SCHEME)),
            tooltip=['Day', 'Count']
        ).properties(width=CHART_WIDTH, height=CHART_HEIGHT)

        st.altair_chart(day_chart)

# Run the Streamlit app
if __name__ == "__main__":
    show()
