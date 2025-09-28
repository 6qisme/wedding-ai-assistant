# tools/guest_loader.py

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
    conn = psycopg2.connect(
            dbname=os.getenv("PGDATABASE" ,"your_db"),
            user=os.getenv("PGUSER", "postgres"),
            password=os.getenv("PGPASSWORD","your_password"),
            host=os.getenv("PGHOST", "localhost"),
            port=os.getenv("PGPORT", "5432")
        ) 
    cur = conn.cursor()

    try:
        # Reset guests
        print("Try to reset the guests database...")
        cur.execute("TRUNCATE TABLE guests RESTART IDENTITY CASCADE;")
        print("guests database has been cleaned.")

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
        cur.execute("SELECT COUNT(*) FROM guests;")
        print("Total rows in DB:", cur.fetchone()[0])
        print("guests file import success!")
    except Exception as e:
        print(f"error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    print(os.getenv("PGUSER")) 
    main()