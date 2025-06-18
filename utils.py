"""
Utility functions for the Log Analyzer application.
"""
import os
import pandas as pd
import streamlit as st
from datetime import datetime
import hashlib
import re
from typing import Dict, List, Tuple, Optional, Any, Union

from config import LOG_TYPES, DEFAULT_LOG_TYPE

def detect_log_type(file_path: str) -> str:
    """
    Detect the type of log file based on its content.

    Args:
        file_path: Path to the log file

    Returns:
        str: Detected log type (browsing, virus, mail, etc.)
    """
    try:
        with open(file_path, 'r') as file:
            sample_lines = [file.readline() for _ in range(5)]  # Read first 5 lines

        # Check for patterns in the sample lines
        for line in sample_lines:
            # Check for browsing log patterns (URLs, HTTP status codes)
            if re.search(r'https?://|www\.|\.(com|org|net|edu|gov)', line) and re.search(r'\b[1-5][0-9]{2}\b', line):
                return "browsing"

            # Check for virus log patterns
            if re.search(r'virus|malware|trojan|infected|quarantine', line, re.IGNORECASE):
                return "virus"

            # Check for mail log patterns
            if re.search(r'@|sender|recipient|subject|spam|mail', line, re.IGNORECASE):
                return "mail"

        # Default to browsing logs if no pattern is detected
        return DEFAULT_LOG_TYPE
    except Exception as e:
        st.error(f"Error detecting log type: {e}")
        return DEFAULT_LOG_TYPE

def format_timestamp(timestamp: Union[int, str], log_type: str = DEFAULT_LOG_TYPE) -> str:
    """
    Format a timestamp based on the log type.

    Args:
        timestamp: The timestamp to format
        log_type: The type of log

    Returns:
        str: Formatted timestamp
    """
    try:
        if isinstance(timestamp, str) and timestamp.isdigit():
            timestamp = int(timestamp)

        if isinstance(timestamp, int):
            # Unix timestamp
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        else:
            # Try to parse using the format specified in LOG_TYPES
            dt_format = LOG_TYPES.get(log_type, {}).get("datetime_format", "%Y%m%d%H%M%S")
            dt = datetime.strptime(timestamp, dt_format)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        # Return the original timestamp if parsing fails
        return str(timestamp)

def get_file_hash(file_path: str) -> str:
    """
    Generate a hash for a file to use as a cache key.

    Args:
        file_path: Path to the file

    Returns:
        str: MD5 hash of the file
    """
    try:
        with open(file_path, 'rb') as file:
            file_hash = hashlib.md5(file.read()).hexdigest()
        return file_hash
    except Exception:
        # Return a timestamp-based string if file reading fails
        return f"nohash_{datetime.now().strftime('%Y%m%d%H%M%S')}"

def get_human_readable_size(size_bytes: Union[int, str]) -> str:
    """
    Convert size in bytes to human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        str: Human-readable size (e.g., "1.23 MB")
    """
    try:
        size_bytes = int(size_bytes)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024 or unit == 'TB':
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
    except (ValueError, TypeError):
        return str(size_bytes)

def get_time_periods(df: pd.DataFrame, timestamp_col: str = 'timestamp') -> Dict[str, pd.DataFrame]:
    """
    Split a DataFrame into different time periods for analysis.

    Args:
        df: DataFrame containing log data
        timestamp_col: Name of the timestamp column

    Returns:
        Dict: Dictionary with time periods as keys and filtered DataFrames as values
    """
    # Ensure timestamp column is datetime
    try:
        # First try to convert as numeric (Unix timestamp)
        if pd.api.types.is_numeric_dtype(df[timestamp_col]):
            df['datetime'] = pd.to_datetime(df[timestamp_col], unit='s')
        else:
            # Try to convert string timestamps
            # Check if it's a Unix timestamp stored as string
            if df[timestamp_col].astype(str).str.match(r'^\d{10}$').all():
                df['datetime'] = pd.to_datetime(df[timestamp_col].astype(float), unit='s')
            else:
                # Try with format from config if available
                from config import LOG_TYPES
                log_type = st.session_state.get('log_type', 'browsing')
                datetime_format = LOG_TYPES.get(log_type, {}).get('datetime_format')

                if datetime_format:
                    df['datetime'] = pd.to_datetime(df[timestamp_col], format=datetime_format, errors='coerce')
                else:
                    # Fall back to pandas default parser with error handling
                    df['datetime'] = pd.to_datetime(df[timestamp_col], errors='coerce')
    except Exception as e:
        st.error(f"Error parsing timestamps: {e}")
        # Create a default datetime column to avoid errors
        df['datetime'] = pd.Timestamp.now()

    # Create time period filters
    now = pd.Timestamp.now()
    last_hour = now - pd.Timedelta(hours=1)
    last_day = now - pd.Timedelta(days=1)
    last_week = now - pd.Timedelta(weeks=1)
    last_month = now - pd.Timedelta(days=30)

    # Create filtered DataFrames
    periods = {
        "Last Hour": df[df['datetime'] >= last_hour],
        "Last Day": df[df['datetime'] >= last_day],
        "Last Week": df[df['datetime'] >= last_week],
        "Last Month": df[df['datetime'] >= last_month],
        "All Time": df
    }

    return periods

def create_download_link(df: pd.DataFrame, filename: str = "data.csv") -> str:
    """
    Create a download link for a DataFrame.

    Args:
        df: DataFrame to download
        filename: Name of the download file

    Returns:
        str: HTML link for downloading the DataFrame
    """
    import base64
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download {filename}</a>'
    return href

def optimize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimize a DataFrame's memory usage by downcasting numeric types and
    converting object types to categories when appropriate.

    Args:
        df: DataFrame to optimize

    Returns:
        pd.DataFrame: Memory-optimized DataFrame
    """
    # Make a copy to avoid modifying the original DataFrame
    result = df.copy()

    # Process each column
    for col in result.columns:
        # Skip datetime columns
        if pd.api.types.is_datetime64_any_dtype(result[col]):
            continue

        # Downcast numeric columns
        if pd.api.types.is_numeric_dtype(result[col]):
            # Integers
            if pd.api.types.is_integer_dtype(result[col]):
                # Check if column can be represented as unsigned int
                if result[col].min() >= 0:
                    result[col] = pd.to_numeric(result[col], downcast='unsigned')
                else:
                    result[col] = pd.to_numeric(result[col], downcast='integer')
            # Floats
            elif pd.api.types.is_float_dtype(result[col]):
                result[col] = pd.to_numeric(result[col], downcast='float')

        # Convert object columns to category if they have few unique values
        elif pd.api.types.is_object_dtype(result[col]):
            # Calculate unique ratio (unique values / total values)
            unique_ratio = result[col].nunique() / len(result)

            # If less than 50% unique values, convert to category
            if unique_ratio < 0.5:
                result[col] = result[col].astype('category')

    return result

def get_dataframe_memory_usage(df: pd.DataFrame) -> str:
    """
    Get a human-readable string of the memory usage of a DataFrame.

    Args:
        df: DataFrame to analyze

    Returns:
        str: Human-readable memory usage string
    """
    memory_bytes = df.memory_usage(deep=True).sum()

    # Convert to appropriate unit
    if memory_bytes < 1024:
        return f"{memory_bytes} bytes"
    elif memory_bytes < 1024**2:
        return f"{memory_bytes/1024:.2f} KB"
    elif memory_bytes < 1024**3:
        return f"{memory_bytes/(1024**2):.2f} MB"
    else:
        return f"{memory_bytes/(1024**3):.2f} GB"

def extract_domain_from_url(url: str) -> str:
    """
    Extract the domain from a URL.

    Args:
        url: URL string

    Returns:
        str: Domain name
    """
    # Simple regex to extract domain
    domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
    if domain_match:
        return domain_match.group(1)
    return "unknown"

def analyze_site_visits(df: pd.DataFrame) -> Dict:
    """
    Analyze site visits from browsing logs.

    Args:
        df: DataFrame containing browsing log data

    Returns:
        Dict: Dictionary with site visit analysis results
    """
    results = {}

    if 'url' in df.columns:
        # Extract domains
        df['domain'] = df['url'].apply(extract_domain_from_url)

        # Top visited domains
        top_domains = df['domain'].value_counts().head(10).to_dict()
        results['top_domains'] = top_domains

        # Visits by category if available
        if 'category' in df.columns:
            category_visits = df['category'].value_counts().to_dict()
            results['category_visits'] = category_visits

            # Top domains by category
            top_domains_by_category = {}
            for category in df['category'].unique():
                category_df = df[df['category'] == category]
                top_domains_by_category[category] = category_df['domain'].value_counts().head(5).to_dict()
            results['top_domains_by_category'] = top_domains_by_category

        # Visits by user if available
        if 'username' in df.columns:
            user_visits = {}
            for user in df['username'].unique():
                user_df = df[df['username'] == user]
                user_visits[user] = {
                    'total_visits': len(user_df),
                    'top_domains': user_df['domain'].value_counts().head(5).to_dict()
                }
            results['user_visits'] = user_visits

    return results
