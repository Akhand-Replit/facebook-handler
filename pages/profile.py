import streamlit as st
from database.user_db import get_user_by_id, update_password, update_user_profile
from utils.ui import display_message, glossy_header, success_button

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
    glossy_header("Profile Information", "View and update your account details")
    
    # Display current information in a card
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div style="font-size: 1.1rem; font-weight: 600; color: #65676B; margin-bottom: 8px;">Username</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size: 1.2rem; color: #1C1E21;">{user_info["username"]}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div style="font-size: 1.1rem; font-weight: 600; color: #65676B; margin-bottom: 8px;">Email</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size: 1.2rem; color: #1C1E21;">{user_info["email"] or "Not provided"}</div>', unsafe_allow_html=True)
    
    st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div style="font-size: 1.1rem; font-weight: 600; color: #65676B; margin-bottom: 8px;">Account Created</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size: 1.2rem; color: #1C1E21;">{user_info["created_at"].strftime("%B %d, %Y")}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Edit profile form with improved styling
    st.markdown("### Update Profile")
    
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    
    with st.form("update_profile_form"):
        email = st.text_input("Email", value=user_info["email"] or "", 
                            placeholder="Enter your email address")
        
        # Add more profile fields as needed
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit_button = st.form_submit_button("Save Changes", use_container_width=True)
        
        if submit_button:
            with st.spinner("Updating profile..."):
                success, message = update_user_profile(user_info["id"], email)
                
                if success:
                    st.success("Profile updated successfully!")
                    st.rerun()
                else:
                    st.error(f"Failed to update profile: {message}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def password_section(user_id):
    """Section for changing password"""
    glossy_header("Change Password", "Keep your account secure with a strong password")
    
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    
    with st.form("change_password_form"):
        current_password = st.text_input("Current Password", type="password", 
                                       placeholder="Enter your current password")
        
        st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
        
        new_password = st.text_input("New Password", type="password", 
                                   placeholder="Enter your new password")
        
        confirm_password = st.text_input("Confirm New Password", type="password", 
                                       placeholder="Confirm your new password")
        
        # Password strength indicator
        if new_password:
            strength = check_password_strength(new_password)
            if strength == "strong":
                st.markdown("""
                    <div style="display: flex; align-items: center; margin-top: 10px;">
                        <div style="width: 100%; height: 6px; background-color: #E4E6EB; border-radius: 3px;">
                            <div style="width: 100%; height: 6px; background-color: #4CAF50; border-radius: 3px;"></div>
                        </div>
                        <div style="margin-left: 10px; color: #4CAF50; font-weight: 600;">Strong</div>
                    </div>
                """, unsafe_allow_html=True)
            elif strength == "medium":
                st.markdown("""
                    <div style="display: flex; align-items: center; margin-top: 10px;">
                        <div style="width: 100%; height: 6px; background-color: #E4E6EB; border-radius: 3px;">
                            <div style="width: 66%; height: 6px; background-color: #FFC107; border-radius: 3px;"></div>
                        </div>
                        <div style="margin-left: 10px; color: #FFC107; font-weight: 600;">Medium</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div style="display: flex; align-items: center; margin-top: 10px;">
                        <div style="width: 100%; height: 6px; background-color: #E4E6EB; border-radius: 3px;">
                            <div style="width: 33%; height: 6px; background-color: #F44336; border-radius: 3px;"></div>
                        </div>
                        <div style="margin-left: 10px; color: #F44336; font-weight: 600;">Weak</div>
                    </div>
                """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit_button = st.form_submit_button("Change Password", use_container_width=True)
        
        if submit_button:
            if not current_password or not new_password or not confirm_password:
                st.error("Please fill in all password fields")
            elif new_password != confirm_password:
                st.error("New passwords do not match")
            elif check_password_strength(new_password) == "weak":
                st.warning("Your password is weak. Consider using a stronger password with a mix of letters, numbers, and special characters.")
            else:
                with st.spinner("Updating password..."):
                    success, message = update_password(user_id, current_password, new_password)
                    
                    if success:
                        st.success("Password changed successfully!")
                    else:
                        st.error(f"Failed to change password: {message}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Password tips
    with st.expander("Password Security Tips"):
        st.markdown("""
        - Use a mix of uppercase and lowercase letters, numbers, and special characters
        - Make your password at least 12 characters long
        - Avoid using personal information like your name or birthdate
        - Don't reuse passwords across different sites
        - Consider using a password manager to generate and store secure passwords
        """)

def check_password_strength(password):
    """Check the strength of a password"""
    # Simple password strength check
    if len(password) < 8:
        return "weak"
    
    # Check for mixture of character types
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    
    # Count the character types
    char_types = sum([has_upper, has_lower, has_digit, has_special])
    
    if len(password) >= 12 and char_types >= 3:
        return "strong"
    elif len(password) >= 8 and char_types >= 2:
        return "medium"
    else:
        return "weak"
