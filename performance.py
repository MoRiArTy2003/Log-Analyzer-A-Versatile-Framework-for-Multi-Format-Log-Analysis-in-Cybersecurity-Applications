"""
Performance optimization module for the Log Analyzer application.
Provides caching, parallel processing, and other performance enhancements.
"""
import streamlit as st
import pandas as pd
import numpy as np
import time
import os
import hashlib
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple, Callable
import functools
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# Import plotly for visualization
try:
    import plotly.graph_objects as go
except ImportError:
    # Create a placeholder for go if plotly is not installed
    class PlaceholderModule:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    go = PlaceholderModule()

# Import cache settings from config
from config import CACHE_DIR, CACHE_EXPIRATION, MAX_CACHE_SIZE

# Create cache directory if it doesn't exist
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_key(file_path: str, log_type: str, **kwargs) -> str:
    """
    Generate a cache key for a file and log type.

    Args:
        file_path: Path to the log file
        log_type: Type of log
        **kwargs: Additional parameters to include in the cache key

    Returns:
        str: Cache key
    """
    # Get file modification time
    try:
        mtime = os.path.getmtime(file_path)
    except (FileNotFoundError, OSError):
        mtime = 0

    # Create a string with all parameters
    key_str = f"{file_path}_{mtime}_{log_type}"

    # Add additional parameters
    for k, v in sorted(kwargs.items()):
        key_str += f"_{k}_{v}"

    # Create MD5 hash
    return hashlib.md5(key_str.encode()).hexdigest()

def cache_to_disk(func: Callable) -> Callable:
    """
    Decorator to cache function results to disk.

    Args:
        func: Function to cache

    Returns:
        Callable: Wrapped function with caching
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get cache key
        if 'file_path' in kwargs and 'log_type' in kwargs:
            cache_key = get_cache_key(kwargs['file_path'], kwargs['log_type'], **{k: v for k, v in kwargs.items() if k not in ['file_path', 'log_type']})
        else:
            # If required parameters are not in kwargs, don't cache
            return func(*args, **kwargs)

        # Cache file path
        cache_file = os.path.join(CACHE_DIR, f"{cache_key}.pkl")

        # Check if cache exists and is not expired
        if os.path.exists(cache_file):
            # Get cache age
            cache_age = time.time() - os.path.getmtime(cache_file)

            # Use cache expiration time from config
            if cache_age < CACHE_EXPIRATION:
                try:
                    # Load from cache
                    with open(cache_file, 'rb') as f:
                        result = pickle.load(f)

                    return result
                except Exception as e:
                    st.warning(f"Error loading from cache: {e}")

        # Call the original function
        result = func(*args, **kwargs)

        # Save to cache
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(result, f)

            # Manage cache size after adding new file
            manage_cache_size()
        except Exception as e:
            st.warning(f"Error saving to cache: {e}")

        return result

    return wrapper

def parallel_process(func: Callable, items: List[Any], max_workers: Optional[int] = None, use_processes: bool = False) -> List[Any]:
    """
    Process items in parallel using threads or processes.

    Args:
        func: Function to apply to each item
        items: List of items to process
        max_workers: Maximum number of workers (default: number of CPU cores)
        use_processes: Whether to use processes instead of threads

    Returns:
        List: Results of applying func to each item
    """
    if max_workers is None:
        max_workers = multiprocessing.cpu_count()

    # Choose executor based on use_processes
    Executor = ProcessPoolExecutor if use_processes else ThreadPoolExecutor

    # Process items in parallel
    with Executor(max_workers=max_workers) as executor:
        results = list(executor.map(func, items))

    return results

def chunk_dataframe(df: pd.DataFrame, num_chunks: int) -> List[pd.DataFrame]:
    """
    Split a DataFrame into chunks for parallel processing.

    Args:
        df: DataFrame to split
        num_chunks: Number of chunks

    Returns:
        List: List of DataFrame chunks
    """
    # Calculate chunk size
    chunk_size = len(df) // num_chunks
    if chunk_size == 0:
        chunk_size = 1

    # Split DataFrame into chunks
    return [df.iloc[i:i+chunk_size] for i in range(0, len(df), chunk_size)]

def optimize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimize a DataFrame for memory usage.

    Args:
        df: DataFrame to optimize

    Returns:
        DataFrame: Optimized DataFrame
    """
    # Create a copy of the DataFrame
    result_df = df.copy()

    # Optimize each column
    for col in result_df.columns:
        col_type = result_df[col].dtype

        # Optimize integers
        if pd.api.types.is_integer_dtype(col_type):
            # Get min and max values
            min_val = result_df[col].min()
            max_val = result_df[col].max()

            # Choose the smallest integer type that can represent the data
            if min_val >= 0:
                if max_val <= 255:
                    result_df[col] = result_df[col].astype(np.uint8)
                elif max_val <= 65535:
                    result_df[col] = result_df[col].astype(np.uint16)
                elif max_val <= 4294967295:
                    result_df[col] = result_df[col].astype(np.uint32)
                else:
                    result_df[col] = result_df[col].astype(np.uint64)
            else:
                if min_val >= -128 and max_val <= 127:
                    result_df[col] = result_df[col].astype(np.int8)
                elif min_val >= -32768 and max_val <= 32767:
                    result_df[col] = result_df[col].astype(np.int16)
                elif min_val >= -2147483648 and max_val <= 2147483647:
                    result_df[col] = result_df[col].astype(np.int32)
                else:
                    result_df[col] = result_df[col].astype(np.int64)

        # Optimize floats
        elif pd.api.types.is_float_dtype(col_type):
            # Check if float32 is sufficient
            result_df[col] = result_df[col].astype(np.float32)

        # Optimize strings (categorical)
        elif pd.api.types.is_string_dtype(col_type) or pd.api.types.is_object_dtype(col_type):
            # Check if column has few unique values
            num_unique = result_df[col].nunique()
            if num_unique < len(result_df) * 0.5:  # If less than 50% unique values
                result_df[col] = result_df[col].astype('category')

    return result_df

def show_performance_dashboard():
    """Display the performance dashboard."""
    st.title("Performance Dashboard")

    # Check if user is logged in
    if not st.session_state.logged_in:
        st.warning("Please log in to access the performance dashboard.")
        return

    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Cache Management", "Memory Usage", "Processing Stats"])

    with tab1:
        st.subheader("Cache Management")

        # Get cache statistics
        cache_files = [f for f in os.listdir(CACHE_DIR) if f.endswith('.pkl')]

        # Display cache summary
        st.write(f"Total cache files: {len(cache_files)}")

        if cache_files:
            # Calculate total cache size
            total_size = sum(os.path.getsize(os.path.join(CACHE_DIR, f)) for f in cache_files)
            st.write(f"Total cache size: {total_size / (1024 * 1024):.2f} MB / {MAX_CACHE_SIZE / (1024 * 1024):.2f} MB ({total_size / MAX_CACHE_SIZE * 100:.2f}%)")

            # Get cache age statistics
            now = time.time()
            ages = [(now - os.path.getmtime(os.path.join(CACHE_DIR, f))) / 3600 for f in cache_files]

            st.write(f"Oldest cache: {max(ages):.2f} hours")
            st.write(f"Newest cache: {min(ages):.2f} hours")

            # Cache management options
            st.subheader("Cache Actions")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Clear All Cache"):
                    for f in cache_files:
                        try:
                            os.remove(os.path.join(CACHE_DIR, f))
                        except Exception as e:
                            st.error(f"Error removing {f}: {e}")

                    st.success("Cache cleared successfully!")
                    st.rerun()

            with col2:
                # Clear old cache
                if st.button("Clear Old Cache (>24h)"):
                    cleared = 0
                    for f in cache_files:
                        file_path = os.path.join(CACHE_DIR, f)
                        age = (now - os.path.getmtime(file_path)) / 3600

                        if age > 24:
                            try:
                                os.remove(file_path)
                                cleared += 1
                            except Exception as e:
                                st.error(f"Error removing {f}: {e}")

                    st.success(f"Cleared {cleared} old cache files!")
                    st.rerun()

            # Display cache files
            st.subheader("Cache Files")

            # Create DataFrame for cache files
            cache_df = pd.DataFrame([
                {
                    'filename': f,
                    'size_mb': os.path.getsize(os.path.join(CACHE_DIR, f)) / (1024 * 1024),
                    'age_hours': (now - os.path.getmtime(os.path.join(CACHE_DIR, f))) / 3600,
                    'created': datetime.fromtimestamp(os.path.getmtime(os.path.join(CACHE_DIR, f)))
                }
                for f in cache_files
            ])

            # Sort by age
            cache_df = cache_df.sort_values('age_hours')

            # Display cache files
            st.dataframe(cache_df)
        else:
            st.info("No cache files found.")

    with tab2:
        st.subheader("Memory Usage")

        # Check if log data is available
        if 'log_data' not in st.session_state or st.session_state.log_data is None or st.session_state.log_data.empty:
            st.warning("No log data available. Please analyze logs in the Charts section first.")
        else:
            # Get memory usage of log data
            df = st.session_state.log_data

            # Calculate memory usage
            memory_usage = df.memory_usage(deep=True)
            total_memory = memory_usage.sum()

            # Display memory usage
            st.write(f"Total memory usage: {total_memory / (1024 * 1024):.2f} MB")

            # Display memory usage by column
            memory_df = pd.DataFrame({
                'column': memory_usage.index,
                'memory_mb': memory_usage.values / (1024 * 1024),
                'percent': memory_usage.values / total_memory * 100
            })

            # Sort by memory usage
            memory_df = memory_df.sort_values('memory_mb', ascending=False)

            # Display memory usage by column
            st.dataframe(memory_df)

            # Create bar chart of memory usage
            st.bar_chart(memory_df.set_index('column')['memory_mb'])

            # Optimize memory usage
            st.subheader("Memory Optimization")

            # Add detailed memory optimization options
            optimization_options = st.expander("Optimization Options", expanded=False)

            with optimization_options:
                st.write("Select optimization techniques to apply:")

                # Optimization options
                downcast_numeric = st.checkbox("Downcast Numeric Types", value=True,
                                              help="Convert numeric columns to the smallest possible type")

                convert_categorical = st.checkbox("Convert String to Categorical", value=True,
                                                help="Convert string columns with few unique values to categorical type")

                optimize_datetime = st.checkbox("Optimize Datetime Columns", value=True,
                                              help="Convert datetime columns to more efficient representations")

                drop_na_columns = st.checkbox("Drop Columns with All NAs", value=False,
                                            help="Remove columns that contain only NA values")

                # Advanced options
                st.write("Advanced Options:")
                categorical_threshold = st.slider("Categorical Conversion Threshold (%)",
                                                min_value=1, max_value=99, value=50,
                                                help="Convert string columns to categorical if unique values are below this percentage")

            # Memory usage before optimization
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Current Memory Usage", f"{total_memory / (1024 * 1024):.2f} MB")

            # Add a visual indicator of memory usage
            with col2:
                # Create a progress bar to visualize memory usage
                try:
                    import psutil
                    memory = psutil.virtual_memory()
                    memory_percent = total_memory / memory.total * 100
                    st.progress(min(memory_percent / 100, 1.0))
                    st.caption(f"Using {memory_percent:.2f}% of system memory")
                except ImportError:
                    pass

            # Optimize button with more detailed feedback
            if st.button("Optimize Memory Usage"):
                with st.spinner("Analyzing and optimizing memory usage..."):
                    # Get current memory usage
                    before_size = df.memory_usage(deep=True).sum() / (1024 * 1024)

                    # Create a progress bar for the optimization process
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    # Step 1: Analyze DataFrame
                    status_text.text("Analyzing DataFrame structure...")
                    progress_bar.progress(10)

                    # Get column types for reporting
                    dtypes_before = df.dtypes.value_counts()

                    # Step 2: Apply optimizations
                    status_text.text("Applying optimizations...")
                    progress_bar.progress(30)

                    # Create a copy of the DataFrame
                    optimized_df = df.copy()

                    # Apply selected optimizations
                    if downcast_numeric:
                        status_text.text("Downcasting numeric columns...")
                        progress_bar.progress(40)

                        # Process numeric columns
                        for col in optimized_df.select_dtypes(include=['int', 'float']).columns:
                            if pd.api.types.is_integer_dtype(optimized_df[col]):
                                # Check if column can be represented as unsigned int
                                if optimized_df[col].min() >= 0:
                                    optimized_df[col] = pd.to_numeric(optimized_df[col], downcast='unsigned')
                                else:
                                    optimized_df[col] = pd.to_numeric(optimized_df[col], downcast='integer')
                            elif pd.api.types.is_float_dtype(optimized_df[col]):
                                optimized_df[col] = pd.to_numeric(optimized_df[col], downcast='float')

                    if convert_categorical:
                        status_text.text("Converting string columns to categorical...")
                        progress_bar.progress(60)

                        # Process string/object columns
                        for col in optimized_df.select_dtypes(include=['object']).columns:
                            # Calculate unique ratio
                            unique_ratio = optimized_df[col].nunique() / len(optimized_df) * 100

                            # If below threshold, convert to category
                            if unique_ratio < categorical_threshold:
                                optimized_df[col] = optimized_df[col].astype('category')

                    if optimize_datetime:
                        status_text.text("Optimizing datetime columns...")
                        progress_bar.progress(80)

                        # Process datetime columns
                        for col in optimized_df.select_dtypes(include=['datetime']).columns:
                            # Check if datetime64[ns] is sufficient or if we need a larger unit
                            optimized_df[col] = pd.to_datetime(optimized_df[col], errors='ignore')

                    if drop_na_columns:
                        status_text.text("Removing columns with all NAs...")
                        progress_bar.progress(90)

                        # Drop columns with all NAs
                        optimized_df = optimized_df.dropna(axis=1, how='all')

                    # Step 3: Calculate results
                    status_text.text("Calculating results...")
                    progress_bar.progress(95)

                    # Get new memory usage
                    after_size = optimized_df.memory_usage(deep=True).sum() / (1024 * 1024)

                    # Calculate reduction
                    reduction = (before_size - after_size) / before_size * 100

                    # Get column types after optimization
                    dtypes_after = optimized_df.dtypes.value_counts()

                    # Update session state
                    st.session_state.log_data = optimized_df

                    # Complete the progress
                    progress_bar.progress(100)
                    status_text.text("Optimization complete!")

                    # Show results
                    st.success(f"Memory usage reduced from {before_size:.2f} MB to {after_size:.2f} MB ({reduction:.2f}% reduction)!")

                    # Show detailed results
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("**Before Optimization:**")
                        st.write(f"- Total Size: {before_size:.2f} MB")
                        st.write("- Column Types:")
                        for dtype, count in dtypes_before.items():
                            st.write(f"  - {dtype}: {count} columns")

                    with col2:
                        st.write("**After Optimization:**")
                        st.write(f"- Total Size: {after_size:.2f} MB")
                        st.write("- Column Types:")
                        for dtype, count in dtypes_after.items():
                            st.write(f"  - {dtype}: {count} columns")

    with tab3:
        st.subheader("Processing Statistics")

        # Display processing statistics if available
        if 'processing_stats' in st.session_state:
            stats = st.session_state.processing_stats

            # Create DataFrame for stats
            stats_df = pd.DataFrame(stats)

            # Display stats
            st.dataframe(stats_df)

            # Create line chart of processing times
            if 'processing_time' in stats_df.columns and 'timestamp' in stats_df.columns:
                st.line_chart(stats_df.set_index('timestamp')['processing_time'])
        else:
            st.info("No processing statistics available yet.")

        # System information
        st.subheader("System Information")

        # CPU cores
        st.write(f"CPU cores: {multiprocessing.cpu_count()}")

        # Memory information
        try:
            import psutil
            memory = psutil.virtual_memory()
            st.write(f"Total memory: {memory.total / (1024 * 1024 * 1024):.2f} GB")
            st.write(f"Available memory: {memory.available / (1024 * 1024 * 1024):.2f} GB")
            st.write(f"Memory usage: {memory.percent}%")

            # Create memory usage gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=memory.percent,
                title={'text': "Memory Usage"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "green"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "red"}
                    ]
                }
            ))

            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            st.warning("psutil not installed. Install with 'pip install psutil' for system information.")

# Function to track processing time
def track_processing_time(func: Callable) -> Callable:
    """
    Decorator to track processing time of a function.

    Args:
        func: Function to track

    Returns:
        Callable: Wrapped function with processing time tracking
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Start time
        start_time = time.time()

        # Call the original function
        result = func(*args, **kwargs)

        # End time
        end_time = time.time()

        # Calculate processing time
        processing_time = end_time - start_time

        # Add to processing stats
        if 'processing_stats' not in st.session_state:
            st.session_state.processing_stats = []

        st.session_state.processing_stats.append({
            'function': func.__name__,
            'processing_time': processing_time,
            'timestamp': datetime.now(),
            'args': str(args),
            'kwargs': str(kwargs)
        })

        # Keep only the last 100 stats
        if len(st.session_state.processing_stats) > 100:
            st.session_state.processing_stats = st.session_state.processing_stats[-100:]

        return result

    return wrapper

# Apply decorators to functions that need optimization
@cache_to_disk
def optimized_parse_file(file_path: str, log_type: str) -> pd.DataFrame:
    """
    Optimized version of parse_file with caching.

    Args:
        file_path: Path to the log file
        log_type: Type of log

    Returns:
        DataFrame: Parsed log data
    """
    from log_parser import LogParser

    # Create parser
    parser = LogParser(log_type)

    # Parse file
    df = parser.parse_file(file_path)

    # Optimize DataFrame
    return optimize_dataframe(df)

@track_processing_time
def optimized_detect_anomalies(df: pd.DataFrame, contamination: float = 0.05) -> pd.DataFrame:
    """
    Optimized version of detect_anomalies with processing time tracking.

    Args:
        df: DataFrame containing log data
        contamination: The proportion of outliers in the data set

    Returns:
        DataFrame: DataFrame with anomaly scores and flags
    """
    from ml_engine import detect_anomalies

    # Detect anomalies
    return detect_anomalies(df, contamination)

def manage_cache_size():
    """
    Manage cache size to prevent it from growing too large.
    Removes oldest cache files if total size exceeds MAX_CACHE_SIZE.
    """
    try:
        # Get all cache files
        cache_files = [os.path.join(CACHE_DIR, f) for f in os.listdir(CACHE_DIR) if f.endswith('.pkl')]

        # Calculate total size
        total_size = sum(os.path.getsize(f) for f in cache_files)

        # If total size exceeds maximum, remove oldest files
        if total_size > MAX_CACHE_SIZE and cache_files:
            # Sort files by modification time (oldest first)
            cache_files.sort(key=os.path.getmtime)

            # Remove files until we're under the limit
            while total_size > MAX_CACHE_SIZE * 0.8 and cache_files:  # Aim for 80% of max
                file_to_remove = cache_files.pop(0)  # Remove oldest
                file_size = os.path.getsize(file_to_remove)
                try:
                    os.remove(file_to_remove)
                    total_size -= file_size
                except Exception as e:
                    st.warning(f"Error removing cache file {file_to_remove}: {e}")
    except Exception as e:
        st.warning(f"Error managing cache size: {e}")

# Run the module if executed directly
if __name__ == "__main__":
    show_performance_dashboard()
