import streamlit as st
import time

from config import THEME_COLORS, DEFAULT_THEME
from auth import check_session_validity

# Try to import streamlit_option_menu, but make it optional
try:
    from streamlit_option_menu import option_menu
    OPTION_MENU_AVAILABLE = True
except ImportError:
    OPTION_MENU_AVAILABLE = False
    st.warning("streamlit-option-menu not installed. Using standard sidebar.")

def configure_sidebar():
    """Configure and display the sidebar navigation menu."""
    # Check if user session is still valid
    if st.session_state.logged_in:
        check_session_validity()

    # Get theme colors
    theme = st.session_state.get('theme', DEFAULT_THEME)
    colors = THEME_COLORS.get(theme, THEME_COLORS['dark'])

    # Display app info
    with st.sidebar:
        st.markdown(f"""<div style='text-align: center; margin-bottom: 10px;'>
            <h3 style='color: {colors['primary']}'>Log Analyser</h3>
            <p style='color: {colors['text']}; font-size: 0.8em;'>Version 1.0.0</p>
            </div>""", unsafe_allow_html=True)

        # Display current time
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        st.markdown(f"""<div style='text-align: center; margin-bottom: 20px;'>
            <p style='color: {colors['secondary']}; font-size: 0.7em;'>{current_time}</p>
            </div>""", unsafe_allow_html=True)

        # Configure navigation menu
        if st.session_state.logged_in:
            # Basic menu options for all users
            menu_options = ["Home", "Charts", "Advanced Charts", "Historical Dashboard", "Real-time Monitor"]
            menu_icons = ["house", "bar-chart-line", "graph-up", "calendar3", "broadcast"]

            # Advanced analysis options for analysts and admins
            if st.session_state.get('user_role') in ['analyst', 'admin']:
                menu_options.extend(["Anomaly Detection", "Forecasting", "Geospatial Analysis", "Correlation Analysis"])
                menu_icons.extend(["exclamation-triangle", "graph-up-arrow", "globe", "link"])

            # Report option for all users
            menu_options.append("Report")
            menu_icons.append("file-earmark-text")

            # Performance dashboard for admins only
            if st.session_state.get('user_role') == 'admin':
                menu_options.append("Performance")
                menu_icons.append("speedometer")

            # Settings and logout for all users
            menu_options.extend(["Settings", "Logout"])
            menu_icons.extend(["gear", "box-arrow-left"])
        else:
            # Only home for non-logged in users
            menu_options = ["Home"]
            menu_icons = ["house"]

        # Use option_menu if available, otherwise use standard radio buttons
        if OPTION_MENU_AVAILABLE:
            selected = option_menu(
                menu_title=None,
                options=menu_options,
                icons=menu_icons,
                default_index=0,
                styles={
                    "container": {
                        "padding": "0!important",
                        "background-color": colors['background'],
                        "color": colors['text'],
                        "width": "100%",
                        "display": "flex",
                        "flex-direction": "column",
                    },
                    "icon": {"color": colors['primary'], "font-size": "1.2rem"},
                    "nav-link": {
                        "font-size": "1rem",
                        "text-align": "left",
                        "margin": "10px 0",
                        "padding": "10px",
                        "color": colors['text'],
                        "--hover-color": colors['secondary'],
                        "border-radius": "5px",
                        "transition": "background-color 0.3s",
                    },
                    "nav-link-selected": {
                        "background-color": colors['primary'],
                        "color": "#ffffff",
                    },
                },
            )
        else:
            # Use standard radio buttons as fallback
            st.subheader("Navigation")
            selected = st.radio(
                "Select Page",
                options=menu_options,
                index=0,
                horizontal=True
            )

        # Display user info if logged in
        if st.session_state.logged_in and st.session_state.username:
            st.markdown(f"""<div style='position: absolute; bottom: 20px; left: 10px; right: 10px; text-align: center;'>
                <p style='color: {colors['text']}; font-size: 0.8em;'>Logged in as:</p>
                <p style='color: {colors['primary']}; font-weight: bold;'>{st.session_state.username}</p>
                </div>""", unsafe_allow_html=True)

    return selected
