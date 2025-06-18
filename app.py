import streamlit as st

# Set page configuration (must be the first Streamlit command)
st.set_page_config(
    page_title="Log Analyser",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

import os
import sys

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import login_page, signup_page, logout_user, check_user_login, check_session_validity
from sidebar import configure_sidebar
from pages import (home_page, charts_page, advanced_charts_page, historical_dashboard_page,
                  real_time_monitor_page, anomaly_detection_page, forecasting_page,
                  geospatial_analysis_page, correlation_analysis_page, performance_dashboard_page,
                  report_preview_page, settings_page)

# Initialize session state variables if not already set
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'username' not in st.session_state:
    st.session_state.username = None

if 'user_role' not in st.session_state:
    st.session_state.user_role = None

if 'login_time' not in st.session_state:
    st.session_state.login_time = None

# Initialize application state variables
if 'log_data' not in st.session_state:
    st.session_state.log_data = None

if 'log_type' not in st.session_state:
    st.session_state.log_type = "browsing"

if 'time_period' not in st.session_state:
    st.session_state.time_period = "all"

if 'chart_type' not in st.session_state:
    st.session_state.chart_type = "bar"

# Add custom CSS
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 4px;
        padding: 10px 16px;
        background-color: #f0f2f6;
    }
    .stTabs [aria-selected="true"] {
        background-color: #007acc !important;
        color: white !important;
    }
    .stButton>button {
        width: 100%;
    }
    .stForm>div>div>div>div>div:nth-child(2) {
        gap: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar configuration
selected = configure_sidebar()

# Check if session is valid for logged-in users
if st.session_state.logged_in:
    check_session_validity()

# Main content based on selected option
if selected == "Home":
    home_page()

elif selected == "Charts":
    charts_page()

elif selected == "Advanced Charts":
    advanced_charts_page()

elif selected == "Historical Dashboard":
    historical_dashboard_page()

elif selected == "Real-time Monitor":
    real_time_monitor_page()

elif selected == "Anomaly Detection":
    anomaly_detection_page()

elif selected == "Forecasting":
    forecasting_page()

elif selected == "Geospatial Analysis":
    geospatial_analysis_page()

elif selected == "Correlation Analysis":
    correlation_analysis_page()

elif selected == "Performance":
    performance_dashboard_page()

elif selected == "Report":
    report_preview_page()

elif selected == "Settings":
    settings_page()

elif selected == "Logout":
    logout_user()

# Add footer
st.markdown("""
<div style='position: fixed; bottom: 0; left: 0; right: 0; background-color: #f0f2f6; padding: 5px; text-align: center; font-size: 0.8em;'>© 2024 Log Analyser | Developed for Cybersecurity Professionals</div>
""", unsafe_allow_html=True)
