"""
Machine learning module for the Log Analyzer application.
Provides anomaly detection and predictive analytics capabilities.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional, Union, Any, Tuple

# Try to import scikit-learn, but make it optional
try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import DBSCAN
    from sklearn.decomposition import PCA
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    st.warning("scikit-learn not installed. Machine learning features will be limited.")

# Try to import prophet for time series forecasting
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

def detect_anomalies(df: pd.DataFrame, contamination: float = 0.05) -> pd.DataFrame:
    """
    Detect anomalies in log data using Isolation Forest algorithm.
    
    Args:
        df: DataFrame containing log data
        contamination: The proportion of outliers in the data set (default: 0.05)
        
    Returns:
        DataFrame with anomaly scores and flags
    """
    if not SKLEARN_AVAILABLE:
        st.error("scikit-learn is required for anomaly detection.")
        return df
    
    # Create a copy of the DataFrame to avoid modifying the original
    result_df = df.copy()
    
    # Select numerical features for anomaly detection
    numerical_features = df.select_dtypes(include=['number']).columns.tolist()
    
    # We need at least one numerical feature for anomaly detection
    if len(numerical_features) == 0:
        st.warning("No numerical features found for anomaly detection.")
        result_df['anomaly_score'] = 0
        result_df['is_anomaly'] = 'Unknown'
        return result_df
    
    try:
        # Fill missing values
        df_clean = df[numerical_features].fillna(0)
        
        # Standardize the data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df_clean)
        
        # Initialize and fit the model
        model = IsolationForest(contamination=contamination, random_state=42)
        result_df['anomaly_score'] = model.fit_predict(scaled_data)
        
        # Convert predictions to binary (1: normal, -1: anomaly)
        result_df['is_anomaly'] = result_df['anomaly_score'].apply(lambda x: 'Anomaly' if x == -1 else 'Normal')
        
        return result_df
    
    except Exception as e:
        st.error(f"Error in anomaly detection: {e}")
        result_df['anomaly_score'] = 0
        result_df['is_anomaly'] = 'Error'
        return result_df

def cluster_logs(df: pd.DataFrame, eps: float = 0.5, min_samples: int = 5) -> pd.DataFrame:
    """
    Cluster log entries using DBSCAN algorithm.
    
    Args:
        df: DataFrame containing log data
        eps: The maximum distance between two samples for them to be considered as in the same neighborhood
        min_samples: The number of samples in a neighborhood for a point to be considered as a core point
        
    Returns:
        DataFrame with cluster labels
    """
    if not SKLEARN_AVAILABLE:
        st.error("scikit-learn is required for clustering.")
        return df
    
    # Create a copy of the DataFrame to avoid modifying the original
    result_df = df.copy()
    
    # Select numerical features for clustering
    numerical_features = df.select_dtypes(include=['number']).columns.tolist()
    
    # We need at least one numerical feature for clustering
    if len(numerical_features) == 0:
        st.warning("No numerical features found for clustering.")
        result_df['cluster'] = -1
        return result_df
    
    try:
        # Fill missing values
        df_clean = df[numerical_features].fillna(0)
        
        # Standardize the data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df_clean)
        
        # Reduce dimensionality if we have many features
        if len(numerical_features) > 2:
            pca = PCA(n_components=2)
            scaled_data = pca.fit_transform(scaled_data)
        
        # Initialize and fit the model
        model = DBSCAN(eps=eps, min_samples=min_samples)
        result_df['cluster'] = model.fit_predict(scaled_data)
        
        # Add PCA components for visualization
        if len(numerical_features) > 2:
            result_df['pca_1'] = scaled_data[:, 0]
            result_df['pca_2'] = scaled_data[:, 1]
        
        return result_df
    
    except Exception as e:
        st.error(f"Error in clustering: {e}")
        result_df['cluster'] = -1
        return result_df

def forecast_time_series(df: pd.DataFrame, time_col: str, value_col: str, periods: int = 30) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Forecast time series data using Prophet.
    
    Args:
        df: DataFrame containing time series data
        time_col: Name of the column containing timestamps
        value_col: Name of the column containing values to forecast
        periods: Number of periods to forecast
        
    Returns:
        Tuple of (forecast DataFrame, original DataFrame with forecast)
    """
    if not PROPHET_AVAILABLE:
        st.error("Prophet is required for time series forecasting.")
        return pd.DataFrame(), df
    
    try:
        # Prepare data for Prophet
        prophet_df = df[[time_col, value_col]].copy()
        prophet_df.columns = ['ds', 'y']
        
        # Create and fit the model
        model = Prophet(daily_seasonality=True, yearly_seasonality=True, weekly_seasonality=True)
        model.fit(prophet_df)
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=periods)
        
        # Make predictions
        forecast = model.predict(future)
        
        # Merge forecast with original data
        result_df = df.copy()
        forecast_df = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
        forecast_df.columns = [time_col, 'forecast', 'forecast_lower', 'forecast_upper']
        
        # Return both the forecast and the original data with forecast
        return forecast_df, result_df
    
    except Exception as e:
        st.error(f"Error in time series forecasting: {e}")
        return pd.DataFrame(), df

def show_anomaly_detection():
    """Display the anomaly detection interface."""
    st.title("Anomaly Detection")
    
    # Check if user is logged in
    if not st.session_state.logged_in:
        st.warning("Please log in to access anomaly detection.")
        return
    
    # Check if scikit-learn is available
    if not SKLEARN_AVAILABLE:
        st.error("scikit-learn is required for anomaly detection. Please install it using 'pip install scikit-learn'.")
        return
    
    # Check if log data is available
    if 'log_data' not in st.session_state or st.session_state.log_data is None or st.session_state.log_data.empty:
        st.warning("No log data available. Please analyze logs in the Charts section first.")
        return
    
    # Get the log data
    df = st.session_state.log_data
    log_type = st.session_state.log_type if 'log_type' in st.session_state else "browsing"
    
    # Sidebar for controls
    with st.sidebar:
        st.subheader("Anomaly Detection Settings")
        
        # Anomaly detection method
        detection_method = st.selectbox(
            "Detection Method",
            options=["Isolation Forest", "DBSCAN Clustering"],
            index=0
        )
        
        # Parameters for Isolation Forest
        if detection_method == "Isolation Forest":
            contamination = st.slider(
                "Contamination (expected % of anomalies)",
                min_value=0.01,
                max_value=0.5,
                value=0.05,
                step=0.01,
                format="%.2f"
            )
        
        # Parameters for DBSCAN
        else:
            eps = st.slider(
                "Epsilon (max distance between points)",
                min_value=0.1,
                max_value=2.0,
                value=0.5,
                step=0.1
            )
            
            min_samples = st.slider(
                "Min Samples (min points in neighborhood)",
                min_value=2,
                max_value=20,
                value=5
            )
        
        # Features to use
        numerical_features = df.select_dtypes(include=['number']).columns.tolist()
        
        if len(numerical_features) > 0:
            selected_features = st.multiselect(
                "Features to Use",
                options=numerical_features,
                default=numerical_features[:3] if len(numerical_features) > 3 else numerical_features
            )
        else:
            st.warning("No numerical features found in the data.")
            selected_features = []
        
        # Run detection button
        run_detection = st.button("Run Anomaly Detection")
    
    # Main content area
    st.subheader("Anomaly Detection Results")
    
    if run_detection:
        with st.spinner("Running anomaly detection..."):
            # Filter data to use only selected features
            if selected_features:
                analysis_df = df[selected_features].copy()
                
                # Add datetime column if available
                if 'datetime' in df.columns:
                    analysis_df['datetime'] = df['datetime']
                
                # Run anomaly detection
                if detection_method == "Isolation Forest":
                    result_df = detect_anomalies(analysis_df, contamination)
                else:
                    result_df = cluster_logs(analysis_df, eps, min_samples)
                
                # Merge results back to original data
                if detection_method == "Isolation Forest":
                    df['anomaly_score'] = result_df['anomaly_score']
                    df['is_anomaly'] = result_df['is_anomaly']
                else:
                    df['cluster'] = result_df['cluster']
                    if 'pca_1' in result_df.columns and 'pca_2' in result_df.columns:
                        df['pca_1'] = result_df['pca_1']
                        df['pca_2'] = result_df['pca_2']
                
                # Store results in session state
                st.session_state.anomaly_results = df
                
                # Display results
                if detection_method == "Isolation Forest":
                    display_isolation_forest_results(df)
                else:
                    display_dbscan_results(df)
            else:
                st.error("Please select at least one feature for anomaly detection.")
    
    # If we already have results, display them
    elif 'anomaly_results' in st.session_state and not st.session_state.anomaly_results.empty:
        df = st.session_state.anomaly_results
        if 'is_anomaly' in df.columns:
            display_isolation_forest_results(df)
        elif 'cluster' in df.columns:
            display_dbscan_results(df)

def display_isolation_forest_results(df: pd.DataFrame):
    """
    Display the results of Isolation Forest anomaly detection.
    
    Args:
        df: DataFrame containing anomaly detection results
    """
    # Count anomalies
    anomaly_count = (df['is_anomaly'] == 'Anomaly').sum()
    normal_count = (df['is_anomaly'] == 'Normal').sum()
    
    # Display summary
    st.write(f"Found {anomaly_count} anomalies out of {len(df)} log entries ({anomaly_count/len(df)*100:.2f}%).")
    
    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Anomaly Overview", "Anomaly Details", "Time Analysis"])
    
    with tab1:
        # Pie chart of anomalies vs normal
        fig = px.pie(
            names=['Normal', 'Anomaly'],
            values=[normal_count, anomaly_count],
            title="Anomaly Distribution",
            color_discrete_sequence=['green', 'red']
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Feature distribution by anomaly status
        numerical_features = df.select_dtypes(include=['number']).columns.tolist()
        
        if len(numerical_features) > 0:
            feature_to_plot = st.selectbox(
                "Select Feature to Visualize",
                options=[f for f in numerical_features if f not in ['anomaly_score']],
                index=0 if len(numerical_features) > 0 else None
            )
            
            if feature_to_plot:
                fig = px.box(
                    df,
                    x='is_anomaly',
                    y=feature_to_plot,
                    color='is_anomaly',
                    title=f"{feature_to_plot} Distribution by Anomaly Status",
                    color_discrete_map={'Normal': 'green', 'Anomaly': 'red'}
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Filter to show only anomalies
        anomalies_df = df[df['is_anomaly'] == 'Anomaly'].copy()
        
        if not anomalies_df.empty:
            st.write("### Anomalous Log Entries")
            st.dataframe(anomalies_df)
            
            # Allow download of anomalies
            csv = anomalies_df.to_csv(index=False)
            st.download_button(
                label="Download Anomalies CSV",
                data=csv,
                file_name="log_anomalies.csv",
                mime="text/csv"
            )
            
            # Show details of most anomalous entries
            st.write("### Top 5 Most Anomalous Entries")
            top_anomalies = anomalies_df.sort_values('anomaly_score').head(5)
            
            for i, (_, row) in enumerate(top_anomalies.iterrows()):
                with st.expander(f"Anomaly #{i+1}"):
                    for col in row.index:
                        st.write(f"**{col}:** {row[col]}")
        else:
            st.info("No anomalies detected.")
    
    with tab3:
        # Time-based analysis if datetime column exists
        if 'datetime' in df.columns:
            # Group by date and anomaly status
            df['date'] = df['datetime'].dt.date
            anomaly_time = df.groupby(['date', 'is_anomaly']).size().reset_index(name='count')
            
            fig = px.line(
                anomaly_time,
                x='date',
                y='count',
                color='is_anomaly',
                title="Anomalies Over Time",
                labels={'date': 'Date', 'count': 'Number of Entries', 'is_anomaly': 'Status'},
                color_discrete_map={'Normal': 'green', 'Anomaly': 'red'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Heatmap of anomalies by hour and day of week
            df['hour'] = df['datetime'].dt.hour
            df['day_of_week'] = df['datetime'].dt.day_name()
            
            # Create pivot table for anomalies
            anomaly_pivot = df[df['is_anomaly'] == 'Anomaly'].groupby(['day_of_week', 'hour']).size().unstack(fill_value=0)
            
            # Reorder days
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            anomaly_pivot = anomaly_pivot.reindex(day_order)
            
            fig = px.imshow(
                anomaly_pivot,
                labels=dict(x="Hour of Day", y="Day of Week", color="Anomaly Count"),
                x=list(range(24)),
                y=day_order,
                title="Anomaly Heatmap by Day and Hour",
                color_continuous_scale="Reds"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Datetime information not available for time-based analysis.")

def display_dbscan_results(df: pd.DataFrame):
    """
    Display the results of DBSCAN clustering.
    
    Args:
        df: DataFrame containing clustering results
    """
    # Count clusters
    cluster_counts = df['cluster'].value_counts().reset_index()
    cluster_counts.columns = ['cluster', 'count']
    
    # Noise points (cluster = -1) are potential anomalies
    noise_count = (df['cluster'] == -1).sum()
    
    # Display summary
    st.write(f"Found {len(cluster_counts)-1} clusters and {noise_count} noise points (potential anomalies).")
    
    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Cluster Overview", "Cluster Details", "PCA Visualization"])
    
    with tab1:
        # Bar chart of cluster sizes
        fig = px.bar(
            cluster_counts,
            x='cluster',
            y='count',
            title="Cluster Sizes",
            labels={'cluster': 'Cluster ID', 'count': 'Number of Entries'},
            color='cluster',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Pie chart of clusters
        fig = px.pie(
            cluster_counts,
            names='cluster',
            values='count',
            title="Cluster Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Select cluster to view
        cluster_to_view = st.selectbox(
            "Select Cluster to View",
            options=sorted(df['cluster'].unique()),
            index=0
        )
        
        # Filter to show only selected cluster
        cluster_df = df[df['cluster'] == cluster_to_view].copy()
        
        if not cluster_df.empty:
            st.write(f"### Cluster {cluster_to_view} Entries")
            st.dataframe(cluster_df)
            
            # Allow download of cluster data
            csv = cluster_df.to_csv(index=False)
            st.download_button(
                label=f"Download Cluster {cluster_to_view} CSV",
                data=csv,
                file_name=f"cluster_{cluster_to_view}.csv",
                mime="text/csv"
            )
            
            # Show summary statistics for the cluster
            st.write(f"### Cluster {cluster_to_view} Statistics")
            
            numerical_features = cluster_df.select_dtypes(include=['number']).columns.tolist()
            numerical_features = [f for f in numerical_features if f not in ['cluster', 'pca_1', 'pca_2']]
            
            if numerical_features:
                st.dataframe(cluster_df[numerical_features].describe())
    
    with tab3:
        # PCA visualization if available
        if 'pca_1' in df.columns and 'pca_2' in df.columns:
            fig = px.scatter(
                df,
                x='pca_1',
                y='pca_2',
                color='cluster',
                title="PCA Visualization of Clusters",
                labels={'pca_1': 'Principal Component 1', 'pca_2': 'Principal Component 2', 'cluster': 'Cluster'},
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("PCA components not available for visualization.")

def show_time_series_forecasting():
    """Display the time series forecasting interface."""
    st.title("Time Series Forecasting")
    
    # Check if user is logged in
    if not st.session_state.logged_in:
        st.warning("Please log in to access time series forecasting.")
        return
    
    # Check if Prophet is available
    if not PROPHET_AVAILABLE:
        st.error("Prophet is required for time series forecasting. Please install it using 'pip install prophet'.")
        return
    
    # Check if log data is available
    if 'log_data' not in st.session_state or st.session_state.log_data is None or st.session_state.log_data.empty:
        st.warning("No log data available. Please analyze logs in the Charts section first.")
        return
    
    # Get the log data
    df = st.session_state.log_data
    
    # Check if datetime column exists
    if 'datetime' not in df.columns:
        st.error("Datetime information not available for time series forecasting.")
        return
    
    # Sidebar for controls
    with st.sidebar:
        st.subheader("Forecasting Settings")
        
        # Aggregate by time period
        time_period = st.selectbox(
            "Aggregate By",
            options=["Hour", "Day", "Week", "Month"],
            index=1
        )
        
        # Select metric to forecast
        numerical_features = df.select_dtypes(include=['number']).columns.tolist()
        
        if len(numerical_features) > 0:
            metric_to_forecast = st.selectbox(
                "Metric to Forecast",
                options=["Count"] + numerical_features,
                index=0
            )
        else:
            metric_to_forecast = "Count"
        
        # Forecast horizon
        forecast_periods = st.slider(
            "Forecast Periods",
            min_value=1,
            max_value=90,
            value=30
        )
        
        # Run forecast button
        run_forecast = st.button("Run Forecast")
    
    # Main content area
    st.subheader("Time Series Forecast")
    
    if run_forecast:
        with st.spinner("Running forecast..."):
            # Prepare time series data
            if time_period == "Hour":
                df['period'] = df['datetime'].dt.floor('H')
            elif time_period == "Day":
                df['period'] = df['datetime'].dt.date
            elif time_period == "Week":
                df['period'] = df['datetime'].dt.to_period('W').dt.start_time
            else:  # Month
                df['period'] = df['datetime'].dt.to_period('M').dt.start_time
            
            # Aggregate data
            if metric_to_forecast == "Count":
                time_series = df.groupby('period').size().reset_index(name='value')
            else:
                time_series = df.groupby('period')[metric_to_forecast].sum().reset_index(name='value')
            
            # Run forecast
            forecast_df, result_df = forecast_time_series(
                time_series,
                'period',
                'value',
                forecast_periods
            )
            
            # Store results in session state
            st.session_state.forecast_results = forecast_df
            st.session_state.forecast_original = result_df
            
            # Display results
            display_forecast_results(forecast_df, time_series, metric_to_forecast, time_period)
    
    # If we already have results, display them
    elif 'forecast_results' in st.session_state and not st.session_state.forecast_results.empty:
        display_forecast_results(
            st.session_state.forecast_results,
            st.session_state.forecast_original,
            metric_to_forecast,
            time_period
        )

def display_forecast_results(forecast_df: pd.DataFrame, original_df: pd.DataFrame, metric: str, period: str):
    """
    Display the results of time series forecasting.
    
    Args:
        forecast_df: DataFrame containing forecast results
        original_df: DataFrame containing original time series data
        metric: Name of the metric being forecasted
        period: Time period used for aggregation
    """
    # Create combined dataframe for plotting
    if 'period' in original_df.columns and 'value' in original_df.columns:
        plot_df = original_df.copy()
        
        # Merge with forecast
        if 'period' in forecast_df.columns and 'forecast' in forecast_df.columns:
            forecast_data = forecast_df[['period', 'forecast', 'forecast_lower', 'forecast_upper']]
            plot_df = pd.merge(plot_df, forecast_data, on='period', how='outer')
    else:
        st.error("Invalid data format for plotting forecast.")
        return
    
    # Create tabs for different visualizations
    tab1, tab2 = st.tabs(["Forecast Chart", "Forecast Data"])
    
    with tab1:
        # Create forecast chart
        fig = go.Figure()
        
        # Add historical data
        fig.add_trace(go.Scatter(
            x=plot_df['period'],
            y=plot_df['value'],
            mode='lines+markers',
            name='Historical',
            line=dict(color='blue')
        ))
        
        # Add forecast
        fig.add_trace(go.Scatter(
            x=plot_df['period'],
            y=plot_df['forecast'],
            mode='lines',
            name='Forecast',
            line=dict(color='red')
        ))
        
        # Add confidence interval
        fig.add_trace(go.Scatter(
            x=plot_df['period'],
            y=plot_df['forecast_upper'],
            mode='lines',
            name='Upper Bound',
            line=dict(width=0),
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=plot_df['period'],
            y=plot_df['forecast_lower'],
            mode='lines',
            name='Lower Bound',
            line=dict(width=0),
            fillcolor='rgba(255, 0, 0, 0.1)',
            fill='tonexty',
            showlegend=False
        ))
        
        # Update layout
        fig.update_layout(
            title=f"{metric} Forecast by {period}",
            xaxis_title=period,
            yaxis_title=metric,
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Display forecast data
        st.write("### Forecast Data")
        st.dataframe(forecast_df)
        
        # Allow download of forecast data
        csv = forecast_df.to_csv(index=False)
        st.download_button(
            label="Download Forecast CSV",
            data=csv,
            file_name="forecast_data.csv",
            mime="text/csv"
        )
        
        # Display forecast statistics
        st.write("### Forecast Statistics")
        
        # Calculate forecast metrics
        if 'value' in plot_df.columns and 'forecast' in plot_df.columns:
            # Filter to only rows with both actual and forecast values
            eval_df = plot_df.dropna(subset=['value', 'forecast'])
            
            if not eval_df.empty:
                # Calculate error metrics
                mae = np.mean(np.abs(eval_df['value'] - eval_df['forecast']))
                mape = np.mean(np.abs((eval_df['value'] - eval_df['forecast']) / eval_df['value'])) * 100
                
                # Display metrics
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Mean Absolute Error (MAE)", f"{mae:.2f}")
                
                with col2:
                    st.metric("Mean Absolute Percentage Error (MAPE)", f"{mape:.2f}%")

# Run the module if executed directly
if __name__ == "__main__":
    show_anomaly_detection()
