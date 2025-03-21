import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database.account_db import (
    get_user_facebook_accounts, 
    add_facebook_account, 
    update_facebook_account,
    delete_facebook_account
)
from facebook.auth import get_facebook_pages, get_long_lived_token
from utils.ui import display_message

def show():
    """Display the accounts management page"""
    st.title("Facebook Accounts")
    
    # Get user accounts
    user_id = st.session_state.user_id
    accounts = get_user_facebook_accounts(user_id)
    
    # Create tabs for account management
    tab1, tab2 = st.tabs(["My Accounts", "Add New Account"])
    
    with tab1:
        if accounts:
            # Display accounts in a table
            account_data = []
            for account in accounts:
                expires_at = "Never" if not account["expires_at"] else account["expires_at"].strftime("%Y-%m-%d %H:%M")
                is_expired = False
                if account["expires_at"] and account["expires_at"] < datetime.now():
                    is_expired = True
                
                account_data.append({
                    "ID": account["id"],
                    "Account Name": account["account_name"],
                    "Page ID": account["page_id"] or "-",
                    "Token Expires": expires_at,
                    "Status": "Expired" if is_expired else "Active"
                })
            
            df = pd.DataFrame(account_data)
            st.dataframe(df, use_container_width=True)
            
            # Account action section
            st.subheader("Account Actions")
            
            # Select account to manage
            selected_account_id = st.selectbox(
                "Select account to manage",
                [(a["id"], a["account_name"]) for a in accounts],
                format_func=lambda x: x[1]
            )[0]
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Edit Account", use_container_width=True):
                    st.session_state.edit_account_id = selected_account_id
                    st.rerun()
            
            with col2:
                if st.button("Refresh Token", use_container_width=True):
                    # This would open a Facebook login/auth flow
                    st.warning("Token refresh functionality requires Facebook OAuth integration")
            
            with col3:
                if st.button("Delete Account", use_container_width=True):
                    st.session_state.delete_account_id = selected_account_id
                    st.rerun()
            
            # Handle edit account
            if "edit_account_id" in st.session_state and st.session_state.edit_account_id:
                edit_account(st.session_state.edit_account_id, user_id)
            
            # Handle delete account
            if "delete_account_id" in st.session_state and st.session_state.delete_account_id:
                confirm_delete_account(st.session_state.delete_account_id, user_id)
        else:
            st.info("You haven't added any Facebook accounts yet. Go to the 'Add New Account' tab to add one.")
    
    with tab2:
        add_account(user_id)

def add_account(user_id):
    """Form to add a new Facebook account"""
    st.subheader("Add New Facebook Account")
    
    with st.form("add_account_form"):
        account_name = st.text_input("Account Name (for your reference)")
        
        # In a real app, you would use Facebook OAuth to get these
        st.markdown("##### Facebook Authentication")
        st.markdown("""
            In a real application, this would be replaced with a Facebook OAuth flow.
            For demonstration purposes, we're allowing manual entry of tokens.
        """)
        
        access_token = st.text_input("Facebook Access Token")
        
        # Option to select a Facebook page
        if access_token:
            st.markdown("If you've entered a valid token, you can select a page:")
            pages = get_facebook_pages(access_token)
            
            if pages:
                page_options = [(p["id"], p["name"]) for p in pages]
                selected_page = st.selectbox(
                    "Select Facebook Page",
                    options=page_options,
                    format_func=lambda x: x[1]
                )
                page_id = selected_page[0] if selected_page else None
            else:
                page_id = st.text_input("Page ID (manual entry)")
                st.warning("Could not fetch pages with provided token. You can enter a Page ID manually.")
        else:
            page_id = st.text_input("Page ID (manual entry)")
        
        submit_button = st.form_submit_button("Add Account")
        
        if submit_button:
            if not account_name:
                st.error("Please enter an account name")
            elif not access_token:
                st.error("Please enter an access token")
            else:
                # Get a long-lived token if possible
                long_token, expires_at = get_long_lived_token(access_token)
                
                # Use original token if we couldn't get a long-lived one
                token_to_use = long_token or access_token
                
                # Add the account
                success, result = add_facebook_account(
                    user_id, account_name, token_to_use, page_id, expires_at
                )
                
                if success:
                    st.success("Facebook account added successfully!")
                    # Clear form and refresh
                    st.rerun()
                else:
                    st.error(f"Failed to add account: {result}")

def edit_account(account_id, user_id):
    """Form to edit an existing Facebook account"""
    from database.account_db import get_account_by_id
    
    account = get_account_by_id(account_id, user_id)
    if not account:
        st.error("Account not found")
        return
    
    st.subheader(f"Edit Account: {account['account_name']}")
    
    with st.form("edit_account_form"):
        account_name = st.text_input("Account Name", value=account["account_name"])
        page_id = st.text_input("Page ID", value=account["page_id"] or "")
        
        submit_button = st.form_submit_button("Update Account")
        cancel_button = st.form_submit_button("Cancel")
        
        if submit_button:
            if not account_name:
                st.error("Please enter an account name")
            else:
                # Update the account
                success, message = update_facebook_account(
                    account_id, user_id, account_name=account_name, page_id=page_id
                )
                
                if success:
                    st.success("Account updated successfully!")
                    # Clear edit state and refresh
                    if "edit_account_id" in st.session_state:
                        del st.session_state.edit_account_id
                    st.rerun()
                else:
                    st.error(f"Failed to update account: {message}")
        
        if cancel_button:
            # Clear edit state and refresh
            if "edit_account_id" in st.session_state:
                del st.session_state.edit_account_id
            st.rerun()

def confirm_delete_account(account_id, user_id):
    """Confirmation dialog for deleting an account"""
    from database.account_db import get_account_by_id
    
    account = get_account_by_id(account_id, user_id)
    if not account:
        st.error("Account not found")
        return
    
    st.warning(f"Are you sure you want to delete the account '{account['account_name']}'?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Yes, Delete", use_container_width=True):
            success, message = delete_facebook_account(account_id, user_id)
            
            if success:
                st.success("Account deleted successfully!")
                # Clear delete state and refresh
                if "delete_account_id" in st.session_state:
                    del st.session_state.delete_account_id
                st.rerun()
            else:
                st.error(f"Failed to delete account: {message}")
    
    with col2:
        if st.button("Cancel", use_container_width=True):
            # Clear delete state and refresh
            if "delete_account_id" in st.session_state:
                del st.session_state.delete_account_id
            st.rerun()
