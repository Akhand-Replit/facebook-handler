import streamlit as st
from pages import login, dashboard, accounts, posts, profile
from utils.session import check_session
from utils.ui import set_page_config

def main():
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
        # Sidebar navigation
        with st.sidebar:
            st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Facebook_f_logo_%282019%29.svg/150px-Facebook_f_logo_%282019%29.svg.png", width=50)
            st.title("FB Manager")
            
            st.markdown(f"Welcome, **{st.session_state.username}**!")
            
            page = st.radio(
                "Navigation",
                ["Dashboard", "Accounts", "Posts", "Profile"],
                key="navigation"
            )
            
            st.button("Logout", on_click=logout)
        
        # Display the selected page
        if page == "Dashboard":
            dashboard.show()
        elif page == "Accounts":
            accounts.show()
        elif page == "Posts":
            posts.show()
        elif page == "Profile":
            profile.show()

def logout():
    # Clear session state and reset authentication
    for key in st.session_state.keys():
        del st.session_state[key]
    st.session_state.authenticated = False
    st.rerun()

if __name__ == "__main__":
    main()
