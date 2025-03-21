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
        st.markdown('<div class="card-container" style="text-align: center; padding: 40px 20px;">', unsafe_allow_html=True)
        st.info("No posts found. Create a new post or refresh to fetch posts from Facebook.")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    # Display posts with improved styling
    for post in posts:
        # Post container
        st.markdown('<div class="post-card">', unsafe_allow_html=True)
        
        # Format date for display
        date_str = post["posted_at"].strftime("%B %d, %Y at %I:%M %p") if post["posted_at"] else "Unknown date"
        
        col1, col2 = st.columns([5, 1])
        
        with col1:
            # Post header
            st.markdown(f"<div class='post-header'><div class='post-author'>Post Update</div><div class='post-time'>{date_str}</div></div>", unsafe_allow_html=True)
            
            # Post content
            st.markdown(f"<div class='post-content'>{post['content']}</div>", unsafe_allow_html=True)
            
            # Post URL if available
            if post["post_url"]:
                st.markdown(f"<a href='{post['post_url']}' target='_blank' style='color: #1877F2; text-decoration: none; font-size: 0.9rem;'><i>View on Facebook</i></a>", unsafe_allow_html=True)
        
        with col2:
            # Action buttons stacked vertically with improved styling
            st.markdown("<div style='display: flex; flex-direction: column; gap: 8px;'>", unsafe_allow_html=True)
            
            if st.button("✏️ Edit", key=f"edit_{post['id']}", use_container_width=True):
                st.session_state.edit_post_id = post["id"]
                st.rerun()
            
            if st.button("💬 Comments", key=f"comments_{post['id']}", use_container_width=True):
                st.session_state.view_comments_post_id = post["id"]
                st.rerun()
            
            # Danger button for delete
            danger_button("🗑️ Delete", key=f"delete_{post['id']}")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
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
    glossy_header("Create New Post", "Share updates with your audience")
    
    # Stylish form container
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    
    with st.form("create_post_form"):
        content = st.text_area("What's on your mind?", height=150, 
                               placeholder="Write something to share with your audience...")
        
        col1, col2 = st.columns(2)
        
        with col1:
            link = st.text_input("Add a link (optional)", 
                                placeholder="https://")
        
        with col2:
            uploaded_image = st.file_uploader("Add an image (optional)", 
                                            type=["jpg", "jpeg", "png"])
        
        # Preview section
        if content or link or uploaded_image:
            st.markdown("### Preview")
            preview_container = st.empty()
            
            preview_html = f"""
            <div style="border: 1px solid #E4E6EB; border-radius: 8px; padding: 15px; background-color: #F8F9FA;">
                <div style="font-weight: bold; margin-bottom: 10px;">Your post will look like this:</div>
                <div style="margin-bottom: 10px;">{content}</div>
                {f'<div style="color: #385898; font-weight: 600;">{link}</div>' if link else ''}
                {f'<div style="color: #65676B; font-style: italic; margin-top: 10px;">Image attached: {uploaded_image.name}</div>' if uploaded_image else ''}
            </div>
            """
            
            preview_container.markdown(preview_html, unsafe_allow_html=True)
        
        # Submit button with modern styling
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit_button = st.form_submit_button("🚀 Post to Facebook", use_container_width=True)
        
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
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Tips for effective posting
    with st.expander("Tips for more engaging posts"):
        st.markdown("""
        - **Use images or videos**: Posts with visual content get 2.3x more engagement
        - **Ask questions**: Encourage your audience to comment
        - **Keep it concise**: The ideal post length is between 40-80 characters
        - **Use hashtags sparingly**: 1-2 relevant hashtags can increase reach
        - **Post at optimal times**: Typically weekdays between 1pm-3pm
        """)

def edit_post(post_id):
    """Form to edit an existing post"""
    post = get_post_by_id(post_id)
    if not post:
        st.error("Post not found")
        return
    
    # Create a modal-like effect
    st.markdown('<div class="card-container" style="border: 2px solid #E4E6EB;">', unsafe_allow_html=True)
    
    st.subheader("Edit Post")
    
    with st.form("edit_post_form"):
        content = st.text_area("Post Content", value=post["content"], height=150)
        
        col1, col2 = st.columns(2)
        
        with col1:
            submit_button = st.form_submit_button("Update Post", use_container_width=True)
        
        with col2:
            cancel_button = st.form_submit_button("Cancel", use_container_width=True)
        
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
    
    st.markdown('</div>', unsafe_allow_html=True)

def confirm_delete_post(post_id):
    """Confirmation dialog for deleting a post"""
    post = get_post_by_id(post_id)
    if not post:
        st.error("Post not found")
        return
    
    # Create a modal-like effect for the confirmation
    st.markdown('<div class="card-container" style="border: 2px solid #FA383E;">', unsafe_allow_html=True)
    
    st.warning("⚠️ Delete Confirmation")
    
    st.markdown("Are you sure you want to delete this post? This action cannot be undone.")
    
    # Show post snippet
    st.markdown('<div style="background-color: #F8F9FA; padding: 15px; border-radius: 8px; margin: 15px 0;">', unsafe_allow_html=True)
    st.markdown(f"**Post content:** {post['content'][:100]}{'...' if len(post['content']) > 100 else ''}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if danger_button("Yes, Delete Post"):
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
    
    st.markdown('</div>', unsafe_allow_html=True)

def view_post_comments(post_id):
    """View and manage comments for a post"""
    post = get_post_by_id(post_id)
    if not post:
        st.error("Post not found")
        return
    
    # Create a comments page view
    glossy_header("Post Comments", "View and respond to engagement")
    
    # Display post content in a card
    st.markdown('<div class="post-card">', unsafe_allow_html=True)
    
    # Format date
    date_str = post["posted_at"].strftime("%B %d, %Y at %I:%M %p") if post["posted_at"] else "Unknown date"
    
    # Post header
    st.markdown(f"<div class='post-header'><div class='post-author'>Original Post</div><div class='post-time'>{date_str}</div></div>", unsafe_allow_html=True)
    
    # Post content
    st.markdown(f"<div class='post-content'>{post['content']}</div>", unsafe_allow_html=True)
    
    # Post URL if available
    if post["post_url"]:
        st.markdown(f"<a href='{post['post_url']}' target='_blank' style='color: #1877F2; text-decoration: none; font-size: 0.9rem;'><i>View on Facebook</i></a>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Refresh comments button
    if st.button("🔄 Refresh Comments", use_container_width=False):
        with st.spinner("Fetching comments from Facebook..."):
            comments, message = get_post_comments(post_id)
            if comments:
                st.success(f"Successfully fetched {len(comments)} comments")
            else:
                st.info(message or "No comments found")
    
    # Get comments from database
    from database.comment_db import get_comments_by_post
    comments = get_comments_by_post(post_id)
    
    # Add new comment form in a card
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    
    with st.form("add_comment_form"):
        st.markdown("### Add a Comment")
        comment_content = st.text_area("Write a comment", height=100, 
                                      placeholder="Share your thoughts...")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit_button = st.form_submit_button("Post Comment", use_container_width=True)
        
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
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display comments with improved styling
    st.subheader(f"Comments ({len(comments)})")
    
    if not comments:
        st.markdown('<div class="card-container" style="text-align: center; padding: 30px 20px;">', unsafe_allow_html=True)
        st.info("No comments found for this post.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        for comment in comments:
            # Format date
            date_str = comment["commented_at"].strftime("%B %d, %Y at %I:%M %p") if comment["commented_at"] else "Unknown date"
            
            # Comment container with modern styling
            st.markdown('<div class="comment-container">', unsafe_allow_html=True)
            
            # Comment author and timestamp
            st.markdown(f"<div class='comment-author'>User Comment</div>", unsafe_allow_html=True)
            
            # Comment content
            st.markdown(f"<div class='comment-content'>{comment['content']}</div>", unsafe_allow_html=True)
            
            # Comment timestamp
            st.markdown(f"<div class='comment-time'>{date_str}</div>", unsafe_allow_html=True)
            
            # Comment actions
            col1, col2, col3 = st.columns([1, 1, 3])
            
            with col1:
                if st.button("✏️ Edit", key=f"edit_comment_{comment['id']}", use_container_width=True):
                    st.session_state.edit_comment_id = comment["id"]
                    st.rerun()
            
            with col2:
                danger_button("🗑️ Delete", key=f"delete_comment_{comment['id']}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Back button with improved styling
    st.markdown('<div style="margin-top: 20px;">', unsafe_allow_html=True)
    if st.button("← Back to Posts", use_container_width=False):
        if "view_comments_post_id" in st.session_state:
            del st.session_state.view_comments_post_id
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
