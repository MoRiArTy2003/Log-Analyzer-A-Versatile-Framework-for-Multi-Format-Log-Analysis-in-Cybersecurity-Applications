"""
Geospatial visualization module for the Log Analyzer application.
Provides IP geolocation and map-based visualizations.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional, Union, Any, Tuple
import json
import requests
import time
import os
from datetime import datetime

# Try to import geolocation libraries, but make them optional
try:
    import geoip2.database
    GEOIP_AVAILABLE = True
except ImportError:
    GEOIP_AVAILABLE = False

# Cache for storing IP geolocation data
IP_CACHE = {}

def get_ip_location(ip_address: str) -> Dict[str, Any]:
    """
    Get geolocation data for an IP address.
    
    Args:
        ip_address: IP address to geolocate
        
    Returns:
        Dict containing location data
    """
    # Check cache first
    if ip_address in IP_CACHE:
        return IP_CACHE[ip_address]
    
    # Default location data
    location_data = {
        'ip_address': ip_address,
        'latitude': None,
        'longitude': None,
        'country': 'Unknown',
        'city': 'Unknown',
        'region': 'Unknown',
        'isp': 'Unknown',
        'success': False
    }
    
    # Try GeoIP2 database if available
    if GEOIP_AVAILABLE:
        try:
            # Check if database file exists
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "GeoLite2-City.mmdb")
            
            if os.path.exists(db_path):
                reader = geoip2.database.Reader(db_path)
                response = reader.city(ip_address)
                
                location_data.update({
                    'latitude': response.location.latitude,
                    'longitude': response.location.longitude,
                    'country': response.country.name or 'Unknown',
                    'city': response.city.name or 'Unknown',
                    'region': response.subdivisions.most_specific.name if response.subdivisions else 'Unknown',
                    'success': True
                })
                
                # Cache the result
                IP_CACHE[ip_address] = location_data
                return location_data
        except Exception as e:
            st.warning(f"Error using GeoIP2 database: {e}")
    
    # Fallback to free IP API
    try:
        response = requests.get(f"https://ipapi.co/{ip_address}/json/", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'error' not in data:
                location_data.update({
                    'latitude': data.get('latitude'),
                    'longitude': data.get('longitude'),
                    'country': data.get('country_name', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('region', 'Unknown'),
                    'isp': data.get('org', 'Unknown'),
                    'success': True
                })
        
        # Cache the result
        IP_CACHE[ip_address] = location_data
        
        # Add delay to avoid rate limiting
        time.sleep(0.5)
        
        return location_data
    except Exception as e:
        st.warning(f"Error using IP API: {e}")
        
        # Cache the failed result to avoid repeated failures
        IP_CACHE[ip_address] = location_data
        return location_data

def enrich_data_with_locations(df: pd.DataFrame, ip_column: str = 'ip_address') -> pd.DataFrame:
    """
    Enrich a DataFrame with geolocation data for IP addresses.
    
    Args:
        df: DataFrame containing IP addresses
        ip_column: Name of the column containing IP addresses
        
    Returns:
        DataFrame with added geolocation columns
    """
    if ip_column not in df.columns:
        st.error(f"Column '{ip_column}' not found in the data.")
        return df
    
    # Create a copy of the DataFrame to avoid modifying the original
    result_df = df.copy()
    
    # Add geolocation columns
    result_df['latitude'] = None
    result_df['longitude'] = None
    result_df['country'] = 'Unknown'
    result_df['city'] = 'Unknown'
    result_df['region'] = 'Unknown'
    
    # Get unique IP addresses to reduce API calls
    unique_ips = df[ip_column].unique()
    
    # Show progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Process each IP address
    for i, ip in enumerate(unique_ips):
        # Update progress
        progress = (i + 1) / len(unique_ips)
        progress_bar.progress(progress)
        status_text.text(f"Processing IP {i+1}/{len(unique_ips)}: {ip}")
        
        # Skip invalid IPs
        if not isinstance(ip, str) or not ip.strip():
            continue
        
        # Get location data
        location = get_ip_location(ip)
        
        # Update DataFrame
        if location['success']:
            mask = result_df[ip_column] == ip
            result_df.loc[mask, 'latitude'] = location['latitude']
            result_df.loc[mask, 'longitude'] = location['longitude']
            result_df.loc[mask, 'country'] = location['country']
            result_df.loc[mask, 'city'] = location['city']
            result_df.loc[mask, 'region'] = location['region']
    
    # Clear progress bar and status text
    progress_bar.empty()
    status_text.empty()
    
    return result_df

def create_ip_map(df: pd.DataFrame) -> go.Figure:
    """
    Create a map visualization of IP addresses.
    
    Args:
        df: DataFrame containing geolocation data
        
    Returns:
        Plotly figure object
    """
    # Filter to rows with valid coordinates
    map_df = df.dropna(subset=['latitude', 'longitude'])
    
    if map_df.empty:
        st.error("No valid geolocation data found.")
        return None
    
    # Count occurrences of each location
    location_counts = map_df.groupby(['latitude', 'longitude', 'country', 'city', 'region']).size().reset_index(name='count')
    
    # Create hover text
    location_counts['hover_text'] = location_counts.apply(
        lambda row: f"Country: {row['country']}<br>Region: {row['region']}<br>City: {row['city']}<br>Count: {row['count']}",
        axis=1
    )
    
    # Create map
    fig = px.scatter_geo(
        location_counts,
        lat='latitude',
        lon='longitude',
        size='count',
        color='count',
        hover_name='city',
        hover_data={
            'latitude': False,
            'longitude': False,
            'count': True,
            'country': True,
            'region': True
        },
        projection='natural earth',
        title='Geographic Distribution of IP Addresses',
        color_continuous_scale='Viridis'
    )
    
    # Update layout
    fig.update_layout(
        geo=dict(
            showland=True,
            landcolor='rgb(217, 217, 217)',
            coastlinecolor='rgb(37, 102, 142)',
            countrycolor='rgb(37, 102, 142)',
            showocean=True,
            oceancolor='rgb(204, 229, 255)',
            showlakes=True,
            lakecolor='rgb(204, 229, 255)',
            showrivers=True,
            rivercolor='rgb(204, 229, 255)'
        )
    )
    
    return fig

def create_choropleth_map(df: pd.DataFrame) -> go.Figure:
    """
    Create a choropleth map visualization of countries.
    
    Args:
        df: DataFrame containing geolocation data
        
    Returns:
        Plotly figure object
    """
    # Count occurrences of each country
    country_counts = df['country'].value_counts().reset_index()
    country_counts.columns = ['country', 'count']
    
    # Create choropleth map
    fig = px.choropleth(
        country_counts,
        locations='country',
        locationmode='country names',
        color='count',
        hover_name='country',
        color_continuous_scale='Viridis',
        title='Log Entries by Country'
    )
    
    # Update layout
    fig.update_layout(
        geo=dict(
            showland=True,
            landcolor='rgb(217, 217, 217)',
            coastlinecolor='rgb(37, 102, 142)',
            countrycolor='rgb(37, 102, 142)',
            showocean=True,
            oceancolor='rgb(204, 229, 255)',
            showlakes=True,
            lakecolor='rgb(204, 229, 255)',
            showrivers=True,
            rivercolor='rgb(204, 229, 255)'
        )
    )
    
    return fig

def show_geospatial_analysis():
    """Display the geospatial analysis interface."""
    st.title("Geospatial Analysis")
    
    # Check if user is logged in
    if not st.session_state.logged_in:
        st.warning("Please log in to access geospatial analysis.")
        return
    
    # Check if log data is available
    if 'log_data' not in st.session_state or st.session_state.log_data is None or st.session_state.log_data.empty:
        st.warning("No log data available. Please analyze logs in the Charts section first.")
        return
    
    # Get the log data
    df = st.session_state.log_data
    log_type = st.session_state.log_type if 'log_type' in st.session_state else "browsing"
    
    # Check if IP address column exists
    ip_column = None
    for col in df.columns:
        if 'ip' in col.lower():
            ip_column = col
            break
    
    if not ip_column:
        st.error("No IP address column found in the data.")
        return
    
    # Sidebar for controls
    with st.sidebar:
        st.subheader("Geospatial Analysis Settings")
        
        # IP address column selection
        ip_column = st.selectbox(
            "IP Address Column",
            options=[col for col in df.columns if 'ip' in col.lower()],
            index=0
        )
        
        # Map type selection
        map_type = st.selectbox(
            "Map Type",
            options=["Scatter Map", "Choropleth Map", "Both"],
            index=0
        )
        
        # Run geolocation button
        run_geolocation = st.button("Run Geolocation")
    
    # Main content area
    st.subheader("Geospatial Analysis Results")
    
    if run_geolocation:
        with st.spinner("Running geolocation..."):
            # Enrich data with locations
            geo_df = enrich_data_with_locations(df, ip_column)
            
            # Store results in session state
            st.session_state.geo_results = geo_df
            
            # Display results
            display_geospatial_results(geo_df, map_type)
    
    # If we already have results, display them
    elif 'geo_results' in st.session_state and not st.session_state.geo_results.empty:
        display_geospatial_results(st.session_state.geo_results, map_type)

def display_geospatial_results(df: pd.DataFrame, map_type: str):
    """
    Display the results of geospatial analysis.
    
    Args:
        df: DataFrame containing geolocation data
        map_type: Type of map to display
    """
    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Maps", "Country Analysis", "Data"])
    
    with tab1:
        # Display maps based on selected type
        if map_type in ["Scatter Map", "Both"]:
            st.write("### IP Address Map")
            fig = create_ip_map(df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        
        if map_type in ["Choropleth Map", "Both"]:
            st.write("### Country Choropleth Map")
            fig = create_choropleth_map(df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Country analysis
        if 'country' in df.columns:
            # Count by country
            country_counts = df['country'].value_counts().reset_index()
            country_counts.columns = ['country', 'count']
            
            # Bar chart of top countries
            fig = px.bar(
                country_counts.head(10),
                x='country',
                y='count',
                title='Top 10 Countries',
                labels={'country': 'Country', 'count': 'Number of Entries'},
                color='count',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Pie chart of top countries
            fig = px.pie(
                country_counts.head(10),
                names='country',
                values='count',
                title='Top 10 Countries Distribution'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # If we have datetime information, show country trends over time
            if 'datetime' in df.columns:
                # Group by date and country
                df['date'] = df['datetime'].dt.date
                country_time = df.groupby(['date', 'country']).size().reset_index(name='count')
                
                # Get top 5 countries
                top_countries = country_counts.head(5)['country'].tolist()
                
                # Filter for top countries
                country_time_filtered = country_time[country_time['country'].isin(top_countries)]
                
                # Line chart of country trends
                fig = px.line(
                    country_time_filtered,
                    x='date',
                    y='count',
                    color='country',
                    title='Top Countries Over Time',
                    labels={'date': 'Date', 'count': 'Number of Entries', 'country': 'Country'}
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Display enriched data
        st.write("### Enriched Data with Geolocation")
        st.dataframe(df)
        
        # Allow download of enriched data
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download Enriched Data CSV",
            data=csv,
            file_name="geo_enriched_data.csv",
            mime="text/csv"
        )

# Run the module if executed directly
if __name__ == "__main__":
    show_geospatial_analysis()
