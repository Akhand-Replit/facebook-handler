import streamlit as st
from database.user_db import get_user_by_id, update_password, update_user_profile
from utils.ui import display_message

def show():
    """Display the user profile page"""
    st.title("User Profile")
    
    # Get user information
    user_id = st.session_state.user_id
    user_info = get_user_by_id(user_id)
    
    if not user_info:
        st.error("User information not found")
        return
    
    # Create tabs for different sections
    tab1, tab2 = st.tabs(["Profile Information", "Change Password"])
    
    with tab1:
        profile_section(user_info)
    
    with tab2:
        password_section(user_id)

def profile_section(user_info):
    """Section for viewing and updating profile information"""
    st.subheader("Profile Information")
    
    # Display current information
    st.markdown(f"**Username:** {user_info['username']}")
    st.markdown(f"**Email:** {user_info['email'] or 'Not provided'}")
    st.markdown(f"**Account Created:** {user_info['created_at'].strftime('%B %d, %Y')}")
    
    # Edit profile form
    st.subheader("Update Profile")
    
    with st.form("update_profile_form"):
        email = st.text_input("Email", value=user_info["email"] or "")
        
        submit_button = st.form_submit_button("Update Profile")
        
        if submit_button:
            success, message = update_user_profile(user_info["id"], email)
            
            if success:
                st.success("Profile updated successfully!")
                st.rerun()
            else:
                st.error(f"Failed to update profile: {message}")

def password_section(user_id):
    """Section for changing password"""
    st.subheader("Change Password")
    
    with st.form("change_password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        submit_button = st.form_submit_button("Change Password")
        
        if submit_button:
            if not current_password or not new_password or not confirm_password:
                st.error("Please fill in all password fields")
            elif new_password != confirm_password:
                st.error("New passwords do not match")
            else:
                success, message = update_password(user_id, current_password, new_password)
                
                if success:
                    st.success("Password changed successfully!")
                else:
                    st.error(f"Failed to change password: {message}")
