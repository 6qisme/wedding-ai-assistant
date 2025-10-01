# tools/init_db.py

import os 
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SCHEMA_FILE = os.path.join(BASE_DIR, "db/schema.sql")
load_dotenv()

def get_connection():
    db_url = os.getenv("RENDER_DATABASE_URL") or os.getenv("REMOTE_DATABASE_URL")
    if not db_url:
        raise RuntimeError("🥲 No database URL found. Please set RENDER_DATABASE_URL or REMOTE_DATABASE_URL.")
    return psycopg2.connect(db_url, sslmode="require", cursor_factory=RealDictCursor)

def init_db():
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            schema_sql = f.read()

    conn = get_connection()
    with conn:
         with conn.cursor() as cur:
              cur.execute(schema_sql)
    conn.close()
    print("😃Database schema initialized successfully.")
    
if __name__ == "__main__":
     init_db()