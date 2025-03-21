import streamlit as st
from pages import login, dashboard, accounts, posts, profile
from utils.session import check_session
from utils.ui import set_page_config

def main():
    """Main application entry point"""
    # Set page configuration
    set_page_config()
    
    # Initialize session state if not already done
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.username = None
    
    # Navigation based on authentication status
    if not st.session_state.authenticated:
        login.show()
    else:
        # Sidebar navigation with improved styling
        with st.sidebar:
            st.markdown("""
                <div style="display: flex; align-items: center; margin-bottom: 20px;">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Facebook_f_logo_%282019%29.svg/150px-Facebook_f_logo_%282019%29.svg.png" width="40" style="margin-right: 10px;">
                    <span style="font-size: 1.5rem; font-weight: 600; color: #1877F2;">FB Manager</span>
                </div>
            """, unsafe_allow_html=True)
            
            # Welcome message
            st.markdown(f"""
                <div style="background: linear-gradient(to right, #E8F0FE, #F2F3F5); padding: 15px; border-radius: 10px; margin-bottom: 25px;">
                    <div style="font-size: 0.9rem; color: #65676B;">Welcome back,</div>
                    <div style="font-size: 1.1rem; font-weight: 600; color: #1C1E21;">{st.session_state.username}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Navigation menu with icons
            st.markdown('<div style="margin-bottom: 30px;">', unsafe_allow_html=True)
            
            # Create a styled navigation menu
            nav_items = {
                "Dashboard": "📊",
                "Accounts": "🔗",
                "Posts": "📝",
                "Profile": "👤"
            }
            
            # Get current page from session state or default to Dashboard
            current_page = st.session_state.get("navigation", "Dashboard")
            
            for page, icon in nav_items.items():
                is_active = current_page == page
                bg_color = "#E7F3FF" if is_active else "transparent"
                text_color = "#1877F2" if is_active else "#1C1E21"
                border_left = "3px solid #1877F2" if is_active else "3px solid transparent"
                
                if st.sidebar.button(
                    f"{icon} {page}",
                    key=f"nav_{page}",
                    use_container_width=True,
                    help=f"Go to {page}"
                ):
                    st.session_state.navigation = page
                    st.rerun()
                
                # Apply custom styling to the last clicked button
                if is_active:
                    st.markdown(f"""
                        <style>
                        div[data-testid="stButton"]:nth-last-child(4) > button {{
                            background-color: {bg_color};
                            color: {text_color};
                            border-left: {border_left};
                            font-weight: 600;
                        }}
                        </style>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Logout button at the bottom
            st.markdown('<div style="position: fixed; bottom: 20px; width: 80%;">', unsafe_allow_html=True)
            if st.button("🚪 Logout", use_container_width=True):
                logout()
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Display the selected page based on navigation state
        page = st.session_state.get("navigation", "Dashboard")
        
        if page == "Dashboard":
            dashboard.show()
        elif page == "Accounts":
            accounts.show()
        elif page == "Posts":
            posts.show()
        elif page == "Profile":
            profile.show()

def logout():
    """Log out the user by clearing session state"""
    # Clear all session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Reset authentication status
    st.session_state.authenticated = False
    st.rerun()

if __name__ == "__main__":
    main()
