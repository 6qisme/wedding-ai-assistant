import os
import time
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone

# Force to assign .env file in root path.
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

URL = os.getenv("KEEP_ALIVE_URL")

if not URL:
    raise SystemExit("ERROR: KEEP_ALIVE_URL is not set in .env")

while True:
    try:
        r = requests.get(URL, timeout=10)
        print(f"[{datetime.now(timezone.utc).isoformat()}][keep-alive] {r.status_code}")
    except Exception as e:
        print(f"[{datetime.now(timezone.utc).isoformat()}][keep-alive][fail] {e}")
    time.sleep(300) # 5 minutes (300s)

