import streamlit as st
import pandas as pd
from datetime import datetime
from database.account_db import get_user_facebook_accounts, get_account_by_id
from database.post_db import get_posts_by_account, get_post_by_id, search_posts
from facebook.posts import create_post, update_post, delete_post, get_user_posts
from facebook.comments import get_post_comments, create_comment
from utils.session import get_current_account, set_current_account, get_current_post, set_current_post
from utils.ui import post_card, display_message

def show():
    """Display the posts management page"""
    st.title("Posts")
    
    # Get user accounts
    user_id = st.session_state.user_id
    accounts = get_user_facebook_accounts(user_id)
    
    if not accounts:
        st.info("You haven't added any Facebook accounts yet. Go to the Accounts page to add one.")
        if st.button("Add Facebook Account"):
            st.session_state.navigation = "Accounts"
            st.rerun()
        return
    
    # Get current account or set to first account
    current_account_id = get_current_account()
    if not current_account_id or not any(a["id"] == current_account_id for a in accounts):
        current_account_id = accounts[0]["id"]
        set_current_account(current_account_id)
    
    # Account selection
    selected_account_name = st.selectbox(
        "Select Account",
        [(a["id"], a["account_name"]) for a in accounts],
        index=[i for i, a in enumerate(accounts) if a["id"] == current_account_id][0],
        format_func=lambda x: x[1]
    )
    
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
    st.subheader("Posts")
    
    # Refresh button and search
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("Refresh Posts", use_container_width=True):
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
        search_term = st.text_input("Search posts", placeholder="Enter keywords...")
    
    # Get posts from database
    if search_term:
        posts = search_posts(account_id, search_term)
    else:
        posts = get_posts_by_account(account_id)
    
    if not posts:
        st.info("No posts found. Create a new post or refresh to fetch posts from Facebook.")
        return
    
    # Display posts
    for post in posts:
        # Post container
        with st.container():
            col1, col2 = st.columns([5, 1])
            
            with col1:
                # Format date
                date_str = post["posted_at"].strftime("%B %d, %Y at %I:%M %p") if post["posted_at"] else "Unknown date"
                
                # Display post content
                st.markdown(f"### Post from {date_str}")
                st.markdown(post["content"])
                
                # Post URL if available
                if post["post_url"]:
                    st.markdown(f"[View on Facebook]({post['post_url']})")
            
            with col2:
                # Action buttons
                if st.button("Edit", key=f"edit_{post['id']}", use_container_width=True):
                    st.session_state.edit_post_id = post["id"]
                    st.rerun()
                
                if st.button("Delete", key=f"delete_{post['id']}", use_container_width=True):
                    st.session_state.delete_post_id = post["id"]
                    st.rerun()
                
                if st.button("Comments", key=f"comments_{post['id']}", use_container_width=True):
                    st.session_state.view_comments_post_id = post["id"]
                    st.rerun()
            
            st.markdown("---")
    
    # Handle edit post
    if "edit_post_id" in st.session_state and st.session_state.edit_post_id:
        edit_post(st.session_state.edit_post_id)
    
    # Handle delete post
    if "delete_post_id" in st.session_state and st.session_state.delete_post_id:
        confirm_delete_post(st.session_state.delete_post_id)
    
    # Handle view comments
    if "view_comments_post_id" in st.session_state and st.session_state.view_comments_post_id:
        view_post_comments(st.session_state.view_comments_post_id)

def create_new_post(account_id):
    """Form to create a new post"""
    st.subheader("Create New Post")
    
    with st.form("create_post_form"):
        content = st.text_area("Post Content", height=150)
        
        col1, col2 = st.columns(2)
        
        with col1:
            link = st.text_input("Link (optional)")
        
        with col2:
            uploaded_image = st.file_uploader("Image (optional)", type=["jpg", "jpeg", "png"])
        
        submit_button = st.form_submit_button("Post to Facebook")
        
        if submit_button:
            if not content:
                st.error("Please enter post content")
            else:
                with st.spinner("Posting to Facebook..."):
                    success, result = create_post(account_id, content, link, uploaded_image)
                    
                    if success:
                        st.success("Post created successfully!")
                        # Clear form
                        st.rerun()
                    else:
                        st.error(f"Failed to create post: {result}")

def edit_post(post_id):
    """Form to edit an existing post"""
    post = get_post_by_id(post_id)
    if not post:
        st.error("Post not found")
        return
    
    st.subheader("Edit Post")
    
    with st.form("edit_post_form"):
        content = st.text_area("Post Content", value=post["content"], height=150)
        
        submit_button = st.form_submit_button("Update Post")
        cancel_button = st.form_submit_button("Cancel")
        
        if submit_button:
            if not content:
                st.error("Please enter post content")
            else:
                with st.spinner("Updating post on Facebook..."):
                    success, message = update_post(post["fb_post_id"], content, post["account_id"])
                    
                    if success:
                        st.success("Post updated successfully!")
                        # Clear edit state and refresh
                        if "edit_post_id" in st.session_state:
                            del st.session_state.edit_post_id
                        st.rerun()
                    else:
                        st.error(f"Failed to update post: {message}")
        
        if cancel_button:
            # Clear edit state and refresh
            if "edit_post_id" in st.session_state:
                del st.session_state.edit_post_id
            st.rerun()

def confirm_delete_post(post_id):
    """Confirmation dialog for deleting a post"""
    post = get_post_by_id(post_id)
    if not post:
        st.error("Post not found")
        return
    
    st.warning("Are you sure you want to delete this post? This action cannot be undone.")
    
    # Show post snippet
    st.markdown(f"**Post snippet:** {post['content'][:100]}...")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Yes, Delete", use_container_width=True):
            with st.spinner("Deleting post from Facebook..."):
                success, message = delete_post(post["fb_post_id"], post["account_id"])
                
                if success:
                    st.success("Post deleted successfully!")
                    # Clear delete state and refresh
                    if "delete_post_id" in st.session_state:
                        del st.session_state.delete_post_id
                    st.rerun()
                else:
                    st.error(f"Failed to delete post: {message}")
    
    with col2:
        if st.button("Cancel", use_container_width=True):
            # Clear delete state and refresh
            if "delete_post_id" in st.session_state:
                del st.session_state.delete_post_id
            st.rerun()

def view_post_comments(post_id):
    """View and manage comments for a post"""
    post = get_post_by_id(post_id)
    if not post:
        st.error("Post not found")
        return
    
    st.subheader("Post Comments")
    
    # Display post content
    st.markdown("### Original Post")
    st.markdown(post["content"])
    st.markdown("---")
    
    # Refresh comments button
    if st.button("Refresh Comments", use_container_width=False):
        with st.spinner("Fetching comments from Facebook..."):
            comments, message = get_post_comments(post_id)
            if comments:
                st.success(f"Successfully fetched {len(comments)} comments")
            else:
                st.info(message or "No comments found")
    
    # Get comments from database
    from database.comment_db import get_comments_by_post
    comments = get_comments_by_post(post_id)
    
    # Add new comment form
    with st.form("add_comment_form"):
        comment_content = st.text_area("Add a comment", height=100)
        submit_button = st.form_submit_button("Post Comment")
        
        if submit_button:
            if not comment_content:
                st.error("Please enter comment content")
            else:
                with st.spinner("Posting comment to Facebook..."):
                    success, result = create_comment(post_id, comment_content)
                    
                    if success:
                        st.success("Comment posted successfully!")
                        # Refresh
                        st.rerun()
                    else:
                        st.error(f"Failed to post comment: {result}")
    
    # Display comments
    st.subheader(f"Comments ({len(comments)})")
    
    if not comments:
        st.info("No comments found for this post.")
    else:
        for comment in comments:
            # Format date
            date_str = comment["commented_at"].strftime("%B %d, %Y at %I:%M %p") if comment["commented_at"] else "Unknown date"
            
            with st.container():
                st.markdown(f"**Comment on {date_str}**")
                st.markdown(comment["content"])
                
                col1, col2, col3 = st.columns([1, 1, 2])
                
                with col1:
                    if st.button("Edit", key=f"edit_comment_{comment['id']}", use_container_width=True):
                        st.session_state.edit_comment_id = comment["id"]
                        st.rerun()
                
                with col2:
                    if st.button("Delete", key=f"delete_comment_{comment['id']}", use_container_width=True):
                        st.session_state.delete_comment_id = comment["id"]
                        st.rerun()
                
                st.markdown("---")
    
    # Back button
    if st.button("Back to Posts"):
        if "view_comments_post_id" in st.session_state:
            del st.session_state.view_comments_post_id
        st.rerun()
    
    # Comment edit/delete functionality would be implemented similarly to posts
