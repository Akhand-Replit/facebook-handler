from database.connection import get_db_connection
import streamlit as st
from datetime import datetime

def save_comment(fb_comment_id, post_id, content, commented_at=None):
    """Save a Facebook comment to the database"""
    db = get_db_connection()
    
    # Check if comment already exists
    query = "SELECT id FROM comments WHERE fb_comment_id = %s"
    result = db.execute_single_fetch(query, (fb_comment_id,))
    
    if result:
        # Update existing comment
        comment_id = result[0]
        query = """
            UPDATE comments 
            SET content = %s, commented_at = %s
            WHERE id = %s
        """
        success = db.execute_query(query, (content, commented_at or datetime.now(), comment_id))
        
        if success:
            return True, comment_id
        else:
            return False, "Failed to update comment"
    else:
        # Insert new comment
        query = """
            INSERT INTO comments (fb_comment_id, post_id, content, commented_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        result = db.execute_single_fetch(
            query, (fb_comment_id, post_id, content, commented_at or datetime.now())
        )
        
        if result:
            return True, result[0]
        else:
            return False, "Failed to save comment"

def get_comments_by_post(post_id, limit=100, offset=0):
    """Get comments for a specific post"""
    db = get_db_connection()
    
    query = """
        SELECT id, fb_comment_id, content, commented_at, created_at
        FROM comments
        WHERE post_id = %s
        ORDER BY commented_at DESC
        LIMIT %s OFFSET %s
    """
    results = db.execute_query(query, (post_id, limit, offset), fetch=True)
    
    comments = []
    if results:
        for row in results:
            comments.append({
                "id": row[0],
                "fb_comment_id": row[1],
                "content": row[2],
                "commented_at": row[3],
                "created_at": row[4]
            })
    
    return comments

def get_comment_by_id(comment_id):
    """Get a comment by its ID"""
    db = get_db_connection()
    
    query = """
        SELECT c.id, c.fb_comment_id, c.post_id, c.content, c.commented_at, c.created_at,
               p.fb_post_id, p.account_id
        FROM comments c
        JOIN posts p ON c.post_id = p.id
        WHERE c.id = %s
    """
    result = db.execute_single_fetch(query, (comment_id,))
    
    if result:
        return {
            "id": result[0],
            "fb_comment_id": result[1],
            "post_id": result[2],
            "content": result[3],
            "commented_at": result[4],
            "created_at": result[5],
            "fb_post_id": result[6],
            "account_id": result[7]
        }
    else:
        return None

def get_comment_by_fb_id(fb_comment_id):
    """Get a comment by its Facebook ID"""
    db = get_db_connection()
    
    query = "SELECT id FROM comments WHERE fb_comment_id = %s"
    result = db.execute_single_fetch(query, (fb_comment_id,))
    
    if result:
        return get_comment_by_id(result[0])
    else:
        return None

def delete_comment(comment_id):
    """Delete a comment from the database"""
    db = get_db_connection()
    
    query = "DELETE FROM comments WHERE id = %s"
    success = db.execute_query(query, (comment_id,))
    
    return success

def count_comments_by_post(post_id):
    """Count the number of comments for a post"""
    db = get_db_connection()
    
    query = "SELECT COUNT(*) FROM comments WHERE post_id = %s"
    result = db.execute_single_fetch(query, (post_id,))
    
    return result[0] if result else 0

def search_comments(post_id, search_term, limit=100, offset=0):
    """Search comments by content for a specific post"""
    db = get_db_connection()
    
    query = """
        SELECT id, fb_comment_id, content, commented_at, created_at
        FROM comments
        WHERE post_id = %s AND content ILIKE %s
        ORDER BY commented_at DESC
        LIMIT %s OFFSET %s
    """
    search_pattern = f"%{search_term}%"
    results = db.execute_query(query, (post_id, search_pattern, limit, offset), fetch=True)
    
    comments = []
    if results:
        for row in results:
            comments.append({
                "id": row[0],
                "fb_comment_id": row[1],
                "content": row[2],
                "commented_at": row[3],
                "created_at": row[4]
            })
    
    return comments
