import streamlit as st
import pandas as pd
import time
from database.account_db import get_user_facebook_accounts
from database.post_db import count_posts_by_account
from utils.ui import create_card, create_two_columns, glossy_header, metric_card
from utils.session import get_current_account, set_current_account

def show():
    """Display the dashboard page"""
    st.title("Dashboard")
    
    # Get user accounts
    user_id = st.session_state.user_id
    accounts = get_user_facebook_accounts(user_id)
    
    if not accounts:
        st.info("You haven't added any Facebook accounts yet. Go to the Accounts page to add one.")
        if st.button("Add Facebook Account", use_container_width=True):
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
    glossy_header(f"Account Overview: {selected_account['account_name']}", 
                 "Track your social media performance at a glance")
    
    # Create metrics row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        post_count = count_posts_by_account(account_id)
        metric_card("Total Posts", post_count)
    
    with col2:
        # Placeholder for engagement metric
        metric_card("Total Engagement", "Coming Soon")
    
    with col3:
        # Display active since date
        active_since = selected_account["created_at"].strftime("%b %d, %Y")
        metric_card("Active Since", active_since)
    
    # Quick actions section
    st.markdown("### Quick Actions")
    
    col1, col2 = create_two_columns()
    
    with col1:
        if st.button("📝 Create New Post", use_container_width=True):
            st.session_state.navigation = "Posts"
            st.rerun()
    
    with col2:
        if st.button("🔍 View All Posts", use_container_width=True):
            st.session_state.navigation = "Posts"
            st.rerun()
    
    # Activity section
    st.markdown("### Recent Activity")
    
    # Create tabs for different activity views
    tab1, tab2 = st.tabs(["Post Activity", "Engagement"])
    
    with tab1:
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            
            with st.spinner("Loading recent activity..."):
                # Simulated delay for demo purposes
                time.sleep(0.5)
                
                # Show placeholder recent activity
                if post_count > 0:
                    # Placeholder for recent posts
                    st.markdown("#### Recent Posts")
                    st.markdown("• Sample post 1 - Posted 2 hours ago")
                    st.markdown("• Sample post 2 - Posted 1 day ago")
                    st.markdown("• Sample post 3 - Posted 3 days ago")
                else:
                    st.info("No recent posts. Create a new post to see activity here.")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            
            # Placeholder for engagement data
            st.info("Connect your Facebook account to see engagement analytics here.")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Tips and insights section
    st.markdown("### Tips & Insights")
    
    # Create a row of tips
    col1, col2 = st.columns(2)
    
    with col1:
        create_card("🕒 Best Time to Post", 
                   "Posts published between 1-3 PM typically get the highest engagement rates.")
        
        create_card("📊 Content Strategy", 
                   "Mix up your content with 70% valuable content, 20% shared content, and 10% promotional content.")
    
    with col2:
        create_card("📱 Visual Content", 
                   "Posts with images receive 2.3x more engagement than those without visuals.")
        
        create_card("💬 Engagement Tip", 
                   "Respond to comments within 60 minutes to increase customer satisfaction by up to 25%.")
