import streamlit as st
from database.user_db import authenticate_user, create_user
from utils.ui import display_message

def show():
    """Display the login page"""
    st.title("Facebook Manager")
    
    # Centered column layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Create tabs for login and registration
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.subheader("Login to Your Account")
            
            # Login form
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit_button = st.form_submit_button("Login")
                
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
            st.subheader("Create a New Account")
            
            # Registration form
            with st.form("register_form"):
                new_username = st.text_input("Username")
                new_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                email = st.text_input("Email (optional)")
                
                submit_button = st.form_submit_button("Register")
                
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
