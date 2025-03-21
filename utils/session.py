import streamlit as st

def init_session_state():
    """Initialize session state variables if they don't exist"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    
    if "username" not in st.session_state:
        st.session_state.username = None
    
    if "current_account_id" not in st.session_state:
        st.session_state.current_account_id = None
    
    if "current_post_id" not in st.session_state:
        st.session_state.current_post_id = None

def check_session():
    """Check if session is valid and user is authenticated"""
    init_session_state()
    return st.session_state.authenticated

def set_current_account(account_id):
    """Set the current account ID in session state"""
    st.session_state.current_account_id = account_id

def get_current_account():
    """Get the current account ID from session state"""
    if "current_account_id" in st.session_state:
        return st.session_state.current_account_id
    return None

def set_current_post(post_id):
    """Set the current post ID in session state"""
    st.session_state.current_post_id = post_id

def get_current_post():
    """Get the current post ID from session state"""
    if "current_post_id" in st.session_state:
        return st.session_state.current_post_id
    return None

def clear_current_selection():
    """Clear current selections in session state"""
    if "current_account_id" in st.session_state:
        st.session_state.current_account_id = None
    
    if "current_post_id" in st.session_state:
        st.session_state.current_post_id = None
