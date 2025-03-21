from database.connection import get_db_connection
from passlib.hash import bcrypt
import streamlit as st

def create_user(username, password, email=None):
    """Create a new user in the database"""
    db = get_db_connection()
    
    # Check if username already exists
    query = "SELECT id FROM users WHERE username = %s"
    result = db.execute_single_fetch(query, (username,))
    
    if result:
        return False, "Username already exists"
    
    # Hash the password
    password_hash = bcrypt.hash(password)
    
    # Insert the new user
    query = """
        INSERT INTO users (username, password_hash, email)
        VALUES (%s, %s, %s)
        RETURNING id
    """
    result = db.execute_single_fetch(query, (username, password_hash, email))
    
    if result:
        return True, result[0]
    else:
        return False, "Failed to create user"

def authenticate_user(username, password):
    """Authenticate a user by username and password"""
    db = get_db_connection()
    
    # Get user information
    query = "SELECT id, password_hash FROM users WHERE username = %s"
    result = db.execute_single_fetch(query, (username,))
    
    if not result:
        return False, "User not found"
    
    user_id, password_hash = result
    
    # Verify the password
    if bcrypt.verify(password, password_hash):
        return True, user_id
    else:
        return False, "Invalid password"

def get_user_by_id(user_id):
    """Get user information by ID"""
    db = get_db_connection()
    
    query = "SELECT id, username, email, created_at FROM users WHERE id = %s"
    result = db.execute_single_fetch(query, (user_id,))
    
    if result:
        return {
            "id": result[0],
            "username": result[1],
            "email": result[2],
            "created_at": result[3]
        }
    else:
        return None

def update_password(user_id, current_password, new_password):
    """Update user password"""
    db = get_db_connection()
    
    # Get current password hash
    query = "SELECT password_hash FROM users WHERE id = %s"
    result = db.execute_single_fetch(query, (user_id,))
    
    if not result:
        return False, "User not found"
    
    current_hash = result[0]
    
    # Verify current password
    if not bcrypt.verify(current_password, current_hash):
        return False, "Current password is incorrect"
    
    # Hash the new password
    new_hash = bcrypt.hash(new_password)
    
    # Update the password
    query = "UPDATE users SET password_hash = %s WHERE id = %s"
    success = db.execute_query(query, (new_hash, user_id))
    
    if success:
        return True, "Password updated successfully"
    else:
        return False, "Failed to update password"

def update_user_profile(user_id, email):
    """Update user profile information"""
    db = get_db_connection()
    
    query = "UPDATE users SET email = %s WHERE id = %s"
    success = db.execute_query(query, (email, user_id))
    
    if success:
        return True, "Profile updated successfully"
    else:
        return False, "Failed to update profile"
