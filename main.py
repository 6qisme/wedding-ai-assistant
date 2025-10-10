# main.py

# --- Section 1: Core Library Imports  ---
import os
import time
import json
from datetime import datetime, timezone
from typing import Any, Optional

import uvicorn
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
# Import necessary components from the line-bot-sdk. 
from linebot.v3 import WebhookParser
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiException,
    ApiClient,
    MessagingApi,
    TextMessage,
    PushMessageRequest,
    ReplyMessageRequest 
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

# Local application imports
from bot_core import handle_message

# Load environment variables for local development.
# On platforms like Render or Heroku, this is automatically handled.
load_dotenv()

# --- Section 2: Initialization and Environment setup  ---

# Initialize the FastAPI application, 'app' is the core instance of our web service.
app = FastAPI()

# Mount static folder for serving images and other assets
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Retrieve credentials from environment variables.
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

# Safety check
if not channel_secret or not channel_access_token:
    print("ERROR: You must set 'LINE_CHANNEL_SECRET' and 'LINE_CHANNEL_ACCESS_TOKEN'. ")
    raise SystemExit(1)
DEBUG_VERBOSE = os.getenv("DEBUG_VERBOSE", "false").lower() == "true"

# Instantiate LINE Bot SDK core components
# WebhookParser: For manually parsing and verifying
parser = WebhookParser(channel_secret)
# Configuration: Holds the Access Token used to authenticate API calls when sending messages.
configuration = Configuration(access_token=channel_access_token)
# Instantiate the main MessagingApi client for sending replies.
line_bot_api = MessagingApi(ApiClient(configuration))

# Failure message log
DEAD_LETTER_PATH = "instance/dead_letters.jsonl"

# When pushing fails, wait 1 or 2 seconds then try again,
# otherwise writing into dead_letters.jsonl for retry in the future.

def _reply_safe(reply_token: str, text: str) -> None:
    """Send a reply message via LINE Reply API (no quota consumption)."""
    safe_text = text if len(text) <= 4500 else (text[:4490] + "...(截斷)")
    try:
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=safe_text)]
            )
        )
        if DEBUG_VERBOSE:
            print(f"[reply][ok] len={len(safe_text)}")
    except ApiException as e:
        if DEBUG_VERBOSE:
            print(f"[reply][api-error] {e}")

def _push_with_retry(to_user_id: str, text: str, max_retries: int = 2) -> bool:
    """
    Send a text message to a LINE user with retry and dead-letter fallback.

    :param to_user_id: The LINE user ID to send the message to.
    :param text: Message content to be sent.
    :param max_retries: Maximum number of retries before writing to dead-letter.
    :return: True if message sent successfully; False otherwise.
    """

    # Limit LINE single message to ~5000 chars, conservatively truncate to avoid rejection.
    safe_text = text if len(text) <= 4500 else (text[:4490] + "...(截斷)")

    for attempt in range(1, max_retries + 2):
        try:
            line_bot_api.push_message(
                PushMessageRequest(
                    to=to_user_id,
                    messages=[TextMessage(text=safe_text)]
                )
            )
            if DEBUG_VERBOSE:
                print(f"[push][ok] to={to_user_id[:5]}***{to_user_id[-3:]} try={attempt}")
            return True
        
        except ApiException as e:
            # When LINE API responds with an error (inspect http status/body for diagnostics).
            if DEBUG_VERBOSE:
                print(
                    f"[push][api-error] status={getattr(e, 'status', None)} "
                    f"body={getattr(e, 'body',None)} try={attempt}"
                    )
            
        except Exception as e:
            # Network-layer error (e.g. Connection reset by peer)
            if DEBUG_VERBOSE:
                print(f"[push][conn-error] {type(e).__name__}: {e} try={attempt}")

        if attempt <= max_retries:
            wait = 2 ** (attempt - 1)  # 1s, 2s...
            print(f"[push] retry in {wait}s")
            time.sleep(wait)

    # Still failing after retries than write a dead-letter record (one JSON per line).
    try:
        folder = os.path.dirname(DEAD_LETTER_PATH)
        if folder:
            os.makedirs(folder, exist_ok=True)

        rec = {
            "ts": datetime.now(timezone.utc).isoformat(),  # timezone-aware UTC
            "user_id": f"{to_user_id[:5]}***{to_user_id[-3:]}",
            "text": safe_text
        }
        with open(DEAD_LETTER_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"[push][dead-letter] saved -> {DEAD_LETTER_PATH}")
    except Exception as e:
        if DEBUG_VERBOSE:
            print(f"[push][dead-letter][fail] {e}")
            return False
    
    return False  # Return False if written to dead-letter file.
    
# --- Section 3 : Define the API router ---
# Define the URL path

# Health Check Endpoint
# @app.get("/") is a route for checking the server is alive.
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Wedding AI Assistant is alive."}

# Webhook endpoint, receiving all messages from LINE.
# @app.post("/webhook"), only accept POST method from this path.
@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    # Get 'X-Line-Signature'
    signature = request.headers.get('X-Line-Signature', '')

    # Get the request body as bytes.
    body = await request.body()

    try: 
        # Signature Check Point
        events = parser.parse(body.decode('utf-8'), signature)
    except InvalidSignatureError:
        # Refuse invalid request
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Go through all verified events
    for event in events:
        # Only handle text message.
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent):
            # Instantiate a single background task for every text message.
            user_id = event.source.user_id
            user_question = event.message.text
            reply_token = event.reply_token
            background_tasks.add_task(process_text_message, user_id, user_question, reply_token)
    return 'OK'

# --- Section 4: Event Processing Logic ---

def process_text_message(user_id: str, user_question: str, reply_token: Optional[str] = None) -> None:
    """
    Handle a single text message event in a background thread.

    :param user_id: LINE user ID.
    :param user_question: Text content of the message.
    :return: None. The reply is sent asynchronously via LINE API.
    """

    print(f"Processing message for user: {user_id[:5]}***{user_id[-3:]}")

    try:
        result = handle_message(user_question)  # Handling by bot_core.py.
        reply_text = result.get("text", "")
        image_url = result.get("image_url")

        if not reply_text:
            reply_text = "出了點狀況喔！請稍後再試～"

        # Reply Mode
        if reply_token:
            _reply_safe(reply_token, reply_text)
        else:
            _push_with_retry(user_id, reply_text)    
        
        # For a seat query, return the seat map URL.
        if image_url:
            _push_with_retry(user_id, f"📍座位圖請看這裡：{image_url}")

    except Exception as e:
        if DEBUG_VERBOSE:
            print(f"[process_text_message][error] user={user_id}: {e}")
        if reply_token:
            _reply_safe(reply_token, "出了點狀況喔！請稍後再試～")
        else:
            _push_with_retry(user_id, "出了點狀況喔！請稍後再試～")

# --- Section 5 : Local Development Block ---
# This block only runs when the script is executed directly (e.g., python main.py).
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)


