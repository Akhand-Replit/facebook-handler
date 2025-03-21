import streamlit as st
import pandas as pd
import time
from database.account_db import get_user_facebook_accounts
from database.post_db import count_posts_by_account
from utils.ui import create_card, create_two_columns
from utils.session import get_current_account, set_current_account

def show():
    """Display the dashboard page"""
    st.title("Dashboard")
    
    # Get user accounts
    user_id = st.session_state.user_id
    accounts = get_user_facebook_accounts(user_id)
    
    if not accounts:
        st.info("You haven't added any Facebook accounts yet. Go to the Accounts page to add one.")
        if st.button("Add Facebook Account"):
            st.session_state.navigation = "Accounts"
            st.rerun()
        return
    
    # Account selection
    selected_account_name = st.selectbox(
        "Select Account",
        [account["account_name"] for account in accounts],
        index=0
    )
    
    # Find the selected account
    selected_account = next(
        (account for account in accounts if account["account_name"] == selected_account_name),
        accounts[0]
    )
    
    # Set current account in session state
    account_id = selected_account["id"]
    set_current_account(account_id)
    
    # Display account information and metrics
    st.subheader(f"Account: {selected_account['account_name']}")
    
    # Create metrics row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        post_count = count_posts_by_account(account_id)
        st.metric(label="Total Posts", value=post_count)
    
    with col2:
        # Placeholder for engagement metric
        st.metric(label="Total Engagement", value="--")
    
    with col3:
        # Placeholder for another metric
        st.metric(label="Active Since", value=selected_account["created_at"].strftime("%b %d, %Y"))
    
    # Activity section
    st.subheader("Recent Activity")
    
    # Placeholder for recent activity
    with st.spinner("Loading recent activity..."):
        # Simulated delay for demo purposes
        time.sleep(0.5)
        
        # Show placeholder recent activity
        st.info("Connect your Facebook account to see recent activity here.")
    
    # Quick actions section
    st.subheader("Quick Actions")
    
    col1, col2 = create_two_columns()
    
    with col1:
        if st.button("Create New Post", use_container_width=True):
            st.session_state.navigation = "Posts"
            st.rerun()
    
    with col2:
        if st.button("View Posts", use_container_width=True):
            st.session_state.navigation = "Posts"
            st.rerun()
    
    # Tips and insights section
    st.subheader("Tips & Insights")
    
    tips = [
        "Post during peak hours to maximize engagement.",
        "Use images in your posts to increase interactions.",
        "Respond to comments promptly to build community.",
        "Share a mix of content types to keep your audience engaged."
    ]
    
    for tip in tips:
        create_card("Tip", tip)
