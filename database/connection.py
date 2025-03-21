import psycopg2
import streamlit as st

class DatabaseConnection:
    def __init__(self):
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Connect to PostgreSQL database using Streamlit secrets"""
        try:
            # Get database URL from Streamlit secrets
            db_url = st.secrets["db_url"]
            
            # Connect to the database
            self.conn = psycopg2.connect(db_url)
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            st.error(f"Database connection error: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def execute_query(self, query, params=None, fetch=False):
        """Execute a database query with optional parameters"""
        try:
            self.cursor.execute(query, params or ())
            
            if fetch:
                return self.cursor.fetchall()
            else:
                self.conn.commit()
                return True
        except Exception as e:
            self.conn.rollback()
            st.error(f"Query execution error: {e}")
            return None
    
    def execute_single_fetch(self, query, params=None):
        """Execute a query and fetch a single result"""
        self.cursor.execute(query, params or ())
        return self.cursor.fetchone()
    
    def table_exists(self, table_name):
        """Check if a table exists in the database"""
        query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = %s
            );
        """
        result = self.execute_single_fetch(query, (table_name,))
        return result[0] if result else False
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        # Users table
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Facebook accounts table
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS fb_accounts (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                account_name VARCHAR(100) NOT NULL,
                access_token TEXT NOT NULL,
                page_id VARCHAR(255),
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Posts table (for caching/tracking posts)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS posts (
                id SERIAL PRIMARY KEY,
                fb_post_id VARCHAR(255) UNIQUE NOT NULL,
                account_id INTEGER REFERENCES fb_accounts(id),
                content TEXT,
                post_url TEXT,
                posted_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Comments table (for caching/tracking comments)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS comments (
                id SERIAL PRIMARY KEY,
                fb_comment_id VARCHAR(255) UNIQUE NOT NULL,
                post_id INTEGER REFERENCES posts(id),
                content TEXT,
                commented_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

# Database connection as a singleton
db = DatabaseConnection()

def get_db_connection():
    """Get the database connection singleton"""
    if not db.conn or db.conn.closed:
        db.connect()
        db.create_tables()
    return db
