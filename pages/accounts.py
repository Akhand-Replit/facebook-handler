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
from utils.ui import display_message, glossy_header, danger_button, success_button

def show():
    """Display the accounts management page"""
    st.title("Facebook Accounts")
    
    # Get user accounts
    user_id = st.session_state.user_id
    accounts = get_user_facebook_accounts(user_id)
    
    # Create tabs for account management
    tab1, tab2 = st.tabs(["My Accounts", "Add New Account"])
    
    with tab1:
        view_accounts(accounts, user_id)
    
    with tab2:
        add_account(user_id)

def view_accounts(accounts, user_id):
    """Display and manage existing accounts"""
    if accounts:
        glossy_header("Your Facebook Accounts", "Manage all your connected accounts")
        
        # Create a styled table for accounts
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        
        # Convert to pandas DataFrame for better display
        account_data = []
        for account in accounts:
            expires_at = "Never" if not account["expires_at"] else account["expires_at"].strftime("%Y-%m-%d %H:%M")
            is_expired = False
            if account["expires_at"] and account["expires_at"] < datetime.now():
                is_expired = True
            
            status_color = "#FF5722" if is_expired else "#4CAF50"
            status_text = "Expired" if is_expired else "Active"
            
            account_data.append({
                "ID": account["id"],
                "Account Name": account["account_name"],
                "Page ID": account["page_id"] or "-",
                "Token Expires": expires_at,
                "Status": f"<span style='color:{status_color}; font-weight:bold;'>{status_text}</span>"
            })
        
        df = pd.DataFrame(account_data)
        
        # Custom styling for the table
        st.markdown("""
        <style>
        .dataframe {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
        }
        .dataframe th {
            text-align: left;
            padding: 12px 15px;
            background-color: #F8F9FA;
            border-bottom: 1px solid #E4E6EB;
            font-weight: 600;
            color: #1877F2;
        }
        .dataframe td {
            text-align: left;
            padding: 12px 15px;
            border-bottom: 1px solid #E4E6EB;
        }
        .dataframe tr:hover {
            background-color: #F2F3F5;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Display the table with HTML formatting enabled
        st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Account action section with improved styling
        st.markdown("### Account Actions")
        
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        
        # Select account to manage
        selected_account_id = st.selectbox(
            "Select account to manage",
            [(a["id"], a["account_name"]) for a in accounts],
            format_func=lambda x: x[1]
        )[0]
        
        # Action buttons with improved styling
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✏️ Edit Account", use_container_width=True):
                st.session_state.edit_account_id = selected_account_id
                st.rerun()
        
        with col2:
            if st.button("🔄 Refresh Token", use_container_width=True):
                # This would open a Facebook login/auth flow
                st.info("Token refresh functionality requires Facebook OAuth integration")
                st.warning("In a production app, this would initiate the Facebook OAuth flow.")
        
        with col3:
            danger_button("🗑️ Delete Account", key=f"delete_account_{selected_account_id}")
            if st.session_state.get(f"delete_account_{selected_account_id}", False):
                st.session_state.delete_account_id = selected_account_id
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Handle edit account
        if "edit_account_id" in st.session_state and st.session_state.edit_account_id:
            edit_account(st.session_state.edit_account_id, user_id)
        
        # Handle delete account
        if "delete_account_id" in st.session_state and st.session_state.delete_account_id:
            confirm_delete_account(st.session_state.delete_account_id, user_id)
    else:
        # No accounts message with nice styling
        st.markdown('<div class="card-container" style="text-align: center; padding: 40px 20px;">', unsafe_allow_html=True)
        st.info("You haven't added any Facebook accounts yet. Go to the 'Add New Account' tab to add one.")
        st.markdown("</div>", unsafe_allow_html=True)

def add_account(user_id):
    """Form to add a new Facebook account"""
    glossy_header("Connect a Facebook Account", "Link your Facebook pages to manage them")
    
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    
    with st.form("add_account_form"):
        account_name = st.text_input("Account Name", 
                                   placeholder="Enter a name for this account (e.g., Business Page)")
        
        # In a real app, you would use Facebook OAuth to get these
        st.markdown("##### Facebook Authentication")
        st.markdown("""
            <div style="background-color: #F8F9FA; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #1877F2;">
                <p style="margin: 0; color: #1C1E21;">
                    In a production application, this would be replaced with a secure Facebook OAuth flow.
                    For demonstration purposes, we're allowing manual entry of tokens.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        access_token = st.text_input("Facebook Access Token", 
                                   placeholder="Enter your Facebook access token",
                                   help="In a real app, this would be obtained securely through OAuth")
        
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
                page_id = st.text_input("Page ID (manual entry)", 
                                      placeholder="Enter your Facebook page ID")
                st.warning("Could not fetch pages with provided token. You can enter a Page ID manually.")
        else:
            page_id = st.text_input("Page ID (manual entry)", 
                                  placeholder="Enter your Facebook page ID")
        
        # Stylish submit button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit_button = st.form_submit_button("Connect Account", use_container_width=True)
        
        if submit_button:
            if not account_name:
                st.error("Please enter an account name")
            elif not access_token:
                st.error("Please enter an access token")
            else:
                with st.spinner("Connecting to Facebook..."):
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
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Tips for Facebook integration
    with st.expander("Tips for Facebook Integration"):
        st.markdown("""
        - **Create a Facebook Developer Account** if you haven't already
        - **Register a Facebook App** in the Facebook Developer Portal
        - **Configure App Settings** to include required permissions
        - **Implement OAuth Flow** for secure token acquisition
        - **Request Extended Permissions** for page management
        
        For more information, visit the [Facebook Developer Documentation](https://developers.facebook.com/docs/pages/).
        """)

def edit_account(account_id, user_id):
    """Form to edit an existing Facebook account"""
    from database.account_db import get_account_by_id
    
    account = get_account_by_id(account_id, user_id)
    if not account:
        st.error("Account not found")
        return
    
    # Create a modal-like effect
    st.markdown('<div class="card-container" style="border: 2px solid #E4E6EB;">', unsafe_allow_html=True)
    
    st.subheader(f"Edit Account: {account['account_name']}")
    
    with st.form("edit_account_form"):
        account_name = st.text_input("Account Name", value=account["account_name"])
        page_id = st.text_input("Page ID", value=account["page_id"] or "")
        
        col1, col2 = st.columns(2)
        
        with col1:
            submit_button = st.form_submit_button("Update Account", use_container_width=True)
        
        with col2:
            cancel_button = st.form_submit_button("Cancel", use_container_width=True)
        
        if submit_button:
            if not account_name:
                st.error("Please enter an account name")
            else:
                with st.spinner("Updating account..."):
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
    
    st.markdown('</div>', unsafe_allow_html=True)

def confirm_delete_account(account_id, user_id):
    """Confirmation dialog for deleting an account"""
    from database.account_db import get_account_by_id
    
    account = get_account_by_id(account_id, user_id)
    if not account:
        st.error("Account not found")
        return
    
    # Create a modal-like effect for the confirmation
    st.markdown('<div class="card-container" style="border: 2px solid #FA383E;">', unsafe_allow_html=True)
    
    st.warning(f"⚠️ Are you sure you want to delete the account '{account['account_name']}'?")
    
    st.markdown("""
    <div style="background-color: #FFF3F0; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #FA383E;">
        <p style="margin: 0; color: #DC3545;">
            This action cannot be undone. All posts, comments, and data associated with this account will be removed from the database.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if danger_button("Yes, Delete Account"):
            with st.spinner("Deleting account..."):
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
    
    st.markdown('</div>', unsafe_allow_html=True)
