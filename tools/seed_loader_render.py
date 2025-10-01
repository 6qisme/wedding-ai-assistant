# tools/seed_loader_render.py

import psycopg2
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(__file__)) # Go to project root path
DB_DIR = os.path.join(BASE_DIR, "db")

schema_path = os.path.join(DB_DIR, "schema.sql")
seed_path = os.path.join(DB_DIR, "seed_data.sql")


def run_sql_file(filename, cursor):
    with open(filename, 'r', encoding="utf-8") as f:
        sql = f.read()
        for statement in sql.split(";"):
            if statement.strip():
                cursor.execute(statement)
    print(f"✅{os.path.basename(filename)} executed successfully!")

def main():
    load_dotenv()
    db_url = os.getenv("RENDER_DATABASE_URL") or os.getenv("REMOTE_DATABASE_URL")
    if not db_url:
        raise RuntimeError("🥲 No database URL found. Please set RENDER_DATABASE_URL or REMOTE_DATABASE_URL.")
    
    conn = psycopg2.connect(db_url, sslmode="require")
    cur = conn.cursor()
    
    try:
        print("🛠️Building database...")
        run_sql_file(schema_path, cur)
        print("📦Loading init groups...")
        run_sql_file(seed_path, cur)

        conn.commit()
        print("✅Initialization completed!")
    except Exception as e:
        print(f"錯誤： {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()