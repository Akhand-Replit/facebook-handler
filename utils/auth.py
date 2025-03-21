import streamlit as st
from database.user_db import authenticate_user, get_user_by_id

def login_user(username, password):
    """Log in a user and set session state"""
    success, result = authenticate_user(username, password)
    
    if success:
        user_id = result
        user_info = get_user_by_id(user_id)
        
        # Set session state variables
        st.session_state.authenticated = True
        st.session_state.user_id = user_id
        st.session_state.username = user_info["username"]
        
        return True, "Login successful"
    else:
        return False, result

def check_auth():
    """Check if user is authenticated"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        
    return st.session_state.authenticated

def logout_user():
    """Log out a user by clearing session state"""
    # Clear all session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Reset authentication status
    st.session_state.authenticated = False
