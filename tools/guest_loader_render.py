# tools/guest_loader_render.py

import psycopg2
import os
import csv
from dotenv import load_dotenv

def normalize(value: str):
    if value is None:
        return None
    val = str(value).strip()
    return val if val else None

def main():
    load_dotenv()
    db_url = os.getenv("RENDER_DATABASE_URL") or os.getenv("REMOTE_DATABASE_URL")
    if not db_url:
        raise RuntimeError("🥲 No database URL found. Please set RENDER_DATABASE_URL or REMOTE_DATABASE_URL.")
    
    conn = psycopg2.connect(db_url, sslmode="require")
    cur = conn.cursor()

    try:
        # Reset guests
        print("🧹Try to reset the guests database...")
        cur.execute("TRUNCATE TABLE guests RESTART IDENTITY CASCADE;")
        print("✅guests database has been cleared.")

        # Import csv
        filename = os.getenv("GUESTS_CSV_PATH")
        if not filename:
            raise ValueError("GUESTS_CSV_PATH hasn't been set, please check .env file!")
        
        with open(filename, newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                cur.execute("""
                            INSERT INTO guests
                            (guest_code, name, alias, seat_number, attending, group_code, relation_role, representative, display_name)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                            """,(
                                  normalize(row.get("guest_code")),
                                  normalize(row.get("name")),
                                  normalize(row.get("alias")),
                                  int(row["seat_number"]) if row.get("seat_number") else None,
                                  str(row.get("attending", "")).strip().upper() == "TRUE",
                                  normalize(row.get("group_code")),
                                  normalize(row.get("relation_role")),
                                  normalize(row.get("representative")),
                                  normalize(row.get("display_name"))
                            ))
        conn.commit()
        print("👌guests file import success on Render!")
        
        cur.execute("SELECT COUNT(*) FROM guests;")
        print("Total rows in DB:", cur.fetchone()[0])

    except Exception as e:
        print(f"🚫error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()