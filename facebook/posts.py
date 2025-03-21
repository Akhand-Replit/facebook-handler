import requests
import streamlit as st
from datetime import datetime
from database.account_db import get_account_by_id
from database.post_db import save_post, get_post_by_fb_id
import json

def create_post(account_id, content, link=None, image=None):
    """Create a new post on Facebook"""
    account = get_account_by_id(account_id)
    if not account:
        return False, "Account not found"
    
    access_token = account["access_token"]
    page_id = account["page_id"]
    
    if not page_id:
        return False, "No page ID associated with this account"
    
    url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
    params = {
        "access_token": access_token,
        "message": content
    }
    
    if link:
        params["link"] = link
    
    files = {}
    if image:
        # If image is a file buffer from st.file_uploader
        files = {"source": image}
        url = f"https://graph.facebook.com/v18.0/{page_id}/photos"
    
    try:
        if files:
            response = requests.post(url, params=params, files=files)
        else:
            response = requests.post(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            post_id = data.get("id")
            
            # Get post details to save
            post_details = get_post_details(post_id, access_token)
            
            # Save post to database
            post_url = f"https://facebook.com/{post_id}"
            success, db_post_id = save_post(
                post_id, account_id, content, post_url, datetime.now()
            )
            
            if success:
                return True, post_id
            else:
                return True, "Post created but failed to save locally"
        else:
            return False, f"Error creating post: {response.text}"
    except Exception as e:
        return False, f"Error connecting to Facebook: {e}"

def get_user_posts(account_id, limit=10):
    """Get recent posts for a Facebook account"""
    account = get_account_by_id(account_id)
    if not account:
        return []
    
    access_token = account["access_token"]
    page_id = account["page_id"]
    
    if not page_id:
        return []
    
    url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
    params = {
        "access_token": access_token,
        "fields": "id,message,created_time,permalink_url",
        "limit": limit
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            posts = response.json().get("data", [])
            
            # Process and save posts to database
            for post in posts:
                # Save post to database
                post_id = post.get("id")
                content = post.get("message", "")
                post_url = post.get("permalink_url")
                created_time = post.get("created_time")
                
                # Parse ISO 8601 timestamp
                if created_time:
                    created_time = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                
                save_post(post_id, account_id, content, post_url, created_time)
            
            return posts
        else:
            st.error(f"Error fetching posts: {response.text}")
            return []
    except Exception as e:
        st.error(f"Error connecting to Facebook: {e}")
        return []

def get_post_details(post_id, access_token):
    """Get details of a specific Facebook post"""
    url = f"https://graph.facebook.com/v18.0/{post_id}"
    params = {
        "access_token": access_token,
        "fields": "id,message,created_time,permalink_url"
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching post details: {response.text}")
            return {}
    except Exception as e:
        st.error(f"Error connecting to Facebook: {e}")
        return {}

def update_post(post_id, content, account_id=None):
    """Update an existing Facebook post"""
    # If account_id is provided, fetch the post from database
    if account_id:
        account = get_account_by_id(account_id)
        if not account:
            return False, "Account not found"
        
        access_token = account["access_token"]
    else:
        # Try to get post from database to find account
        db_post = get_post_by_fb_id(post_id)
        if not db_post:
            return False, "Post not found in database"
        
        account = get_account_by_id(db_post["account_id"])
        if not account:
            return False, "Account not found"
        
        access_token = account["access_token"]
    
    url = f"https://graph.facebook.com/v18.0/{post_id}"
    params = {
        "access_token": access_token,
        "message": content
    }
    
    try:
        response = requests.post(url, params=params)
        if response.status_code == 200:
            # Update post in database
            success, _ = save_post(post_id, account["id"], content)
            if success:
                return True, "Post updated successfully"
            else:
                return True, "Post updated on Facebook but failed to update locally"
        else:
            return False, f"Error updating post: {response.text}"
    except Exception as e:
        return False, f"Error connecting to Facebook: {e}"

def delete_post(post_id, account_id=None):
    """Delete a Facebook post"""
    # Similar to update_post, get account info
    if account_id:
        account = get_account_by_id(account_id)
        if not account:
            return False, "Account not found"
        
        access_token = account["access_token"]
    else:
        db_post = get_post_by_fb_id(post_id)
        if not db_post:
            return False, "Post not found in database"
        
        account = get_account_by_id(db_post["account_id"])
        if not account:
            return False, "Account not found"
        
        access_token = account["access_token"]
    
    url = f"https://graph.facebook.com/v18.0/{post_id}"
    params = {
        "access_token": access_token
    }
    
    try:
        response = requests.delete(url, params=params)
        if response.status_code == 200:
            # Delete post from database if exists
            if db_post:
                from database.post_db import delete_post
                delete_post(db_post["id"])
            
            return True, "Post deleted successfully"
        else:
            return False, f"Error deleting post: {response.text}"
    except Exception as e:
        return False, f"Error connecting to Facebook: {e}"
