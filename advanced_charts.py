"""
Advanced visualization module using Plotly for the Log Analyzer application.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple

from config import CHART_WIDTH, CHART_HEIGHT, COLOR_SCHEME, DEFAULT_LOG_TYPE
from utils import get_time_periods

def show_advanced_charts():
    """Display advanced charts using Plotly."""
    st.title("Advanced Log Visualization")

    # Check if user is logged in
    if not st.session_state.logged_in:
        st.warning("Please log in to view advanced charts.")
        return

    # Check if log data is available
    if 'log_data' not in st.session_state or st.session_state.log_data is None or st.session_state.log_data.empty:
        st.warning("No log data available. Please analyze logs in the Charts section first.")
        return

    # Get the log data
    df = st.session_state.log_data
    log_type = st.session_state.log_type if 'log_type' in st.session_state else DEFAULT_LOG_TYPE

    # Sidebar for controls
    with st.sidebar:
        st.subheader("Visualization Controls")

        # Date range selection
        st.write("### Date Range")

        # Get min and max dates from the data
        if 'datetime' in df.columns:
            min_date = df['datetime'].min().date()
            max_date = df['datetime'].max().date()
        else:
            min_date = datetime.now().date() - timedelta(days=7)
            max_date = datetime.now().date()

        # Date range picker
        start_date = st.date_input("Start Date", min_date)
        end_date = st.date_input("End Date", max_date)

        # Convert to datetime for filtering
        start_datetime = pd.to_datetime(start_date)
        end_datetime = pd.to_datetime(end_date) + timedelta(days=1) - timedelta(seconds=1)  # End of the day

        # Filter data by date range
        if 'datetime' in df.columns:
            filtered_df = df[(df['datetime'] >= start_datetime) & (df['datetime'] <= end_datetime)]
        else:
            filtered_df = df  # No datetime column, use all data

        # Additional filters based on log type
        st.write("### Filters")

        if log_type == "browsing":
            # Filter by username
            if 'username' in filtered_df.columns:
                usernames = filtered_df['username'].unique()
                selected_usernames = st.multiselect("Select Users", usernames, default=usernames[:5] if len(usernames) > 5 else usernames)
                if selected_usernames:
                    filtered_df = filtered_df[filtered_df['username'].isin(selected_usernames)]

            # Filter by status code
            if 'status_code' in filtered_df.columns:
                status_codes = filtered_df['status_code'].unique()
                selected_status = st.multiselect("Select Status Codes", status_codes)
                if selected_status:
                    filtered_df = filtered_df[filtered_df['status_code'].isin(selected_status)]

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

            # Filter by action taken
            if 'action_taken' in filtered_df.columns:
                actions = filtered_df['action_taken'].unique()
                selected_actions = st.multiselect("Select Actions", actions)
                if selected_actions:
                    filtered_df = filtered_df[filtered_df['action_taken'].isin(selected_actions)]

        elif log_type == "mail":
            # Filter by spam score
            if 'spam_score' in filtered_df.columns:
                min_spam = float(filtered_df['spam_score'].min())
                max_spam = float(filtered_df['spam_score'].max())
                spam_range = st.slider("Spam Score Range", min_spam, max_spam, (min_spam, max_spam))
                filtered_df = filtered_df[(filtered_df['spam_score'] >= spam_range[0]) & (filtered_df['spam_score'] <= spam_range[1])]

    # Display data summary
    st.subheader("Data Summary")
    st.write(f"Showing {len(filtered_df)} records from {start_date} to {end_date}")

    # Display the filtered data
    with st.expander("View Filtered Data"):
        st.dataframe(filtered_df)

    # Create advanced visualizations based on log type
    if log_type == "browsing":
        display_browsing_visualizations(filtered_df)
    elif log_type == "virus":
        display_virus_visualizations(filtered_df)
    elif log_type == "mail":
        display_mail_visualizations(filtered_df)
    else:
        st.error(f"Unsupported log type: {log_type}")

def display_browsing_visualizations(df: pd.DataFrame):
    """
    Display advanced visualizations for browsing logs.

    Args:
        df: DataFrame containing browsing log data
    """
    st.subheader("Browsing Log Analysis")

    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs(["Traffic Analysis", "User Activity", "Status Codes", "Categories"])

    with tab1:
        st.write("### Traffic Over Time")

        # Check if datetime column exists
        if 'datetime' in df.columns:
            # Group by hour
            df['hour'] = df['datetime'].dt.hour
            hourly_traffic = df.groupby('hour').size().reset_index(name='count')

            # Create hourly traffic chart
            fig = px.line(hourly_traffic, x='hour', y='count',
                          title='Hourly Traffic Distribution',
                          labels={'hour': 'Hour of Day', 'count': 'Number of Requests'},
                          markers=True)

            fig.update_layout(
                xaxis=dict(tickmode='linear', tick0=0, dtick=1),
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)

            # Traffic by day of week
            if len(df) > 10:  # Only show if we have enough data
                df['day_of_week'] = df['datetime'].dt.day_name()
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                daily_traffic = df.groupby('day_of_week').size().reset_index(name='count')

                # Reorder days
                daily_traffic['day_of_week'] = pd.Categorical(daily_traffic['day_of_week'], categories=day_order, ordered=True)
                daily_traffic = daily_traffic.sort_values('day_of_week')

                fig = px.bar(daily_traffic, x='day_of_week', y='count',
                             title='Traffic by Day of Week',
                             labels={'day_of_week': 'Day', 'count': 'Number of Requests'},
                             color='count', color_continuous_scale='Viridis')

                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Datetime information not available for time-based analysis.")

    with tab2:
        st.write("### User Activity Analysis")

        if 'username' in df.columns and 'ip_address' in df.columns:
            # User activity by count
            user_activity = df.groupby('username').size().reset_index(name='count')
            user_activity = user_activity.sort_values('count', ascending=False)

            fig = px.bar(user_activity.head(10), x='username', y='count',
                         title='Top 10 Users by Activity',
                         labels={'username': 'Username', 'count': 'Number of Requests'},
                         color='count', color_continuous_scale='Viridis')

            st.plotly_chart(fig, use_container_width=True)

            # User activity heatmap
            if 'datetime' in df.columns:
                df['hour'] = df['datetime'].dt.hour
                df['day_of_week'] = df['datetime'].dt.day_name()

                # Get top 5 users
                top_users = user_activity.head(5)['username'].tolist()

                # Filter for top users
                top_user_df = df[df['username'].isin(top_users)]

                # Create pivot table for heatmap
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                top_user_df['day_of_week'] = pd.Categorical(top_user_df['day_of_week'], categories=day_order, ordered=True)

                # Group by user, day, and hour
                user_time_pivot = top_user_df.groupby(['username', 'day_of_week', 'hour']).size().reset_index(name='count')

                # Create heatmap for each user
                for user in top_users:
                    user_data = user_time_pivot[user_time_pivot['username'] == user]

                    # Create pivot table
                    pivot_data = user_data.pivot(index='day_of_week', columns='hour', values='count').fillna(0)

                    # Reorder days
                    pivot_data = pivot_data.reindex(day_order)

                    # Create heatmap
                    try:
                        # Make sure pivot_data has all hours as columns
                        for hour in range(24):
                            if hour not in pivot_data.columns:
                                pivot_data[hour] = 0

                        # Sort columns to ensure they match the x values
                        pivot_data = pivot_data.reindex(sorted(pivot_data.columns), axis=1)

                        fig = px.imshow(pivot_data,
                                        labels=dict(x="Hour of Day", y="Day of Week", color="Request Count"),
                                        x=list(range(24)),
                                        y=day_order,
                                        title=f"Activity Heatmap for {user}",
                                        color_continuous_scale="Viridis")
                    except Exception as e:
                        st.error(f"Error creating heatmap: {e}")
                        # Create a simple bar chart instead
                        user_data_sum = user_data.groupby('hour')['count'].sum().reset_index()
                        fig = px.bar(user_data_sum, x='hour', y='count',
                                    title=f"Hourly Activity for {user}",
                                    labels={'hour': 'Hour of Day', 'count': 'Request Count'})

                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Username or IP address information not available for user analysis.")

    with tab3:
        st.write("### HTTP Status Code Analysis")

        if 'status_code' in df.columns:
            # Group status codes by class (2xx, 3xx, 4xx, 5xx)
            df['status_class'] = df['status_code'].apply(lambda x: f"{x // 100}xx")
            status_class_counts = df.groupby('status_class').size().reset_index(name='count')

            # Create pie chart for status classes
            fig = px.pie(status_class_counts, names='status_class', values='count',
                         title='HTTP Status Code Classes',
                         color='status_class',
                         color_discrete_map={'2xx': 'green', '3xx': 'blue', '4xx': 'orange', '5xx': 'red'})

            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

            # Create bar chart for specific status codes
            status_counts = df.groupby('status_code').size().reset_index(name='count')
            status_counts = status_counts.sort_values('count', ascending=False)

            fig = px.bar(status_counts, x='status_code', y='count',
                         title='HTTP Status Code Distribution',
                         labels={'status_code': 'Status Code', 'count': 'Number of Requests'},
                         color='status_code')

            st.plotly_chart(fig, use_container_width=True)

            # Status codes over time
            if 'datetime' in df.columns:
                df['date'] = df['datetime'].dt.date
                status_time = df.groupby(['date', 'status_class']).size().reset_index(name='count')

                fig = px.line(status_time, x='date', y='count', color='status_class',
                              title='Status Codes Over Time',
                              labels={'date': 'Date', 'count': 'Number of Requests', 'status_class': 'Status Class'})

                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Status code information not available for status analysis.")

    with tab4:
        st.write("### Category Analysis")

        if 'category' in df.columns:
            # Category distribution
            category_counts = df.groupby('category').size().reset_index(name='count')
            category_counts = category_counts.sort_values('count', ascending=False)

            fig = px.bar(category_counts.head(10), x='category', y='count',
                         title='Top 10 Categories',
                         labels={'category': 'Category', 'count': 'Number of Requests'},
                         color='count', color_continuous_scale='Viridis')

            st.plotly_chart(fig, use_container_width=True)

            # Category by user
            if 'username' in df.columns:
                # Get top 5 users and top 5 categories
                top_users = df.groupby('username').size().reset_index(name='count').sort_values('count', ascending=False).head(5)['username'].tolist()
                top_categories = category_counts.head(5)['category'].tolist()

                # Filter data
                top_data = df[df['username'].isin(top_users) & df['category'].isin(top_categories)]

                # Group by user and category
                user_category = top_data.groupby(['username', 'category']).size().reset_index(name='count')

                # Create heatmap
                user_category_pivot = user_category.pivot(index='username', columns='category', values='count').fillna(0)

                fig = px.imshow(user_category_pivot,
                                labels=dict(x="Category", y="Username", color="Request Count"),
                                title="User-Category Heatmap",
                                color_continuous_scale="Viridis")

                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Category information not available for category analysis.")

def display_virus_visualizations(df: pd.DataFrame):
    """
    Display advanced visualizations for virus logs.

    Args:
        df: DataFrame containing virus log data
    """
    st.subheader("Virus Log Analysis")

    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Virus Distribution", "Severity Analysis", "Time Trends"])

    with tab1:
        st.write("### Virus Type Distribution")

        if 'virus_name' in df.columns:
            # Virus name distribution
            virus_counts = df.groupby('virus_name').size().reset_index(name='count')
            virus_counts = virus_counts.sort_values('count', ascending=False)

            fig = px.bar(virus_counts.head(10), x='virus_name', y='count',
                         title='Top 10 Virus Types',
                         labels={'virus_name': 'Virus Name', 'count': 'Occurrences'},
                         color='count', color_continuous_scale='Reds')

            st.plotly_chart(fig, use_container_width=True)

            # Pie chart for virus distribution
            fig = px.pie(virus_counts.head(5), names='virus_name', values='count',
                         title='Top 5 Virus Types Distribution')

            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Virus name information not available for virus distribution analysis.")

    with tab2:
        st.write("### Severity Analysis")

        if 'severity' in df.columns:
            # Severity distribution
            severity_counts = df.groupby('severity').size().reset_index(name='count')

            # Create a custom color map for severity
            severity_colors = {'high': 'red', 'medium': 'orange', 'low': 'yellow', 'info': 'blue'}

            fig = px.bar(severity_counts, x='severity', y='count',
                         title='Severity Distribution',
                         labels={'severity': 'Severity Level', 'count': 'Occurrences'},
                         color='severity',
                         color_discrete_map=severity_colors)

            st.plotly_chart(fig, use_container_width=True)

            # Severity by action taken
            if 'action_taken' in df.columns:
                severity_action = df.groupby(['severity', 'action_taken']).size().reset_index(name='count')

                fig = px.bar(severity_action, x='severity', y='count', color='action_taken',
                             title='Actions Taken by Severity Level',
                             labels={'severity': 'Severity Level', 'count': 'Occurrences', 'action_taken': 'Action Taken'},
                             barmode='group')

                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Severity information not available for severity analysis.")

    with tab3:
        st.write("### Time Trends")

        if 'datetime' in df.columns:
            # Group by date
            df['date'] = df['datetime'].dt.date
            date_counts = df.groupby('date').size().reset_index(name='count')

            fig = px.line(date_counts, x='date', y='count',
                          title='Virus Detections Over Time',
                          labels={'date': 'Date', 'count': 'Number of Detections'},
                          markers=True)

            st.plotly_chart(fig, use_container_width=True)

            # Severity over time
            if 'severity' in df.columns:
                severity_time = df.groupby(['date', 'severity']).size().reset_index(name='count')

                fig = px.line(severity_time, x='date', y='count', color='severity',
                              title='Severity Levels Over Time',
                              labels={'date': 'Date', 'count': 'Number of Detections', 'severity': 'Severity Level'})

                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Datetime information not available for time trend analysis.")

def display_mail_visualizations(df: pd.DataFrame):
    """
    Display advanced visualizations for mail logs.

    Args:
        df: DataFrame containing mail log data
    """
    st.subheader("Mail Log Analysis")

    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Mail Traffic", "Spam Analysis", "Attachment Analysis"])

    with tab1:
        st.write("### Mail Traffic Analysis")

        if 'datetime' in df.columns:
            # Group by date
            df['date'] = df['datetime'].dt.date
            date_counts = df.groupby('date').size().reset_index(name='count')

            fig = px.line(date_counts, x='date', y='count',
                          title='Mail Traffic Over Time',
                          labels={'date': 'Date', 'count': 'Number of Emails'},
                          markers=True)

            st.plotly_chart(fig, use_container_width=True)

            # Mail traffic by hour
            df['hour'] = df['datetime'].dt.hour
            hourly_traffic = df.groupby('hour').size().reset_index(name='count')

            fig = px.bar(hourly_traffic, x='hour', y='count',
                         title='Hourly Mail Distribution',
                         labels={'hour': 'Hour of Day', 'count': 'Number of Emails'},
                         color='count', color_continuous_scale='Blues')

            fig.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=1))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Datetime information not available for mail traffic analysis.")

    with tab2:
        st.write("### Spam Analysis")

        if 'spam_score' in df.columns:
            # Create histogram of spam scores
            fig = px.histogram(df, x='spam_score',
                               title='Distribution of Spam Scores',
                               labels={'spam_score': 'Spam Score', 'count': 'Number of Emails'},
                               color_discrete_sequence=['blue'])

            fig.update_layout(bargap=0.1)
            st.plotly_chart(fig, use_container_width=True)

            # Spam score threshold analysis
            thresholds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
            spam_counts = []

            for threshold in thresholds:
                spam_count = (df['spam_score'] >= threshold).sum()
                spam_counts.append({'threshold': threshold, 'count': spam_count})

            spam_threshold_df = pd.DataFrame(spam_counts)

            fig = px.line(spam_threshold_df, x='threshold', y='count',
                          title='Emails Above Spam Score Threshold',
                          labels={'threshold': 'Spam Score Threshold', 'count': 'Number of Emails'},
                          markers=True)

            st.plotly_chart(fig, use_container_width=True)

            # Spam by sender domain
            if 'sender' in df.columns:
                # Extract domain from sender email
                df['sender_domain'] = df['sender'].apply(lambda x: x.split('@')[-1] if '@' in str(x) else 'Unknown')

                # Group by domain and calculate average spam score
                domain_spam = df.groupby('sender_domain')['spam_score'].mean().reset_index()
                domain_spam = domain_spam.sort_values('spam_score', ascending=False)

                fig = px.bar(domain_spam.head(10), x='sender_domain', y='spam_score',
                             title='Top 10 Domains by Average Spam Score',
                             labels={'sender_domain': 'Sender Domain', 'spam_score': 'Average Spam Score'},
                             color='spam_score', color_continuous_scale='Reds')

                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Spam score information not available for spam analysis.")

    with tab3:
        st.write("### Attachment Analysis")

        if 'attachment_count' in df.columns:
            # Distribution of attachment counts
            attachment_dist = df.groupby('attachment_count').size().reset_index(name='count')

            fig = px.bar(attachment_dist, x='attachment_count', y='count',
                         title='Distribution of Attachment Counts',
                         labels={'attachment_count': 'Number of Attachments', 'count': 'Number of Emails'},
                         color='attachment_count')

            st.plotly_chart(fig, use_container_width=True)

            # Relationship between attachments and spam score
            if 'spam_score' in df.columns:
                # Calculate average spam score by attachment count
                attachment_spam = df.groupby('attachment_count')['spam_score'].mean().reset_index()

                fig = px.line(attachment_spam, x='attachment_count', y='spam_score',
                              title='Average Spam Score by Attachment Count',
                              labels={'attachment_count': 'Number of Attachments', 'spam_score': 'Average Spam Score'},
                              markers=True)

                st.plotly_chart(fig, use_container_width=True)

                # Scatter plot of attachment count vs spam score
                fig = px.scatter(df, x='attachment_count', y='spam_score',
                                 title='Attachment Count vs Spam Score',
                                 labels={'attachment_count': 'Number of Attachments', 'spam_score': 'Spam Score'},
                                 color='spam_score', color_continuous_scale='Reds',
                                 opacity=0.7)

                fig.update_traces(marker=dict(size=10))
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Attachment count information not available for attachment analysis.")

# Run the advanced charts if this file is executed directly
if __name__ == "__main__":
    show_advanced_charts()
