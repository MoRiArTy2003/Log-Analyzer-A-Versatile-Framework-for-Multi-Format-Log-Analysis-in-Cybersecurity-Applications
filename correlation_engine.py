"""
Log correlation engine for the Log Analyzer application.
Provides capabilities to correlate events across different log sources.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple

# Try to import networkx, but make it optional
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    # Create a placeholder for nx if networkx is not installed
    class PlaceholderModule:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    nx = PlaceholderModule()

def correlate_logs(df1: pd.DataFrame, df2: pd.DataFrame, time_window: int = 60,
                   datetime_col1: str = 'datetime', datetime_col2: str = 'datetime') -> pd.DataFrame:
    """
    Correlate events between two log sources within a time window.

    Args:
        df1: First DataFrame with log data
        df2: Second DataFrame with log data
        time_window: Time window in seconds for correlation
        datetime_col1: Name of the datetime column in df1
        datetime_col2: Name of the datetime column in df2

    Returns:
        DataFrame with correlated events
    """
    # Ensure datetime columns exist
    if datetime_col1 not in df1.columns or datetime_col2 not in df2.columns:
        st.error(f"Datetime columns not found: {datetime_col1} in df1 or {datetime_col2} in df2")
        return pd.DataFrame()

    # Create result container
    correlated_events = []

    # For each event in the first log
    for idx1, event1 in df1.iterrows():
        # Define time window
        start_time = event1[datetime_col1] - timedelta(seconds=time_window/2)
        end_time = event1[datetime_col1] + timedelta(seconds=time_window/2)

        # Find events in the second log within the time window
        related_events = df2[(df2[datetime_col2] >= start_time) &
                             (df2[datetime_col2] <= end_time)]

        # If related events found, add to results
        for idx2, event2 in related_events.iterrows():
            correlated_events.append({
                'event1_id': idx1,
                'event1_time': event1[datetime_col1],
                'event1_type': df1.name if hasattr(df1, 'name') else 'Log1',
                'event2_id': idx2,
                'event2_time': event2[datetime_col2],
                'event2_type': df2.name if hasattr(df2, 'name') else 'Log2',
                'time_difference': (event2[datetime_col2] - event1[datetime_col1]).total_seconds()
            })

    return pd.DataFrame(correlated_events)

def find_event_sequences(df: pd.DataFrame, time_window: int = 300,
                         datetime_col: str = 'datetime',
                         event_col: str = 'event_type',
                         min_sequence_length: int = 2) -> List[Dict[str, Any]]:
    """
    Find sequences of events within a time window.

    Args:
        df: DataFrame with log data
        time_window: Time window in seconds for sequence detection
        datetime_col: Name of the datetime column
        event_col: Name of the column containing event types
        min_sequence_length: Minimum length of sequences to detect

    Returns:
        List of dictionaries containing sequence information
    """
    # Ensure required columns exist
    if datetime_col not in df.columns or event_col not in df.columns:
        st.error(f"Required columns not found: {datetime_col} or {event_col}")
        return []

    # Sort by datetime
    sorted_df = df.sort_values(by=datetime_col)

    # Create result container
    sequences = []

    # Current sequence
    current_sequence = []

    # For each event
    for idx, event in sorted_df.iterrows():
        # If sequence is empty, add the first event
        if not current_sequence:
            current_sequence.append((idx, event))
            continue

        # Check if the event is within the time window of the last event in the sequence
        last_event = current_sequence[-1][1]
        time_diff = (event[datetime_col] - last_event[datetime_col]).total_seconds()

        if time_diff <= time_window:
            # Add to current sequence
            current_sequence.append((idx, event))
        else:
            # Save current sequence if it's long enough
            if len(current_sequence) >= min_sequence_length:
                sequences.append({
                    'start_time': current_sequence[0][1][datetime_col],
                    'end_time': current_sequence[-1][1][datetime_col],
                    'duration': (current_sequence[-1][1][datetime_col] - current_sequence[0][1][datetime_col]).total_seconds(),
                    'events': current_sequence,
                    'event_types': [event[1][event_col] for event in current_sequence],
                    'event_count': len(current_sequence)
                })

            # Start a new sequence
            current_sequence = [(idx, event)]

    # Check the last sequence
    if len(current_sequence) >= min_sequence_length:
        sequences.append({
            'start_time': current_sequence[0][1][datetime_col],
            'end_time': current_sequence[-1][1][datetime_col],
            'duration': (current_sequence[-1][1][datetime_col] - current_sequence[0][1][datetime_col]).total_seconds(),
            'events': current_sequence,
            'event_types': [event[1][event_col] for event in current_sequence],
            'event_count': len(current_sequence)
        })

    return sequences

def create_event_graph(df: pd.DataFrame, source_col: str, target_col: str,
                       weight_col: Optional[str] = None) -> Any:
    """
    Create a directed graph of events.

    Args:
        df: DataFrame with event relationships
        source_col: Name of the column containing source nodes
        target_col: Name of the column containing target nodes
        weight_col: Optional name of the column containing edge weights

    Returns:
        NetworkX DiGraph object or None if networkx is not available
    """
    if not NETWORKX_AVAILABLE:
        st.error("networkx is required for graph creation. Please install it using 'pip install networkx'.")
        return None

    # Create a directed graph
    G = nx.DiGraph()

    # Add edges from DataFrame
    for _, row in df.iterrows():
        source = row[source_col]
        target = row[target_col]

        # Add edge with weight if specified
        if weight_col and weight_col in df.columns:
            weight = row[weight_col]
            G.add_edge(source, target, weight=weight)
        else:
            G.add_edge(source, target)

    return G

def extract_event_type(df: pd.DataFrame, log_type: str) -> pd.DataFrame:
    """
    Extract event type from log data based on log type.

    Args:
        df: DataFrame with log data
        log_type: Type of log (browsing, virus, mail)

    Returns:
        DataFrame with added event_type column
    """
    # Create a copy of the DataFrame
    result_df = df.copy()

    # Add event_type column based on log type
    if log_type == "browsing":
        if 'status_code' in df.columns:
            # Categorize by status code
            result_df['event_type'] = df['status_code'].apply(
                lambda x: f"HTTP_{x // 100}xx" if pd.notnull(x) else "Unknown"
            )
        elif 'category' in df.columns:
            # Use category as event type
            result_df['event_type'] = df['category']
        else:
            result_df['event_type'] = "Browsing"

    elif log_type == "virus":
        if 'virus_name' in df.columns:
            # Use virus name as event type
            result_df['event_type'] = df['virus_name']
        elif 'action_taken' in df.columns:
            # Use action taken as event type
            result_df['event_type'] = df['action_taken']
        else:
            result_df['event_type'] = "Virus"

    elif log_type == "mail":
        if 'status' in df.columns:
            # Use mail status as event type
            result_df['event_type'] = df['status']
        elif 'spam_score' in df.columns:
            # Categorize by spam score
            result_df['event_type'] = df['spam_score'].apply(
                lambda x: "Spam" if x > 0.5 else "Ham" if pd.notnull(x) else "Unknown"
            )
        else:
            result_df['event_type'] = "Mail"

    else:
        # Default event type
        result_df['event_type'] = "Unknown"

    return result_df

def show_correlation_analysis():
    """Display the correlation analysis interface."""
    st.title("Log Correlation Analysis")

    # Check if user is logged in
    if not st.session_state.logged_in:
        st.warning("Please log in to access correlation analysis.")
        return

    # Check if log data is available
    if 'log_data' not in st.session_state or st.session_state.log_data is None or st.session_state.log_data.empty:
        st.warning("No log data available. Please analyze logs in the Charts section first.")
        return

    # Get the log data
    df = st.session_state.log_data
    log_type = st.session_state.log_type if 'log_type' in st.session_state else "browsing"

    # Check if datetime column exists
    if 'datetime' not in df.columns:
        if 'timestamp' in df.columns:
            # Try to convert timestamp to datetime
            if pd.api.types.is_numeric_dtype(df['timestamp']):
                df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
            else:
                df['datetime'] = pd.to_datetime(df['timestamp'])
        else:
            st.error("Datetime information not available for correlation analysis.")
            return

    # Extract event type
    df = extract_event_type(df, log_type)

    # Sidebar for controls
    with st.sidebar:
        st.subheader("Correlation Analysis Settings")

        # Analysis type selection
        analysis_type = st.selectbox(
            "Analysis Type",
            options=["Event Sequences", "Event Relationships", "Time-based Correlation"],
            index=0
        )

        # Settings based on analysis type
        if analysis_type == "Event Sequences":
            time_window = st.slider(
                "Time Window (seconds)",
                min_value=1,
                max_value=3600,
                value=300,
                step=1
            )

            min_sequence_length = st.slider(
                "Minimum Sequence Length",
                min_value=2,
                max_value=10,
                value=2
            )

            event_col = st.selectbox(
                "Event Type Column",
                options=[col for col in df.columns if col != 'datetime'],
                index=df.columns.get_loc('event_type') if 'event_type' in df.columns else 0
            )

        elif analysis_type == "Event Relationships":
            source_col = st.selectbox(
                "Source Column",
                options=[col for col in df.columns if col != 'datetime'],
                index=df.columns.get_loc('event_type') if 'event_type' in df.columns else 0
            )

            # For target, use the same column but with next event
            st.write(f"Target Column: Next {source_col}")

            weight_col = st.selectbox(
                "Weight Column (optional)",
                options=["None"] + [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])],
                index=0
            )

            if weight_col == "None":
                weight_col = None

        elif analysis_type == "Time-based Correlation":
            # For time-based correlation, we need to split the data
            split_column = st.selectbox(
                "Split Data By",
                options=[col for col in df.columns if col not in ['datetime', 'timestamp']],
                index=0
            )

            split_value = st.selectbox(
                "Split Value",
                options=sorted(df[split_column].unique()),
                index=0
            )

            time_window = st.slider(
                "Correlation Time Window (seconds)",
                min_value=1,
                max_value=3600,
                value=60,
                step=1
            )

        # Run analysis button
        run_analysis = st.button("Run Correlation Analysis")

    # Main content area
    st.subheader("Correlation Analysis Results")

    if run_analysis:
        with st.spinner("Running correlation analysis..."):
            if analysis_type == "Event Sequences":
                # Find event sequences
                sequences = find_event_sequences(
                    df,
                    time_window=time_window,
                    datetime_col='datetime',
                    event_col=event_col,
                    min_sequence_length=min_sequence_length
                )

                # Store results in session state
                st.session_state.sequence_results = sequences

                # Display results
                display_sequence_results(sequences, df)

            elif analysis_type == "Event Relationships":
                # Create event relationships DataFrame
                relationships_df = create_event_relationships(df, source_col)

                # Store results in session state
                st.session_state.relationship_results = relationships_df

                # Display results
                display_relationship_results(relationships_df, weight_col)

            elif analysis_type == "Time-based Correlation":
                # Split data
                df1 = df[df[split_column] == split_value]
                df2 = df[df[split_column] != split_value]

                # Set names for better identification
                df1.name = f"{split_column}={split_value}"
                df2.name = f"{split_column}≠{split_value}"

                # Correlate logs
                correlated_events = correlate_logs(
                    df1,
                    df2,
                    time_window=time_window,
                    datetime_col1='datetime',
                    datetime_col2='datetime'
                )

                # Store results in session state
                st.session_state.correlation_results = correlated_events

                # Display results
                display_correlation_results(correlated_events, df1, df2)

    # If we already have results, display them
    elif analysis_type == "Event Sequences" and 'sequence_results' in st.session_state:
        display_sequence_results(st.session_state.sequence_results, df)

    elif analysis_type == "Event Relationships" and 'relationship_results' in st.session_state:
        display_relationship_results(st.session_state.relationship_results, weight_col)

    elif analysis_type == "Time-based Correlation" and 'correlation_results' in st.session_state:
        # We need to recreate df1 and df2 for display
        df1 = df[df[split_column] == split_value]
        df2 = df[df[split_column] != split_value]

        df1.name = f"{split_column}={split_value}"
        df2.name = f"{split_column}≠{split_value}"

        display_correlation_results(st.session_state.correlation_results, df1, df2)

def create_event_relationships(df: pd.DataFrame, event_col: str) -> pd.DataFrame:
    """
    Create a DataFrame of event relationships (event transitions).

    Args:
        df: DataFrame with log data
        event_col: Name of the column containing event types

    Returns:
        DataFrame with event relationships
    """
    # Sort by datetime
    sorted_df = df.sort_values(by='datetime')

    # Create source and target columns
    sorted_df['next_event'] = sorted_df[event_col].shift(-1)

    # Remove the last row (which has NaN for next_event)
    relationships_df = sorted_df.dropna(subset=['next_event'])

    # Count transitions
    transitions = relationships_df.groupby([event_col, 'next_event']).size().reset_index(name='count')

    # Rename columns
    transitions.columns = ['source', 'target', 'count']

    return transitions

def display_sequence_results(sequences: List[Dict[str, Any]], df: pd.DataFrame):
    """
    Display the results of event sequence analysis.

    Args:
        sequences: List of dictionaries containing sequence information
        df: Original DataFrame with log data
    """
    if not sequences:
        st.warning("No event sequences found with the current settings.")
        return

    # Create tabs for different visualizations
    tab1, tab2 = st.tabs(["Sequence Overview", "Sequence Details"])

    with tab1:
        # Create a DataFrame for visualization
        seq_df = pd.DataFrame([
            {
                'sequence_id': i,
                'start_time': seq['start_time'],
                'end_time': seq['end_time'],
                'duration': seq['duration'],
                'event_count': seq['event_count'],
                'event_types': ', '.join(seq['event_types'])
            }
            for i, seq in enumerate(sequences)
        ])

        # Display summary
        st.write(f"Found {len(sequences)} event sequences.")

        # Display sequence DataFrame
        st.dataframe(seq_df)

        # Allow download of sequences
        csv = seq_df.to_csv(index=False)
        st.download_button(
            label="Download Sequences CSV",
            data=csv,
            file_name="event_sequences.csv",
            mime="text/csv"
        )

        # Visualize sequence lengths
        fig = px.histogram(
            seq_df,
            x='event_count',
            title='Sequence Lengths',
            labels={'event_count': 'Number of Events', 'count': 'Frequency'},
            color_discrete_sequence=['blue']
        )
        st.plotly_chart(fig, use_container_width=True)

        # Visualize sequence durations
        fig = px.histogram(
            seq_df,
            x='duration',
            title='Sequence Durations (seconds)',
            labels={'duration': 'Duration (seconds)', 'count': 'Frequency'},
            color_discrete_sequence=['green']
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        # Select sequence to view
        sequence_id = st.selectbox(
            "Select Sequence to View",
            options=list(range(len(sequences))),
            format_func=lambda x: f"Sequence {x} ({sequences[x]['event_count']} events, {sequences[x]['duration']:.2f} seconds)"
        )

        # Display selected sequence
        selected_sequence = sequences[sequence_id]

        st.write(f"### Sequence {sequence_id}")
        st.write(f"Start Time: {selected_sequence['start_time']}")
        st.write(f"End Time: {selected_sequence['end_time']}")
        st.write(f"Duration: {selected_sequence['duration']:.2f} seconds")
        st.write(f"Event Count: {selected_sequence['event_count']}")

        # Create a DataFrame of events in the sequence
        events_df = pd.DataFrame([
            {
                'event_id': event[0],
                'time': event[1]['datetime'],
                'event_type': event[1]['event_type']
            }
            for event in selected_sequence['events']
        ])

        # Display events
        st.write("### Events in Sequence")
        st.dataframe(events_df)

        # Create a timeline visualization
        fig = px.timeline(
            events_df,
            x_start='time',
            x_end='time',
            y='event_type',
            color='event_type',
            title=f"Timeline of Events in Sequence {sequence_id}"
        )

        # Update layout for better visualization
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(
            xaxis=dict(
                title="Time",
                type="date"
            ),
            yaxis=dict(
                title="Event Type"
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        # Show the original log entries
        st.write("### Original Log Entries")
        event_ids = [event[0] for event in selected_sequence['events']]
        st.dataframe(df.loc[event_ids])

def display_relationship_results(relationships_df: pd.DataFrame, weight_col: Optional[str] = None):
    """
    Display the results of event relationship analysis.

    Args:
        relationships_df: DataFrame with event relationships
        weight_col: Optional name of the column containing edge weights
    """
    if relationships_df.empty:
        st.warning("No event relationships found.")
        return

    # Create tabs for different visualizations
    tab1, tab2 = st.tabs(["Relationship Overview", "Network Graph"])

    with tab1:
        # Display summary
        st.write(f"Found {len(relationships_df)} event transitions.")

        # Display relationships DataFrame
        st.dataframe(relationships_df)

        # Allow download of relationships
        csv = relationships_df.to_csv(index=False)
        st.download_button(
            label="Download Relationships CSV",
            data=csv,
            file_name="event_relationships.csv",
            mime="text/csv"
        )

        # Visualize top transitions
        top_transitions = relationships_df.sort_values('count', ascending=False).head(10)

        fig = px.bar(
            top_transitions,
            x='source',
            y='count',
            color='target',
            title='Top 10 Event Transitions',
            labels={'source': 'Source Event', 'count': 'Frequency', 'target': 'Target Event'}
        )
        st.plotly_chart(fig, use_container_width=True)

        # Create a heatmap of transitions
        # Pivot the data for the heatmap
        pivot_df = relationships_df.pivot(index='source', columns='target', values='count').fillna(0)

        fig = px.imshow(
            pivot_df,
            labels=dict(x="Target Event", y="Source Event", color="Frequency"),
            title="Event Transition Heatmap",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        # Check if networkx is available
        if not NETWORKX_AVAILABLE:
            st.error("networkx is required for network visualization. Please install it using 'pip install networkx'.")
            return

        # Create a network graph
        try:
            # Create graph
            G = create_event_graph(
                relationships_df,
                source_col='source',
                target_col='target',
                weight_col='count'
            )

            # If graph creation failed, return
            if G is None:
                return

            # Get positions using a layout algorithm
            pos = nx.spring_layout(G, seed=42)

            # Create edge trace
            edge_x = []
            edge_y = []
            edge_text = []

            for edge in G.edges(data=True):
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

                # Add edge weight as text
                weight = edge[2].get('weight', 1)
                edge_text.append(f"{edge[0]} -> {edge[1]}: {weight}")

            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=0.5, color='#888'),
                hoverinfo='text',
                text=edge_text,
                mode='lines'
            )

            # Create node trace
            node_x = []
            node_y = []
            node_text = []
            node_size = []

            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_text.append(node)

                # Node size based on degree
                node_size.append(G.degree(node) * 10)

            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers',
                hoverinfo='text',
                text=node_text,
                marker=dict(
                    showscale=True,
                    colorscale='YlGnBu',
                    size=node_size,
                    colorbar=dict(
                        thickness=15,
                        title='Node Connections',
                        xanchor='left',
                        titleside='right'
                    ),
                    line_width=2
                )
            )

            # Create figure
            fig = go.Figure(data=[edge_trace, node_trace],
                            layout=go.Layout(
                                title='Event Relationship Network',
                                titlefont_size=16,
                                showlegend=False,
                                hovermode='closest',
                                margin=dict(b=20, l=5, r=5, t=40),
                                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                            ))

            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Error creating network graph: {e}")
            st.info("Try installing networkx with 'pip install networkx' for network visualization.")

def display_correlation_results(correlated_events: pd.DataFrame, df1: pd.DataFrame, df2: pd.DataFrame):
    """
    Display the results of time-based correlation analysis.

    Args:
        correlated_events: DataFrame with correlated events
        df1: First DataFrame with log data
        df2: Second DataFrame with log data
    """
    if correlated_events.empty:
        st.warning("No correlated events found with the current settings.")
        return

    # Create tabs for different visualizations
    tab1, tab2 = st.tabs(["Correlation Overview", "Correlation Details"])

    with tab1:
        # Display summary
        st.write(f"Found {len(correlated_events)} correlated event pairs.")

        # Display correlated events DataFrame
        st.dataframe(correlated_events)

        # Allow download of correlated events
        csv = correlated_events.to_csv(index=False)
        st.download_button(
            label="Download Correlated Events CSV",
            data=csv,
            file_name="correlated_events.csv",
            mime="text/csv"
        )

        # Visualize time differences
        fig = px.histogram(
            correlated_events,
            x='time_difference',
            title='Distribution of Time Differences',
            labels={'time_difference': 'Time Difference (seconds)', 'count': 'Frequency'},
            color_discrete_sequence=['purple']
        )
        st.plotly_chart(fig, use_container_width=True)

        # Visualize correlation over time
        if 'event1_time' in correlated_events.columns:
            # Group by hour
            correlated_events['hour'] = pd.to_datetime(correlated_events['event1_time']).dt.floor('H')
            hourly_counts = correlated_events.groupby('hour').size().reset_index(name='count')

            fig = px.line(
                hourly_counts,
                x='hour',
                y='count',
                title='Correlated Events Over Time',
                labels={'hour': 'Time', 'count': 'Number of Correlations'}
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        # Select a correlated event pair to view
        if not correlated_events.empty:
            event_pair_index = st.selectbox(
                "Select Correlated Event Pair",
                options=list(range(len(correlated_events))),
                format_func=lambda x: f"Pair {x} (Time Diff: {correlated_events.iloc[x]['time_difference']:.2f} seconds)"
            )

            # Display selected event pair
            selected_pair = correlated_events.iloc[event_pair_index]

            st.write(f"### Correlated Event Pair {event_pair_index}")
            st.write(f"Event 1 Time: {selected_pair['event1_time']}")
            st.write(f"Event 2 Time: {selected_pair['event2_time']}")
            st.write(f"Time Difference: {selected_pair['time_difference']:.2f} seconds")

            # Display the original log entries
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"### Event 1 ({selected_pair['event1_type']})")
                if 'event1_id' in selected_pair and selected_pair['event1_id'] in df1.index:
                    event1 = df1.loc[selected_pair['event1_id']]
                    for col in event1.index:
                        st.write(f"**{col}:** {event1[col]}")

            with col2:
                st.write(f"### Event 2 ({selected_pair['event2_type']})")
                if 'event2_id' in selected_pair and selected_pair['event2_id'] in df2.index:
                    event2 = df2.loc[selected_pair['event2_id']]
                    for col in event2.index:
                        st.write(f"**{col}:** {event2[col]}")

            # Create a timeline visualization
            timeline_data = pd.DataFrame([
                {
                    'Event': selected_pair['event1_type'],
                    'Time': selected_pair['event1_time']
                },
                {
                    'Event': selected_pair['event2_type'],
                    'Time': selected_pair['event2_time']
                }
            ])

            fig = px.timeline(
                timeline_data,
                x_start='Time',
                x_end='Time',
                y='Event',
                color='Event',
                title=f"Timeline of Correlated Events (Pair {event_pair_index})"
            )

            # Update layout for better visualization
            fig.update_yaxes(autorange="reversed")
            fig.update_layout(
                xaxis=dict(
                    title="Time",
                    type="date"
                ),
                yaxis=dict(
                    title="Event Type"
                )
            )

            st.plotly_chart(fig, use_container_width=True)

# Run the module if executed directly
if __name__ == "__main__":
    show_correlation_analysis()
