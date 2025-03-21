from database.connection import get_db_connection
import streamlit as st
from datetime import datetime

def add_facebook_account(user_id, account_name, access_token, page_id=None, expires_at=None):
    """Add a new Facebook account for a user"""
    db = get_db_connection()
    
    # Check if account with same name already exists for this user
    query = """
        SELECT id FROM fb_accounts 
        WHERE user_id = %s AND account_name = %s
    """
    result = db.execute_single_fetch(query, (user_id, account_name))
    
    if result:
        return False, "An account with this name already exists"
    
    # Insert the new account
    query = """
        INSERT INTO fb_accounts (user_id, account_name, access_token, page_id, expires_at)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """
    result = db.execute_single_fetch(
        query, (user_id, account_name, access_token, page_id, expires_at)
    )
    
    if result:
        return True, result[0]
    else:
        return False, "Failed to add Facebook account"

def get_user_facebook_accounts(user_id):
    """Get all Facebook accounts for a user"""
    db = get_db_connection()
    
    query = """
        SELECT id, account_name, page_id, expires_at, created_at
        FROM fb_accounts
        WHERE user_id = %s
        ORDER BY account_name
    """
    results = db.execute_query(query, (user_id,), fetch=True)
    
    accounts = []
    if results:
        for row in results:
            accounts.append({
                "id": row[0],
                "account_name": row[1],
                "page_id": row[2],
                "expires_at": row[3],
                "created_at": row[4]
            })
    
    return accounts

def get_account_by_id(account_id, user_id=None):
    """Get Facebook account by ID, optionally checking user ownership"""
    db = get_db_connection()
    
    query = """
        SELECT id, user_id, account_name, access_token, page_id, expires_at, created_at
        FROM fb_accounts
        WHERE id = %s
    """
    params = (account_id,)
    
    if user_id:
        query += " AND user_id = %s"
        params = (account_id, user_id)
    
    result = db.execute_single_fetch(query, params)
    
    if result:
        return {
            "id": result[0],
            "user_id": result[1],
            "account_name": result[2],
            "access_token": result[3],
            "page_id": result[4],
            "expires_at": result[5],
            "created_at": result[6]
        }
    else:
        return None

def update_facebook_account(account_id, user_id, account_name=None, access_token=None, page_id=None, expires_at=None):
    """Update Facebook account information"""
    db = get_db_connection()
    
    # Get current account info
    account = get_account_by_id(account_id, user_id)
    if not account:
        return False, "Account not found or access denied"
    
    # Build update query dynamically based on provided parameters
    query = "UPDATE fb_accounts SET "
    params = []
    fields = []
    
    if account_name:
        fields.append("account_name = %s")
        params.append(account_name)
    
    if access_token:
        fields.append("access_token = %s")
        params.append(access_token)
    
    if page_id:
        fields.append("page_id = %s")
        params.append(page_id)
    
    if expires_at:
        fields.append("expires_at = %s")
        params.append(expires_at)
    
    if not fields:
        return False, "No updates provided"
    
    query += ", ".join(fields)
    query += " WHERE id = %s AND user_id = %s"
    params.extend([account_id, user_id])
    
    success = db.execute_query(query, params)
    
    if success:
        return True, "Account updated successfully"
    else:
        return False, "Failed to update account"

def delete_facebook_account(account_id, user_id):
    """Delete a Facebook account"""
    db = get_db_connection()
    
    # Verify ownership
    account = get_account_by_id(account_id, user_id)
    if not account:
        return False, "Account not found or access denied"
    
    # Delete the account
    query = "DELETE FROM fb_accounts WHERE id = %s AND user_id = %s"
    success = db.execute_query(query, (account_id, user_id))
    
    if success:
        return True, "Account deleted successfully"
    else:
        return False, "Failed to delete account"

def is_token_expired(account_id):
    """Check if an account's token is expired"""
    db = get_db_connection()
    
    query = "SELECT expires_at FROM fb_accounts WHERE id = %s"
    result = db.execute_single_fetch(query, (account_id,))
    
    if result and result[0]:
        # Check if expiration date is in the past
        return result[0] < datetime.now()
    
    # If no expiration date is set, assume it's not expired
    return False
