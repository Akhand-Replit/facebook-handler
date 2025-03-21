import streamlit as st

def set_page_config():
    """Set the page configuration for the app"""
    st.set_page_config(
        page_title="Facebook Manager",
        page_icon="📱",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom styles
    apply_custom_styles()

def apply_custom_styles():
    """Apply custom CSS styles to the app"""
    st.markdown("""
        <style>
        /* Main theme colors */
        :root {
            --primary-color: #4267B2;
            --secondary-color: #898F9C;
            --background-color: #F0F2F5;
            --text-color: #1C1E21;
            --accent-color: #1877F2;
        }
        
        /* Body styles */
        .stApp {
            background-color: var(--background-color);
        }
        
        /* Header styles */
        .stHeader {
            background-color: var(--primary-color);
            color: white;
        }
        
        /* Sidebar styles */
        .css-1d391kg {
            background-color: white;
        }
        
        /* Button styles */
        .stButton>button {
            background-color: var(--primary-color);
            color: white;
            border-radius: 20px;
            border: none;
            padding: 5px 15px;
            font-weight: bold;
        }
        
        .stButton>button:hover {
            background-color: var(--accent-color);
        }
        
        /* Card styles */
        .css-1r6slb0 {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
            padding: 10px;
        }
        
        /* Input field styles */
        .stTextInput>div>div>input {
            border-radius: 20px;
            border: 1px solid #ddd;
        }
        
        /* Text area styles */
        .stTextArea>div>div>textarea {
            border-radius: 10px;
            border: 1px solid #ddd;
        }
        
        /* Make the app feel more like Facebook */
        h1, h2, h3 {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: var(--primary-color);
        }
        
        /* Post card styles */
        .post-card {
            background-color: white;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        
        .post-header {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .post-author {
            font-weight: bold;
            margin-left: 10px;
        }
        
        .post-content {
            margin-bottom: 10px;
        }
        
        .post-actions {
            display: flex;
            border-top: 1px solid #ddd;
            padding-top: 10px;
        }
        
        .post-action {
            flex: 1;
            text-align: center;
            color: var(--secondary-color);
            padding: 5px 0;
            cursor: pointer;
        }
        
        .post-action:hover {
            background-color: rgba(0,0,0,0.05);
            border-radius: 4px;
        }
        </style>
    """, unsafe_allow_html=True)

def post_card(title, content, date, actions=None):
    """Create a Facebook-style post card"""
    html = f"""
    <div class="post-card">
        <div class="post-header">
            <div class="post-author">{title}</div>
        </div>
        <div class="post-content">
            {content}
        </div>
        <div class="post-date">
            {date}
        </div>
    """
    
    if actions:
        html += '<div class="post-actions">'
        for action in actions:
            html += f'<div class="post-action">{action}</div>'
        html += '</div>'
    
    html += '</div>'
    
    st.markdown(html, unsafe_allow_html=True)

def display_message(message_type, message):
    """Display a message with the appropriate styling"""
    if message_type == "success":
        st.success(message)
    elif message_type == "error":
        st.error(message)
    elif message_type == "info":
        st.info(message)
    elif message_type == "warning":
        st.warning(message)

def create_three_columns():
    """Create three columns with good spacing"""
    return st.columns([1, 2, 1])

def create_two_columns():
    """Create two equal columns"""
    return st.columns(2)

def create_card(title, content):
    """Create a card with a title and content"""
    with st.container():
        st.markdown(f"### {title}")
        st.markdown(f"{content}")
        st.markdown("---")
