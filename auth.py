import streamlit as st
import os
import json
import hashlib
import time
from datetime import datetime

from config import AUTH_TIMEOUT, MIN_PASSWORD_LENGTH

# Initialize session state variables if not already set
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'username' not in st.session_state:
    st.session_state.username = None

if 'user_role' not in st.session_state:
    st.session_state.user_role = None

if 'login_time' not in st.session_state:
    st.session_state.login_time = None

# Path to the users directory
USERS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "users")

# Create users directory if it doesn't exist
os.makedirs(USERS_DIR, exist_ok=True)

# Check if user session is still valid
def check_session_validity():
    """Check if the user's session is still valid based on timeout."""
    if st.session_state.logged_in and st.session_state.login_time:
        # Calculate time elapsed since login
        elapsed_time = time.time() - st.session_state.login_time

        # If session has timed out, log the user out
        if elapsed_time > AUTH_TIMEOUT:
            logout_user()
            st.warning("Your session has expired. Please log in again.")
            return False

        # Refresh the login time to extend the session
        st.session_state.login_time = time.time()
        return True

    return False

# Check if user is logged in
def check_user_login():
    """Display user login status and logout button."""
    # First check if session is still valid
    check_session_validity()

    if st.session_state.logged_in:
        col1, col2 = st.columns([3, 1])

        with col1:
            st.write(f"Logged in as: {st.session_state.username}")
            if st.session_state.user_role:
                st.write(f"Role: {st.session_state.user_role}")

        with col2:
            if st.button("Logout"):
                logout_user()

# Login page logic
def login_page():
    """Display and handle the login page."""
    st.subheader("Login to your account")

    # Create a clean form layout
    with st.form("login_form"):
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        if not email or not password:
            st.error("Please enter both email and password.")
            return

        # First check for demo account
        if email == "demo@example.com" and password == "password":
            # Set session state variables for demo user
            st.session_state.logged_in = True
            st.session_state.username = "demo@example.com"
            st.session_state.user_role = "analyst"
            st.session_state.login_time = time.time()

            st.success("Logged in successfully as demo user!")
            st.rerun()
            return

        # Try to authenticate with local user accounts
        try:
            # Check if users directory exists
            if not os.path.exists(USERS_DIR):
                st.error("Login Failed: Invalid credentials.")
                st.info("Use demo@example.com / password for demo access or create a new account.")
                return

            # Find user file by email
            user_found = False
            user_data = None

            for filename in os.listdir(USERS_DIR):
                if filename.endswith('.json'):
                    file_path = os.path.join(USERS_DIR, filename)
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        if data.get('email') == email:
                            user_found = True
                            user_data = data
                            break

            if not user_found or not user_data:
                st.error("Login Failed: User not found.")
                return

            # Verify password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if user_data.get('password_hash') != hashed_password:
                st.error("Login Failed: Incorrect password.")
                return

            # Set session state variables
            st.session_state.logged_in = True
            st.session_state.username = user_data.get('username')
            st.session_state.user_role = user_data.get('role', 'analyst')
            st.session_state.login_time = time.time()

            st.success(f"Logged in successfully as {user_data.get('username')}!")
            st.rerun()
        except Exception as e:
            st.error(f"Login Failed: {e}")
            st.info("Use demo@example.com / password for demo access or create a new account.")

# Sign up page logic
def signup_page():
    """Display and handle the signup page."""
    st.subheader("Create a new account")

    # Create a clean form layout
    with st.form("signup_form"):
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        username = st.text_input("Username")
        submit = st.form_submit_button("Create Account")

    if submit:
        # Validate inputs
        if not email or not password or not username:
            st.error("Please fill in all fields.")
            return

        if password != confirm_password:
            st.error("Passwords do not match.")
            return

        if len(password) < MIN_PASSWORD_LENGTH:
            st.error(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")
            return

        # Create a local user account
        try:
            # Create a user file with hashed password
            user_file = os.path.join(USERS_DIR, f"{username}.json")

            # Check if user already exists
            if os.path.exists(user_file):
                st.error(f"User {username} already exists. Please choose a different username.")
                return

            # Check if email is already in use
            for filename in os.listdir(USERS_DIR):
                if filename.endswith('.json'):
                    file_path = os.path.join(USERS_DIR, filename)
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        if data.get('email') == email:
                            st.error(f"Email {email} is already in use. Please use a different email.")
                            return

            # Hash the password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # Create user data
            user_data = {
                "username": username,
                "email": email,
                "password_hash": hashed_password,
                "role": "analyst",
                "created_at": datetime.now().isoformat()
            }

            # Save user data to file
            with open(user_file, 'w') as f:
                json.dump(user_data, f)

            st.success('Account created successfully! Please log in using your email and password.')
            return
        except Exception as e:
            st.error(f"Error creating account: {e}")

# Logout logic
def logout_user():
    """Log out the current user."""
    if st.session_state.logged_in:
        # Clear all session state variables related to authentication
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.user_role = None
        st.session_state.login_time = None

        # Clear any cached data
        if 'log_data' in st.session_state:
            st.session_state.log_data = None

        st.success("You have been logged out.")
        st.rerun()
    else:
        st.warning("You are not logged in.")

# Function to check if user has required role
def check_user_role(required_role):
    """Check if the user has the required role."""
    if not st.session_state.logged_in:
        return False

    # Check session validity
    if not check_session_validity():
        return False

    # Admin role has access to everything
    if st.session_state.user_role == 'admin':
        return True

    # Check if user role matches required role
    return st.session_state.user_role == required_role
