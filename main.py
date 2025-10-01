# main.py

# --- Section 1: Core Library Imports  ---

import time, json, os
import uvicorn
from datetime import datetime, timezone
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from dotenv import load_dotenv

# Load environment variables for the .env file for local development.
# On a cloud platform like Render, this is not needed and will safely be ignored.
load_dotenv()

# Import necessary components from the line-bot-sdk. 
from linebot.v3 import WebhookParser
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiException,
    ApiClient,
    MessagingApi,
    TextMessage,
    PushMessageRequest
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

# Local application imports
from ai_core import get_ai_reply
from data_provider import get_wedding_context_string

# PostgreSQL database import
from intents import classify_intents, extract_keyword
from db.queries import find_guest_and_family
from db.formatters import format_guest_reply

# --- Section 2: Initialization and Environment setup  ---

# Initialize the FastAPI application, 'app' is the core instance of our web service.
app = FastAPI()

# Retrieve credentials from environment variables.
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

# Safety check
if not channel_secret or not channel_access_token:
    print("ERROR: You must set 'LINE_CHANNEL_SECRET' and 'LINE_CHANNEL_ACCESS_TOKEN'. ")
    raise SystemExit(1)

# Instantiate LINE Bot SDK core components
# WebhookParser: For manually parsing and verifying
parser = WebhookParser(channel_secret)
# Configuration: Holds the Access Token used to authenticate API calls when sending messages.
configuration = Configuration(access_token=channel_access_token)
# Instantiate the main MessagingApi client for sending replies.
line_bot_api = MessagingApi(ApiClient(configuration))

# Failure message log
DEAD_LETTER_PATH ="instance/dead_letters.jsonl"

# When pushing fault, wait 1 or 2 second than try again,
# otherwise writing into dead_letters.jsonl for retry in the future.

def _push_with_retry(to_user_id: str, text: str, max_retries: int = 2) -> bool:
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
            print(f"[push][ok] to={to_user_id} try={attempt}")
            return True
        
        except ApiException as e:
            # When LINE API responds with an error (inspect http status/body for diagnostics).
            print(
                f"[push][api-error] status={getattr(e, 'status', None)} "
                f"body={getattr(e, 'body',None)} try={attempt}"
                  )
            
        except Exception as e:
            # Network-layer error (e.g. Connection reset by peer)
            print(f"[push][conn-error] {type(e).__name__}: {e} try={attempt}")

        if attempt <= max_retries:
            wait = 2 ** (attempt - 1) # 1s, 2s...
            print(f"[push] retry in {wait}s")
            time.sleep(wait)

    # Still failing after retries than write a dead-letter record (one JSON per line).
    try:
        folder = os.path.dirname(DEAD_LETTER_PATH)
        if folder:
            os.makedirs(folder, exist_ok=True)

        rec = {
            "ts": datetime.now(timezone.utc).isoformat(), # timezone-aware UTC
            "user_id": to_user_id,
            "text": safe_text
        }
        with open(DEAD_LETTER_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"[push][dead-letter] saved -> {DEAD_LETTER_PATH}")
    except Exception as e:
        print(f"[push][dead-letter][fail] {e}")
        return False
    
    return False # If dead-letter success.
    
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
            background_tasks.add_task(process_text_message, user_id, user_question)
    return 'OK'

# --- Section 4: Event Processing Logic ---

def process_text_message(user_id: str, user_question: str):
    """
    Processes incoming user message:
    1. Classify intent (seat lookup / wedding info / fallback).
    2. Query JSON or DB based on the intent.
    3. Wrap result with GPT to gernerate a nutural reply.
    4. Push reply back to the user
    """

    # Step 1: Classify intent

    intents = classify_intents(user_question)
    intent = intents[0] if intents else "smalltalk"

    print(f"Processing message for user: {user_id}")

    # Step 2: Prepare context depending on intent
    context = ""
    if intent == "seat_lookup":
       keyword = extract_keyword(user_question)
       if not keyword:
           reply_text = "抱歉，我不太確定你要找誰的座位，麻煩您重新查詢，查詢範例：「我要找王小明的座位」，謝謝您！"
           _push_with_retry(user_id, reply_text)
           return
       db_result = find_guest_and_family(keyword)
       context = format_guest_reply(db_result)

    elif intent in ["wedding_location", "wedding_time"]:
        context = get_wedding_context_string()
    
    else:
        context = get_wedding_context_string()

    try:
        reply_text = get_ai_reply(context=context, user_question=user_question)
        print(f"AI reply generated: '{reply_text[:100]}...'")

        ok = _push_with_retry(user_id, reply_text, max_retries=2)
        print("Push message sent." if ok else f"[push][give-up] user={user_id}")
    except Exception as e:
        # Catch any error in background (e.g. AI API calling fault.).
        print(f"An error occurred in background task for user {user_id}: {e}")

# --- Section 5 : Local Development Block ---
# This block only runs when the script is executed directly (e.g., python main.py).
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)


