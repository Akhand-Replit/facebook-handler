import requests
import streamlit as st
import json
from database.account_db import get_account_by_id, update_facebook_account
from datetime import datetime, timedelta

def get_facebook_pages(access_token):
    """Get all Facebook pages associated with an access token"""
    url = f"https://graph.facebook.com/v18.0/me/accounts?access_token={access_token}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('data', [])
        else:
            st.error(f"Error fetching Facebook pages: {response.text}")
            return []
    except Exception as e:
        st.error(f"Error connecting to Facebook: {e}")
        return []

def get_long_lived_token(access_token):
    """Exchange a short-lived token for a long-lived token"""
    # These would be stored in Streamlit secrets
    app_id = st.secrets["fb_app_id"]
    app_secret = st.secrets["fb_app_secret"]
    
    url = f"https://graph.facebook.com/v18.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": access_token
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            new_token = data.get("access_token")
            # Facebook long-lived tokens typically last for 60 days
            expires_in = data.get("expires_in", 60 * 24 * 60 * 60)  # Default to 60 days in seconds
            expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            return new_token, expires_at
        else:
            st.error(f"Error exchanging token: {response.text}")
            return None, None
    except Exception as e:
        st.error(f"Error connecting to Facebook: {e}")
        return None, None

def verify_token(access_token):
    """Verify if a token is valid and get basic information about it"""
    url = f"https://graph.facebook.com/debug_token"
    params = {
        "input_token": access_token,
        "access_token": access_token
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json().get("data", {})
            is_valid = data.get("is_valid", False)
            expires_at = data.get("expires_at")
            
            return is_valid, expires_at
        else:
            return False, None
    except Exception as e:
        st.error(f"Error verifying token: {e}")
        return False, None

def refresh_token_if_needed(account_id, user_id):
    """Check if a token needs refreshing and refresh it if necessary"""
    account = get_account_by_id(account_id, user_id)
    if not account:
        return False, "Account not found"
    
    # If token expires in less than 7 days, refresh it
    now = datetime.now()
    if account["expires_at"] and account["expires_at"] < (now + timedelta(days=7)):
        new_token, expires_at = get_long_lived_token(account["access_token"])
        if new_token:
            success, message = update_facebook_account(
                account_id, user_id, access_token=new_token, expires_at=expires_at
            )
            if success:
                return True, "Token refreshed successfully"
            else:
                return False, message
        else:
            return False, "Failed to refresh token"
    
    return True, "Token is still valid"
