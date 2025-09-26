# seed_loader.py

import psycopg2
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(__file__)) # Go to project root path
DB_DIR = os.path.join(BASE_DIR, "db")

schema_path = os.path.join(DB_DIR, "schema.sql")
seed_path = os.path.join(DB_DIR, "seed_data.sql")


def run_sql_file(filename):
    with open(filename, 'r', encoding="utf-8") as f:
        return f.read()

def main():
    load_dotenv()
    conn = psycopg2.connect(
            dbname=os.getenv("PGDATABASE" ,"your_db"),
            user=os.getenv("PGUSER", "postgres"),
            password=os.getenv("PGPASSWORD","your_password"),
            host=os.getenv("PGHOST", "localhost"),
            port=os.getenv("PGPORT", "5432")
        ) 
    cur = conn.cursor()
    
    try:
        print("建立資料表...")
        cur.execute(run_sql_file(schema_path))
        print("載入初始群組...")
        cur.execute(run_sql_file(seed_path))
        conn.commit()
        print("初始化完成!")
    except Exception as e:
        print(f"錯誤： {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()