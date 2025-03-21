import streamlit as st
from database.user_db import authenticate_user, create_user
from utils.ui import display_message, success_button

def show():
    """Display the login page"""
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Add logo and app title with modern styling
        st.markdown("""
            <div style="text-align: center; padding: 1.5rem 0;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Facebook_f_logo_%282019%29.svg/150px-Facebook_f_logo_%282019%29.svg.png" width="80">
                <h1 style="margin-top: 1rem;">Facebook Manager</h1>
                <p style="color: #65676B; font-size: 1.1rem; margin-bottom: 2rem;">Manage all your Facebook accounts in one place</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Create tabs for login and registration
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            # Login form with improved styling
            with st.form("login_form"):
                st.markdown('<div style="height: 20px"></div>', unsafe_allow_html=True)
                
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                
                st.markdown('<div style="height: 10px"></div>', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    submit_button = st.form_submit_button("Login", use_container_width=True)
                
                if submit_button:
                    if username and password:
                        success, result = authenticate_user(username, password)
                        
                        if success:
                            # Set session state
                            st.session_state.authenticated = True
                            st.session_state.user_id = result
                            st.session_state.username = username
                            
                            st.success("Login successful! Redirecting...")
                            st.rerun()
                        else:
                            st.error(f"Login failed: {result}")
                    else:
                        st.error("Please enter both username and password")
        
        with tab2:
            # Registration form with improved styling
            with st.form("register_form"):
                st.markdown('<div style="height: 20px"></div>', unsafe_allow_html=True)
                
                new_username = st.text_input("Username", placeholder="Choose a username")
                email = st.text_input("Email (optional)", placeholder="Enter your email")
                new_password = st.text_input("Password", type="password", placeholder="Create a password")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                
                st.markdown('<div style="height: 10px"></div>', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    submit_button = st.form_submit_button("Create Account", use_container_width=True)
                
                if submit_button:
                    if not new_username or not new_password:
                        st.error("Please enter both username and password")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        success, result = create_user(new_username, new_password, email)
                        
                        if success:
                            st.success("Account created successfully! You can now login.")
                            # Switch to login tab
                            st.rerun()
                        else:
                            st.error(f"Registration failed: {result}")
        
        # Add additional information
        st.markdown("""
            <div style="text-align: center; margin-top: 2rem; padding: 1rem; background-color: #F2F3F5; border-radius: 10px;">
                <p style="color: #65676B; font-size: 0.9rem;">
                    Welcome to the Facebook Manager app. Manage all your Facebook pages,
                    posts, and comments in one centralized dashboard.
                </p>
            </div>
        """, unsafe_allow_html=True)
