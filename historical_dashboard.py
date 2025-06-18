"""
Historical dashboard module for the Log Analyzer application.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
from typing import Dict, List, Optional, Union, Any, Tuple

from config import CHART_WIDTH, CHART_HEIGHT, COLOR_SCHEME, DEFAULT_LOG_TYPE
from utils import get_time_periods, create_download_link

def show_historical_dashboard():
    """Display the historical dashboard for log analysis."""
    st.title("Historical Log Analysis Dashboard")

    # Check if user is logged in
    if not st.session_state.logged_in:
        st.warning("Please log in to view the historical dashboard.")
        return

    # Check if log data is available
    if 'log_data' not in st.session_state or st.session_state.log_data is None or st.session_state.log_data.empty:
        st.warning("No log data available. Please analyze logs in the Charts section first.")
        return

    # Get the log data
    df = st.session_state.log_data
    log_type = st.session_state.log_type if 'log_type' in st.session_state else DEFAULT_LOG_TYPE

    # Ensure we have datetime information
    if 'datetime' not in df.columns and 'timestamp' in df.columns:
        if pd.api.types.is_numeric_dtype(df['timestamp']):
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        else:
            df['datetime'] = pd.to_datetime(df['timestamp'])

    if 'datetime' not in df.columns:
        st.error("Datetime information not available for historical analysis.")
        return

    # Add date components
    df['date'] = df['datetime'].dt.date
    df['year'] = df['datetime'].dt.year
    df['month'] = df['datetime'].dt.month
    df['day'] = df['datetime'].dt.day
    df['hour'] = df['datetime'].dt.hour
    df['day_of_week'] = df['datetime'].dt.day_name()
    df['week_of_year'] = df['datetime'].dt.isocalendar().week

    # Sidebar for controls
    with st.sidebar:
        st.subheader("Dashboard Controls")

        # Time range selection
        st.write("### Time Range")
        time_range = st.selectbox(
            "Select Time Range",
            options=["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last 90 Days", "Last Year", "All Time", "Custom Range"],
            index=2  # Default to Last 30 Days
        )

        # Handle custom date range
        if time_range == "Custom Range":
            min_date = df['datetime'].min().date()
            max_date = df['datetime'].max().date()

            start_date = st.date_input("Start Date", min_date)
            end_date = st.date_input("End Date", max_date)

            # Convert to datetime for filtering
            start_datetime = pd.to_datetime(start_date)
            end_datetime = pd.to_datetime(end_date) + timedelta(days=1) - timedelta(seconds=1)  # End of the day
        else:
            # Calculate date range based on selection
            end_datetime = df['datetime'].max()

            if time_range == "Last 24 Hours":
                start_datetime = end_datetime - timedelta(days=1)
            elif time_range == "Last 7 Days":
                start_datetime = end_datetime - timedelta(days=7)
            elif time_range == "Last 30 Days":
                start_datetime = end_datetime - timedelta(days=30)
            elif time_range == "Last 90 Days":
                start_datetime = end_datetime - timedelta(days=90)
            elif time_range == "Last Year":
                start_datetime = end_datetime - timedelta(days=365)
            else:  # All Time
                start_datetime = df['datetime'].min()

        # Filter data by date range
        filtered_df = df[(df['datetime'] >= start_datetime) & (df['datetime'] <= end_datetime)]

        # Time granularity for charts
        st.write("### Time Granularity")
        time_granularity = st.selectbox(
            "Select Time Granularity",
            options=["Hourly", "Daily", "Weekly", "Monthly"],
            index=1  # Default to Daily
        )

        # Additional filters based on log type
        st.write("### Additional Filters")

        if log_type == "browsing":
            # Filter by category
            if 'category' in filtered_df.columns:
                categories = filtered_df['category'].unique()
                selected_categories = st.multiselect("Select Categories", categories)
                if selected_categories:
                    filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]

        elif log_type == "virus":
            # Filter by severity
            if 'severity' in filtered_df.columns:
                severities = filtered_df['severity'].unique()
                selected_severities = st.multiselect("Select Severities", severities)
                if selected_severities:
                    filtered_df = filtered_df[filtered_df['severity'].isin(selected_severities)]

        elif log_type == "mail":
            # Filter by spam threshold
            if 'spam_score' in filtered_df.columns:
                spam_threshold = st.slider("Minimum Spam Score", 0.0, 1.0, 0.0, 0.1)
                if spam_threshold > 0:
                    filtered_df = filtered_df[filtered_df['spam_score'] >= spam_threshold]

    # Display summary metrics
    st.subheader("Summary Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Records", len(filtered_df))

    with col2:
        if log_type == "browsing":
            if 'username' in filtered_df.columns:
                unique_users = filtered_df['username'].nunique()
                st.metric("Unique Users", unique_users)
        elif log_type == "virus":
            if 'virus_name' in filtered_df.columns:
                unique_viruses = filtered_df['virus_name'].nunique()
                st.metric("Unique Viruses", unique_viruses)
        elif log_type == "mail":
            if 'sender' in filtered_df.columns:
                unique_senders = filtered_df['sender'].nunique()
                st.metric("Unique Senders", unique_senders)

    with col3:
        if log_type == "browsing":
            if 'status_code' in filtered_df.columns:
                error_count = filtered_df[filtered_df['status_code'] >= 400].shape[0]
                error_pct = (error_count / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0
                st.metric("Error Rate", f"{error_pct:.2f}%")
        elif log_type == "virus":
            if 'severity' in filtered_df.columns:
                high_severity = filtered_df[filtered_df['severity'] == 'high'].shape[0]
                st.metric("High Severity", high_severity)
        elif log_type == "mail":
            if 'spam_score' in filtered_df.columns:
                spam_count = filtered_df[filtered_df['spam_score'] > 0.5].shape[0]
                spam_pct = (spam_count / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0
                st.metric("Spam Rate", f"{spam_pct:.2f}%")

    with col4:
        # Calculate average daily activity
        if len(filtered_df) > 0:
            days_span = (filtered_df['datetime'].max() - filtered_df['datetime'].min()).days + 1
            daily_avg = len(filtered_df) / max(days_span, 1)
            st.metric("Daily Average", f"{daily_avg:.2f}")

    # Create time series based on selected granularity
    st.subheader("Time Series Analysis")

    if time_granularity == "Hourly":
        time_series = filtered_df.groupby(['date', 'hour']).size().reset_index(name='count')
        time_series['datetime'] = pd.to_datetime(time_series['date']) + pd.to_timedelta(time_series['hour'], unit='h')
        x_col = 'datetime'
        x_title = 'Hour'
    elif time_granularity == "Daily":
        time_series = filtered_df.groupby('date').size().reset_index(name='count')
        time_series['datetime'] = pd.to_datetime(time_series['date'])
        x_col = 'datetime'
        x_title = 'Date'
    elif time_granularity == "Weekly":
        time_series = filtered_df.groupby(['year', 'week_of_year']).size().reset_index(name='count')
        # Create a datetime for the first day of each week
        time_series['datetime'] = time_series.apply(
            lambda row: datetime.strptime(f"{int(row['year'])}-{int(row['week_of_year'])}-1", "%Y-%W-%w"), axis=1
        )
        x_col = 'datetime'
        x_title = 'Week'
    else:  # Monthly
        time_series = filtered_df.groupby(['year', 'month']).size().reset_index(name='count')
        time_series['datetime'] = time_series.apply(
            lambda row: datetime(int(row['year']), int(row['month']), 1), axis=1
        )
        x_col = 'datetime'
        x_title = 'Month'

    # Create time series chart
    fig = px.line(time_series, x=x_col, y='count',
                  title=f'{time_granularity} Activity',
                  labels={x_col: x_title, 'count': 'Number of Records'},
                  markers=True)

    st.plotly_chart(fig, use_container_width=True)

    # Create heatmap for day of week vs hour
    st.subheader("Activity Patterns")

    # Day of week vs hour heatmap
    try:
        day_hour_pivot = filtered_df.groupby(['day_of_week', 'hour'], observed=True).size().unstack(fill_value=0)

        # Reorder days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_hour_pivot = day_hour_pivot.reindex(day_order)

        # Create a complete DataFrame with all hours (0-23)
        all_hours = list(range(24))

        # Create a new DataFrame with the correct structure
        new_pivot = pd.DataFrame(index=day_order, columns=all_hours, data=0)

        # Fill in the values from the original pivot table
        for day in day_hour_pivot.index:
            for hour in day_hour_pivot.columns:
                if day in new_pivot.index and hour in new_pivot.columns:
                    new_pivot.at[day, hour] = day_hour_pivot.at[day, hour]

        # Use the new pivot table for the heatmap
        fig = px.imshow(new_pivot,
                        labels=dict(x="Hour of Day", y="Day of Week", color="Activity Count"),
                        x=all_hours,  # Use the complete list of hours
                        y=day_order,
                        title="Activity Heatmap by Day and Hour",
                        color_continuous_scale="Viridis")
    except ValueError:
        # Fallback to a simpler visualization if the heatmap fails
        st.warning("Could not create heatmap due to data mismatch. Showing alternative visualization.")

        # Create a bar chart of activity by hour instead
        hour_counts = filtered_df['hour'].value_counts().sort_index().reset_index()
        hour_counts.columns = ['Hour', 'Count']

        fig = px.bar(hour_counts, x='Hour', y='Count',
                    title="Activity by Hour of Day",
                    labels={'Hour': 'Hour of Day', 'Count': 'Number of Events'})

    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Create log type specific visualizations
    if log_type == "browsing":
        display_browsing_historical(filtered_df)
    elif log_type == "virus":
        display_virus_historical(filtered_df)
    elif log_type == "mail":
        display_mail_historical(filtered_df)

    # Export options
    st.subheader("Export Options")

    # Create download link for filtered data
    st.markdown(create_download_link(filtered_df, f"{log_type}_historical_data.csv"), unsafe_allow_html=True)

    # Option to save dashboard as report
    if st.button("Save Dashboard as Report"):
        if 'reports' not in st.session_state:
            st.session_state.reports = []

        report = {
            "title": f"Historical {log_type.capitalize()} Log Analysis",
            "description": f"Analysis of {log_type} logs from {start_datetime.date()} to {end_datetime.date()}",
            "created_at": datetime.now(),
            "log_type": log_type,
            "record_count": len(filtered_df),
            "time_range": time_range if time_range != "Custom Range" else f"Custom: {start_datetime.date()} to {end_datetime.date()}"
        }

        st.session_state.reports.append(report)
        st.success("Dashboard saved as a report!")

def display_browsing_historical(df: pd.DataFrame):
    """
    Display historical visualizations for browsing logs.

    Args:
        df: DataFrame containing browsing log data
    """
    st.subheader("Browsing Patterns")

    # Create tabs for different visualizations
    tab1, tab2 = st.tabs(["Content Analysis", "User Behavior"])

    with tab1:
        if 'category' in df.columns:
            # Category trends over time
            df['month_year'] = df['datetime'].dt.strftime('%Y-%m')

            # Get top 5 categories
            top_categories = df['category'].value_counts().nlargest(5).index.tolist()

            # Filter for top categories
            category_df = df[df['category'].isin(top_categories)]

            # Group by month and category
            category_time = category_df.groupby(['month_year', 'category'], observed=True).size().reset_index(name='count')

            fig = px.line(category_time, x='month_year', y='count', color='category',
                          title='Top Categories Over Time',
                          labels={'month_year': 'Month', 'count': 'Number of Requests', 'category': 'Category'})

            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

            # Category distribution pie chart
            category_counts = df['category'].value_counts().reset_index()
            category_counts.columns = ['category', 'count']

            fig = px.pie(category_counts.head(10), names='category', values='count',
                         title='Top 10 Categories Distribution')

            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

        if 'status_code' in df.columns:
            # Status code trends
            df['status_class'] = df['status_code'].apply(lambda x: f"{x // 100}xx")

            # Group by month and status class
            status_time = df.groupby(['month_year', 'status_class'], observed=True).size().reset_index(name='count')

            fig = px.line(status_time, x='month_year', y='count', color='status_class',
                          title='HTTP Status Codes Over Time',
                          labels={'month_year': 'Month', 'count': 'Number of Requests', 'status_class': 'Status Class'},
                          color_discrete_map={'2xx': 'green', '3xx': 'blue', '4xx': 'orange', '5xx': 'red'})

            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        if 'username' in df.columns:
            # User activity over time
            user_time = df.groupby(['date', 'username'], observed=True).size().reset_index(name='count')

            # Get top 5 users
            top_users = df['username'].value_counts().nlargest(5).index.tolist()

            # Filter for top users
            user_time_filtered = user_time[user_time['username'].isin(top_users)]

            fig = px.line(user_time_filtered, x='date', y='count', color='username',
                          title='Top Users Activity Over Time',
                          labels={'date': 'Date', 'count': 'Number of Requests', 'username': 'Username'})

            st.plotly_chart(fig, use_container_width=True)

            # User activity distribution
            user_counts = df['username'].value_counts().reset_index()
            user_counts.columns = ['username', 'count']

            fig = px.bar(user_counts.head(10), x='username', y='count',
                         title='Top 10 Users by Activity',
                         labels={'username': 'Username', 'count': 'Number of Requests'},
                         color='count', color_continuous_scale='Viridis')

            st.plotly_chart(fig, use_container_width=True)

        if 'device_info' in df.columns:
            # Device type distribution
            df['device_type'] = df['device_info'].apply(lambda x: x.split('#')[0] if '#' in str(x) else x)

            device_counts = df['device_type'].value_counts().reset_index()
            device_counts.columns = ['device_type', 'count']

            fig = px.pie(device_counts, names='device_type', values='count',
                         title='Device Type Distribution')

            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

def display_virus_historical(df: pd.DataFrame):
    """
    Display historical visualizations for virus logs.

    Args:
        df: DataFrame containing virus log data
    """
    st.subheader("Virus Detection Patterns")

    # Create tabs for different visualizations
    tab1, tab2 = st.tabs(["Virus Trends", "Severity Analysis"])

    with tab1:
        if 'virus_name' in df.columns:
            # Virus detection over time
            df['month_year'] = df['datetime'].dt.strftime('%Y-%m')

            # Get top 5 viruses
            top_viruses = df['virus_name'].value_counts().nlargest(5).index.tolist()

            # Filter for top viruses
            virus_df = df[df['virus_name'].isin(top_viruses)]

            # Group by month and virus
            virus_time = virus_df.groupby(['month_year', 'virus_name'], observed=True).size().reset_index(name='count')

            fig = px.line(virus_time, x='month_year', y='count', color='virus_name',
                          title='Top Viruses Over Time',
                          labels={'month_year': 'Month', 'count': 'Number of Detections', 'virus_name': 'Virus Name'})

            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

            # Virus distribution pie chart
            virus_counts = df['virus_name'].value_counts().reset_index()
            virus_counts.columns = ['virus_name', 'count']

            fig = px.pie(virus_counts.head(10), names='virus_name', values='count',
                         title='Top 10 Viruses Distribution')

            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        if 'severity' in df.columns:
            # Severity trends over time
            severity_time = df.groupby(['month_year', 'severity'], observed=True).size().reset_index(name='count')

            fig = px.line(severity_time, x='month_year', y='count', color='severity',
                          title='Severity Levels Over Time',
                          labels={'month_year': 'Month', 'count': 'Number of Detections', 'severity': 'Severity Level'})

            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

            # Severity distribution
            severity_counts = df['severity'].value_counts().reset_index()
            severity_counts.columns = ['severity', 'count']

            # Create a custom color map for severity
            severity_colors = {'high': 'red', 'medium': 'orange', 'low': 'yellow', 'info': 'blue'}

            fig = px.pie(severity_counts, names='severity', values='count',
                         title='Severity Distribution',
                         color='severity',
                         color_discrete_map=severity_colors)

            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

            # Severity by action taken
            if 'action_taken' in df.columns:
                action_severity = df.groupby(['severity', 'action_taken'], observed=True).size().reset_index(name='count')

                fig = px.bar(action_severity, x='severity', y='count', color='action_taken',
                             title='Actions Taken by Severity Level',
                             labels={'severity': 'Severity Level', 'count': 'Number of Detections', 'action_taken': 'Action Taken'},
                             barmode='group')

                st.plotly_chart(fig, use_container_width=True)

def display_mail_historical(df: pd.DataFrame):
    """
    Display historical visualizations for mail logs.

    Args:
        df: DataFrame containing mail log data
    """
    st.subheader("Email Traffic Patterns")

    # Create tabs for different visualizations
    tab1, tab2 = st.tabs(["Email Volume", "Spam Analysis"])

    with tab1:
        # Email volume over time
        df['month_year'] = df['datetime'].dt.strftime('%Y-%m')

        # Group by month
        mail_time = df.groupby('month_year', observed=True).size().reset_index(name='count')

        fig = px.line(mail_time, x='month_year', y='count',
                      title='Email Volume Over Time',
                      labels={'month_year': 'Month', 'count': 'Number of Emails'})

        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

        if 'size' in df.columns:
            # Email size distribution
            fig = px.histogram(df, x='size',
                               title='Email Size Distribution',
                               labels={'size': 'Email Size', 'count': 'Number of Emails'},
                               color_discrete_sequence=['blue'])

            fig.update_layout(bargap=0.1)
            st.plotly_chart(fig, use_container_width=True)

            # Average email size over time
            size_time = df.groupby('month_year', observed=True)['size'].mean().reset_index()

            fig = px.line(size_time, x='month_year', y='size',
                          title='Average Email Size Over Time',
                          labels={'month_year': 'Month', 'size': 'Average Size'})

            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        if 'spam_score' in df.columns:
            # Spam score distribution
            fig = px.histogram(df, x='spam_score',
                               title='Spam Score Distribution',
                               labels={'spam_score': 'Spam Score', 'count': 'Number of Emails'},
                               color_discrete_sequence=['red'])

            fig.update_layout(bargap=0.1)
            st.plotly_chart(fig, use_container_width=True)

            # Spam trend over time
            df['is_spam'] = df['spam_score'] > 0.5
            spam_time = df.groupby(['month_year', 'is_spam'], observed=True).size().reset_index(name='count')

            fig = px.line(spam_time, x='month_year', y='count', color='is_spam',
                          title='Spam vs. Ham Over Time',
                          labels={'month_year': 'Month', 'count': 'Number of Emails', 'is_spam': 'Is Spam'},
                          color_discrete_map={True: 'red', False: 'green'})

            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

            # Spam percentage over time
            spam_pct = df.groupby('month_year', observed=True)['is_spam'].mean().reset_index()
            spam_pct['percentage'] = spam_pct['is_spam'] * 100

            fig = px.line(spam_pct, x='month_year', y='percentage',
                          title='Spam Percentage Over Time',
                          labels={'month_year': 'Month', 'percentage': 'Spam Percentage (%)'},
                          color_discrete_sequence=['red'])

            fig.update_xaxes(tickangle=45)
            fig.update_layout(yaxis=dict(range=[0, 100]))
            st.plotly_chart(fig, use_container_width=True)

# Run the historical dashboard if this file is executed directly
if __name__ == "__main__":
    show_historical_dashboard()
