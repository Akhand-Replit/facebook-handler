import requests
import streamlit as st
from datetime import datetime
from database.account_db import get_account_by_id
from database.post_db import get_post_by_id, get_post_by_fb_id
from database.comment_db import save_comment, get_comment_by_fb_id

def get_post_comments(post_id, account_id=None):
    """Get comments for a specific Facebook post"""
    # Get post and account info
    if account_id:
        account = get_account_by_id(account_id)
        db_post = get_post_by_id(post_id)
    else:
        db_post = get_post_by_id(post_id)
        if db_post:
            account = get_account_by_id(db_post["account_id"])
        else:
            return [], "Post not found"
    
    if not account:
        return [], "Account not found"
    
    access_token = account["access_token"]
    fb_post_id = db_post["fb_post_id"]
    
    url = f"https://graph.facebook.com/v18.0/{fb_post_id}/comments"
    params = {
        "access_token": access_token,
        "fields": "id,message,created_time",
        "limit": 50
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            comments = response.json().get("data", [])
            
            # Process and save comments to database
            for comment in comments:
                comment_id = comment.get("id")
                content = comment.get("message", "")
                created_time = comment.get("created_time")
                
                # Parse ISO 8601 timestamp
                if created_time:
                    created_time = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                
                save_comment(comment_id, post_id, content, created_time)
            
            return comments, "Comments fetched successfully"
        else:
            return [], f"Error fetching comments: {response.text}"
    except Exception as e:
        return [], f"Error connecting to Facebook: {e}"

def create_comment(post_id, content, account_id=None):
    """Create a new comment on a Facebook post"""
    # Get post and account info
    if account_id:
        account = get_account_by_id(account_id)
        db_post = get_post_by_id(post_id)
    else:
        db_post = get_post_by_id(post_id)
        if db_post:
            account = get_account_by_id(db_post["account_id"])
        else:
            return False, "Post not found"
    
    if not account:
        return False, "Account not found"
    
    access_token = account["access_token"]
    fb_post_id = db_post["fb_post_id"]
    
    url = f"https://graph.facebook.com/v18.0/{fb_post_id}/comments"
    params = {
        "access_token": access_token,
        "message": content
    }
    
    try:
        response = requests.post(url, params=params)
        if response.status_code == 200:
            data = response.json()
            comment_id = data.get("id")
            
            # Save comment to database
            success, db_comment_id = save_comment(
                comment_id, post_id, content, datetime.now()
            )
            
            if success:
                return True, comment_id
            else:
                return True, "Comment created but failed to save locally"
        else:
            return False, f"Error creating comment: {response.text}"
    except Exception as e:
        return False, f"Error connecting to Facebook: {e}"

def update_comment(comment_id, content):
    """Update an existing Facebook comment"""
    # Try to get comment from database to find post and account
    db_comment = get_comment_by_fb_id(comment_id)
    if not db_comment:
        return False, "Comment not found in database"
    
    post_id = db_comment["post_id"]
    db_post = get_post_by_id(post_id)
    if not db_post:
        return False, "Post not found"
    
    account = get_account_by_id(db_post["account_id"])
    if not account:
        return False, "Account not found"
    
    access_token = account["access_token"]
    
    url = f"https://graph.facebook.com/v18.0/{comment_id}"
    params = {
        "access_token": access_token,
        "message": content
    }
    
    try:
        response = requests.post(url, params=params)
        if response.status_code == 200:
            # Update comment in database
            success, _ = save_comment(comment_id, post_id, content)
            if success:
                return True, "Comment updated successfully"
            else:
                return True, "Comment updated on Facebook but failed to update locally"
        else:
            return False, f"Error updating comment: {response.text}"
    except Exception as e:
        return False, f"Error connecting to Facebook: {e}"

def delete_comment(comment_id):
    """Delete a Facebook comment"""
    # Get comment from database
    db_comment = get_comment_by_fb_id(comment_id)
    if not db_comment:
        return False, "Comment not found in database"
    
    post_id = db_comment["post_id"]
    db_post = get_post_by_id(post_id)
    if not db_post:
        return False, "Post not found"
    
    account = get_account_by_id(db_post["account_id"])
    if not account:
        return False, "Account not found"
    
    access_token = account["access_token"]
    
    url = f"https://graph.facebook.com/v18.0/{comment_id}"
    params = {
        "access_token": access_token
    }
    
    try:
        response = requests.delete(url, params=params)
        if response.status_code == 200:
            # Delete comment from database
            from database.comment_db import delete_comment as db_delete_comment
            db_delete_comment(db_comment["id"])
            
            return True, "Comment deleted successfully"
        else:
            return False, f"Error deleting comment: {response.text}"
    except Exception as e:
        return False, f"Error connecting to Facebook: {e}"

def reply_to_comment(comment_id, content):
    """Reply to a Facebook comment"""
    # Get comment from database
    db_comment = get_comment_by_fb_id(comment_id)
    if not db_comment:
        return False, "Comment not found in database"
    
    post_id = db_comment["post_id"]
    db_post = get_post_by_id(post_id)
    if not db_post:
        return False, "Post not found"
    
    account = get_account_by_id(db_post["account_id"])
    if not account:
        return False, "Account not found"
    
    access_token = account["access_token"]
    
    # Reply by creating a comment on the comment
    url = f"https://graph.facebook.com/v18.0/{comment_id}/comments"
    params = {
        "access_token": access_token,
        "message": content
    }
    
    try:
        response = requests.post(url, params=params)
        if response.status_code == 200:
            data = response.json()
            reply_id = data.get("id")
            
            # Save reply as a comment (with parent_id)
            # Note: This would require modifying the comments table to include parent_id
            # For now, just return success
            return True, reply_id
        else:
            return False, f"Error replying to comment: {response.text}"
    except Exception as e:
        return False, f"Error connecting to Facebook: {e}"
