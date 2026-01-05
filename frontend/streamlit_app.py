"""
FitTrack - Main Application Entry Point
Modular fitness tracking application with Streamlit
"""
import streamlit as st
import streamlit.components.v1 as components
from config import API_BASE, GLOBAL_CSS
from auth import initialize_session, check_oauth_callback, check_login, logout
from components import render_app_header, render_footer, render_sidebar_navigation
from pages_simple import landing_page, catalog_page, export_page
from pages_dashboard import dashboard_page, stats_page
from pages_workouts import workouts_page, new_workout_page, workout_detail_page
from pages_admin import admin_page
from pages_extra import achievements_page, tools_page, settings_page, workout_plans_page, goals_page

# Page configuration
st.set_page_config(
    page_title="FitTrack - Fitness Tracker",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"  # Changed to expanded so menu is visible
)

# Initialize session and authentication
initialize_session()

# Debug: log query params to see what we're working with
try:
    try:
        qp = st.query_params
    except AttributeError:
        qp = st.experimental_get_query_params()
    if 'auth' in qp:
        print(f"[App] Query params detected: {dict(qp)}")
except Exception as e:
    print(f"[App] Could not read query params: {e}")

check_oauth_callback()

# Apply global CSS styles
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# Additional CSS to hide status messages
st.markdown("""
<style>
/* Hide Streamlit status and spinner messages */
.stSpinner {
    display: none !important;
}
div[data-testid="stStatusWidget"] {
    display: none !important;
}
.stToast {
    display: none !important;
}
div[data-testid="stToastContainer"] {
    display: none !important;
}
/* Hide elements containing "Running" text */
div:contains("Running get_user") {
    display: none !important;
}
div[class*="status"]:contains("Running") {
    display: none !important;
}
.element-container:has([data-testid="stAlert"]) {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# Get current page from session state
current_page = st.session_state.get('page', 'landing')

# Decide whether to call the remote /me check or rely on session state set by OAuth
# If `skip_check_login` is set by `check_oauth_callback`, use the state prepared there and
# avoid calling `check_login()` which may clear the freshly-created session in the same run.
skip = st.session_state.pop('skip_check_login', False)
if not skip:
    logged = check_login()
else:
    logged = st.session_state.get('logged_in', False)

if not logged:
    # Not logged in - hide sidebar and show landing page with footer
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        display: none;
    }
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    landing_page()
else:
    # Logged in - show app content with sidebar and WITHOUT footer
    
    # Render sidebar navigation
    render_sidebar_navigation()
    
    # Render header without login button
    render_app_header(show_login_button=False)
    
    # Route to appropriate page
    if current_page == 'dashboard':
        dashboard_page()
    elif current_page == 'workouts':
        workouts_page()
    elif current_page == 'new_workout':
        new_workout_page()
    elif current_page == 'workout_detail':
        workout_detail_page()
    elif current_page == 'statistics':
        stats_page()
    elif current_page == 'catalog':
        catalog_page()
    elif current_page == 'export':
        export_page()
    elif current_page == 'achievements':
        achievements_page()
    elif current_page == 'tools':
        tools_page()
    elif current_page == 'workout_plans':
        workout_plans_page()
    elif current_page == 'goals':
        goals_page()
    elif current_page == 'settings':
        settings_page()
    elif current_page == 'admin':
        admin_page()
    else:
        # Default to dashboard
        st.session_state['page'] = 'dashboard'
        st.rerun()
