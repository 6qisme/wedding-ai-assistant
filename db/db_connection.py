# db_connection.py

import os 
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Go to root path.
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

def get_connection():
    """
    Create a PostgreSQL connection.
    Priority:
    1. RENDER_DATABASE_URL (internal, best for Render deploy)
    2. REMOTE_DATABASE_URL (external, for local dev to connect cloud DB)
    3. PG* variables (for local dev only)
    """

    db_url = os.getenv("RENDER_DATABASE_URL") or os.getenv("REMOTE_DATABASE_URL")
    if db_url:
        # Render
        return psycopg2.connect(
            db_url, 
            sslmode="require", 
            cursor_factory=RealDictCursor
            )
    else:
        return psycopg2.connect(
            dbname=os.getenv("PGDATABASE" ,"your_db"),
            user=os.getenv("PGUSER", "postgres"),
            password=os.getenv("PGPASSWORD","your_password"),
            host=os.getenv("PGHOST", "localhost"),
            port=os.getenv("PGPORT", "5432"),
            cursor_factory=RealDictCursor
        ) 

def run_query(sql:str, params: tuple= ()):
    """
    Convenience helper:
    Execute a read-only query and return list[dict].
    It opens/closes the connection for the function
    """

    conn = None
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchall()
    finally:
        if conn:
            conn.close()