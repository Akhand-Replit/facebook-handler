from database.connection import get_db_connection
import streamlit as st
from datetime import datetime

def save_post(fb_post_id, account_id, content, post_url=None, posted_at=None):
    """Save a Facebook post to the database"""
    db = get_db_connection()
    
    # Check if post already exists
    query = "SELECT id FROM posts WHERE fb_post_id = %s"
    result = db.execute_single_fetch(query, (fb_post_id,))
    
    if result:
        # Update existing post
        post_id = result[0]
        query = """
            UPDATE posts 
            SET content = %s, post_url = %s, posted_at = %s
            WHERE id = %s
        """
        success = db.execute_query(query, (content, post_url, posted_at or datetime.now(), post_id))
        
        if success:
            return True, post_id
        else:
            return False, "Failed to update post"
    else:
        # Insert new post
        query = """
            INSERT INTO posts (fb_post_id, account_id, content, post_url, posted_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """
        result = db.execute_single_fetch(
            query, (fb_post_id, account_id, content, post_url, posted_at or datetime.now())
        )
        
        if result:
            return True, result[0]
        else:
            return False, "Failed to save post"

def get_posts_by_account(account_id, limit=50, offset=0):
    """Get posts for a specific Facebook account"""
    db = get_db_connection()
    
    query = """
        SELECT id, fb_post_id, content, post_url, posted_at, created_at
        FROM posts
        WHERE account_id = %s
        ORDER BY posted_at DESC
        LIMIT %s OFFSET %s
    """
    results = db.execute_query(query, (account_id, limit, offset), fetch=True)
    
    posts = []
    if results:
        for row in results:
            posts.append({
                "id": row[0],
                "fb_post_id": row[1],
                "content": row[2],
                "post_url": row[3],
                "posted_at": row[4],
                "created_at": row[5]
            })
    
    return posts

def get_post_by_id(post_id):
    """Get a post by its ID"""
    db = get_db_connection()
    
    query = """
        SELECT p.id, p.fb_post_id, p.account_id, p.content, p.post_url, p.posted_at, 
               a.user_id, a.account_name
        FROM posts p
        JOIN fb_accounts a ON p.account_id = a.id
        WHERE p.id = %s
    """
    result = db.execute_single_fetch(query, (post_id,))
    
    if result:
        return {
            "id": result[0],
            "fb_post_id": result[1],
            "account_id": result[2],
            "content": result[3],
            "post_url": result[4],
            "posted_at": result[5],
            "user_id": result[6],
            "account_name": result[7]
        }
    else:
        return None

def get_post_by_fb_id(fb_post_id):
    """Get a post by its Facebook ID"""
    db = get_db_connection()
    
    query = "SELECT id FROM posts WHERE fb_post_id = %s"
    result = db.execute_single_fetch(query, (fb_post_id,))
    
    if result:
        return get_post_by_id(result[0])
    else:
        return None

def delete_post(post_id):
    """Delete a post from the database"""
    db = get_db_connection()
    
    # Delete associated comments first
    query = "DELETE FROM comments WHERE post_id = %s"
    db.execute_query(query, (post_id,))
    
    # Delete the post
    query = "DELETE FROM posts WHERE id = %s"
    success = db.execute_query(query, (post_id,))
    
    return success

def count_posts_by_account(account_id):
    """Count the number of posts for an account"""
    db = get_db_connection()
    
    query = "SELECT COUNT(*) FROM posts WHERE account_id = %s"
    result = db.execute_single_fetch(query, (account_id,))
    
    return result[0] if result else 0

def search_posts(account_id, search_term, limit=50, offset=0):
    """Search posts by content for a specific account"""
    db = get_db_connection()
    
    query = """
        SELECT id, fb_post_id, content, post_url, posted_at, created_at
        FROM posts
        WHERE account_id = %s AND content ILIKE %s
        ORDER BY posted_at DESC
        LIMIT %s OFFSET %s
    """
    search_pattern = f"%{search_term}%"
    results = db.execute_query(query, (account_id, search_pattern, limit, offset), fetch=True)
    
    posts = []
    if results:
        for row in results:
            posts.append({
                "id": row[0],
                "fb_post_id": row[1],
                "content": row[2],
                "post_url": row[3],
                "posted_at": row[4],
                "created_at": row[5]
            })
    
    return posts
