import streamlit as st
import pandas as pd
from datetime import datetime
from database.account_db import get_user_facebook_accounts, get_account_by_id
from database.post_db import get_posts_by_account, get_post_by_id, search_posts
from facebook.posts import create_post, update_post, delete_post, get_user_posts
from facebook.comments import get_post_comments, create_comment
from utils.session import get_current_account, set_current_account, get_current_post, set_current_post
from utils.ui import post_card, display_message, glossy_header, danger_button, success_button

def show():
    """Display the posts management page"""
    st.title("Posts")
    
    # Get user accounts
    user_id = st.session_state.user_id
    accounts = get_user_facebook_accounts(user_id)
    
    if not accounts:
        st.info("You haven't added any Facebook accounts yet. Go to the Accounts page to add one.")
        if st.button("Add Facebook Account", use_container_width=True):
            st.session_state.navigation = "Accounts"
            st.rerun()
        return
    
    # Get current account or set to first account
    current_account_id = get_current_account()
    if not current_account_id or not any(a["id"] == current_account_id for a in accounts):
        current_account_id = accounts[0]["id"]
        set_current_account(current_account_id)
    
    # Account selection with improved styling
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    
    selected_account_name = st.selectbox(
        "Select Account",
        [(a["id"], a["account_name"]) for a in accounts],
        index=[i for i, a in enumerate(accounts) if a["id"] == current_account_id][0],
        format_func=lambda x: x[1]
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Update current account if changed
    if selected_account_name[0] != current_account_id:
        current_account_id = selected_account_name[0]
        set_current_account(current_account_id)
        # Clear current post selection when account changes
        set_current_post(None)
    
    # Create tabs for viewing and creating posts
    tab1, tab2 = st.tabs(["View Posts", "Create New Post"])
    
    with tab1:
        view_posts(current_account_id, user_id)
    
    with tab2:
        create_new_post(current_account_id)

def view_posts(account_id, user_id):
    """Display posts for the selected account"""
    glossy_header("Your Posts", "View, edit and manage all your Facebook posts")
    
    # Refresh button and search
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("🔄 Refresh Posts", use_container_width=True):
            # Get posts from Facebook API
            account = get_account_by_id(account_id, user_id)
            if account:
                with st.spinner("Refreshing posts from Facebook..."):
                    posts = get_user_posts(account_id)
                    if posts:
                        st.success(f"Successfully refreshed {len(posts)} posts")
                    else:
                        st.info("No posts found or couldn't connect to Facebook")
    
    with col2:
        search_term = st.text_input("Search posts", placeholder="Enter keywords to search...", 
                                  help="Search for posts containing specific words or phrases")
    
    # Get posts from database
    if search_term:
        posts = search_posts(account_id, search_term)
        if posts:
            st.success(f"Found {len(posts)} posts matching '{search_term}'")
        else:
            st.info(f"No posts found matching '{search_term}'")
    else:
        posts = get_posts_by_account(account_id)
    
    if not posts:
