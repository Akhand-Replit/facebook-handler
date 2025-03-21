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
        /* Main theme colors - Modern Facebook palette with glossy feel */
        :root {
            --primary-color: #1877F2;
            --secondary-color: #3C5A99;
            --background-color: #F0F2F5;
            --card-bg-color: #FFFFFF;
            --text-color: #1C1E21;
            --accent-color: #42B72A;
            --danger-color: #FA383E;
            --border-radius: 10px;
            --box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
        }
        
        /* Global styles */
        .stApp {
            background-color: var(--background-color);
        }
        
        /* Make text sharper */
        * {
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }
        
        /* Header styles */
        h1, h2, h3, h4, h5 {
            font-family: 'SF Pro Display', 'Segoe UI', Roboto, Helvetica, sans-serif;
            font-weight: 600;
            color: var(--secondary-color);
        }
        
        h1 {
            font-size: 2.3rem;
            margin-bottom: 1.5rem;
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: inline-block;
        }
        
        /* Sidebar styles */
        .css-1d391kg, .css-1wrcr25 {
            background-color: var(--card-bg-color);
            border-right: 1px solid #E4E6EB;
        }
        
        /* Sidebar title */
        .css-1d391kg h1, .css-1wrcr25 h1 {
            color: var(--primary-color) !important;
            -webkit-text-fill-color: var(--primary-color) !important;
            background: none;
            font-size: 1.5rem;
            margin-bottom: 1.2rem;
        }
        
        /* Button styles - Glossy effect */
        .stButton>button {
            background: linear-gradient(to bottom, var(--primary-color), #1670E6);
            color: white;
            border-radius: 20px;
            border: none;
            padding: 8px 16px;
            font-weight: 600;
            transition: all 0.2s ease;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            height: auto;
        }
        
        .stButton>button:hover {
            background: linear-gradient(to bottom, #1670E6, #1064D9);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            transform: translateY(-1px);
        }
        
        .stButton>button:active {
            transform: translateY(1px);
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
        }
        
        /* Danger button style */
        .danger-button button {
            background: linear-gradient(to bottom, var(--danger-color), #E62D32);
        }
        
        .danger-button button:hover {
            background: linear-gradient(to bottom, #E62D32, #D02428);
        }
        
        /* Success button style */
        .success-button button {
            background: linear-gradient(to bottom, var(--accent-color), #37A621);
        }
        
        .success-button button:hover {
            background: linear-gradient(to bottom, #37A621, #2E9219);
        }
        
        /* Card styles - Glossy effect */
        .css-1r6slb0, .element-container, .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div, div[data-testid="stForm"] {
            background-color: var(--card-bg-color);
            border-radius: var(--border-radius);
            transition: all 0.2s ease;
        }
        
        /* Add depth to cards with shadow */
        div[data-testid="stForm"], .card-container {
            box-shadow: var(--box-shadow);
            padding: 1.5rem;
            border-radius: var(--border-radius);
            background-color: var(--card-bg-color);
            margin-bottom: 1rem;
            border: 1px solid rgba(0,0,0,0.05);
        }
        
        /* Form elements styling */
        .stTextInput>div>div>input, .stSelectbox>div>div, .stTextArea>div>div>textarea {
            border-radius: var(--border-radius);
            border: 1px solid #E4E6EB;
            padding: 10px 12px;
            line-height: 1.4;
            transition: all 0.2s ease;
        }
        
        .stTextInput>div>div>input:focus, .stSelectbox>div>div:focus, .stTextArea>div>div>textarea:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 2px rgba(24, 119, 242, 0.2);
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
            background-color: #EFF1F3;
            border-radius: var(--border-radius);
            padding: 2px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            border-radius: var(--border-radius);
            padding: 0 16px;
            background-color: transparent;
            font-weight: 600;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: white !important;
            color: var(--primary-color) !important;
            box-shadow: var(--box-shadow);
        }
        
        /* Tables styling */
        .stDataFrame, [data-testid="stTable"] {
            border-radius: var(--border-radius);
            overflow: hidden;
            box-shadow: var(--box-shadow);
        }
        
        .stDataFrame table, [data-testid="stTable"] table {
            border-collapse: separate;
            border-spacing: 0;
        }
        
        .stDataFrame th, [data-testid="stTable"] th {
            background-color: #F8F9FA;
            padding: 12px 16px;
            border-top: none;
            font-weight: 600;
            color: var(--secondary-color);
        }
        
        .stDataFrame td, [data-testid="stTable"] td {
            padding: 12px 16px;
            border-top: 1px solid #E4E6EB;
        }
        
        /* Custom post card styling */
        .post-card {
            background-color: var(--card-bg-color);
            border-radius: var(--border-radius);
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: var(--box-shadow);
            transition: all 0.2s ease;
            border: 1px solid rgba(0,0,0,0.05);
        }
        
        .post-card:hover {
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
            transform: translateY(-2px);
        }
        
        .post-header {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .post-author {
            font-weight: 600;
            font-size: 1.1rem;
            color: var(--text-color);
        }
        
        .post-time {
            color: #65676B;
            font-size: 0.9rem;
            margin-left: auto;
        }
        
        .post-content {
            margin-bottom: 15px;
            line-height: 1.5;
            color: var(--text-color);
        }
        
        .post-actions {
            display: flex;
            border-top: 1px solid #E4E6EB;
            padding-top: 12px;
            margin-top: 5px;
        }
        
        .post-action {
            flex: 1;
            text-align: center;
            color: #65676B;
            padding: 8px 0;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s ease;
        }
        
        .post-action:hover {
            background-color: #F2F3F5;
            color: var(--primary-color);
        }
        
        /* Comment styles */
        .comment-container {
            margin-left: 20px;
            margin-bottom: 15px;
            padding: 12px 15px;
            background-color: #F2F3F5;
            border-radius: 15px;
            position: relative;
        }
        
        .comment-author {
            font-weight: 600;
            color: var(--text-color);
            font-size: 0.95rem;
        }
        
        .comment-content {
            margin-top: 4px;
            line-height: 1.4;
        }
        
        .comment-time {
            color: #65676B;
            font-size: 0.8rem;
            margin-top: 5px;
        }
        
        /* Dashboard metrics */
        .metric-card {
            background: linear-gradient(145deg, #FFFFFF, #F8F9FA);
            border-radius: var(--border-radius);
            padding: 20px;
            box-shadow: var(--box-shadow);
            text-align: center;
            transition: all 0.2s ease;
            border: 1px solid rgba(0,0,0,0.05);
        }
        
        .metric-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        }
        
        .metric-value {
            font-size: 2.2rem;
            font-weight: 700;
            color: var(--primary-color);
            margin: 10px 0;
        }
        
        .metric-label {
            font-size: 1rem;
            font-weight: 600;
            color: #65676B;
        }
        
        /* Custom loader */
        .stSpinner > div {
            border-color: var(--primary-color);
        }
        
        /* Dropdown menu styling */
        div[data-baseweb="select"] > div {
            border-radius: var(--border-radius);
            background-color: white;
            border: 1px solid #E4E6EB;
            box-shadow: none;
        }
        
        div[data-baseweb="select"]:hover > div {
            border-color: #BEC3C9;
        }
        
        /* Make radio buttons more modern */
        .stRadio [data-testid="stMarkdownContainer"] > p {
            font-size: 1rem;
            font-weight: 500;
        }
        
        /* Glossy header effect */
        .glossy-header {
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 20px;
            border-radius: var(--border-radius);
            margin-bottom: 20px;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
        }
        
        .glossy-header h2 {
            color: white !important;
            margin: 0;
        }
        </style>
    """, unsafe_allow_html=True)

def post_card(title, content, date, actions=None):
    """Create a Facebook-style post card"""
    html = f"""
    <div class="post-card">
        <div class="post-header">
            <div class="post-author">{title}</div>
            <div class="post-time">{date}</div>
        </div>
        <div class="post-content">
            {content}
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
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown(f"<h3>{title}</h3>", unsafe_allow_html=True)
        st.markdown(f"{content}")
        st.markdown('</div>', unsafe_allow_html=True)

def glossy_header(title, subtitle=None):
    """Create a glossy header with title and optional subtitle"""
    html = f"""
    <div class="glossy-header">
        <h2>{title}</h2>
        {f"<p>{subtitle}</p>" if subtitle else ""}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def metric_card(label, value, description=None):
    """Create a metric card with a label, value, and optional description"""
    html = f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {f"<div class='metric-description'>{description}</div>" if description else ""}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def danger_button(label, key=None, on_click=None):
    """Create a danger-styled button"""
    with st.container():
        st.markdown('<div class="danger-button">', unsafe_allow_html=True)
        result = st.button(label, key=key, on_click=on_click)
        st.markdown('</div>', unsafe_allow_html=True)
        return result

def success_button(label, key=None, on_click=None):
    """Create a success-styled button"""
    with st.container():
        st.markdown('<div class="success-button">', unsafe_allow_html=True)
        result = st.button(label, key=key, on_click=on_click)
        st.markdown('</div>', unsafe_allow_html=True)
        return result
