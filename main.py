# main.py

# --- Section 1: Core Library Imports  ---

import os
import uvicorn
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
    ApiClient,
    MessagingApi,
    TextMessage,
    PushMessageRequest
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

# Local application imports
from ai_core import get_ai_reply
from data_provider import get_wedding_context_string

# --- Section 2: Initialization and Environment setup  ---

# Initialize the FastAPI application, 'app' is the core instance of our web service.
app = FastAPI()

# Retrieve credentials from environment variables.
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

# Safety check
if not channel_secret or not channel_access_token:
    print("ERROR: You must set 'LINE_CHANNEL_SECRET' and 'LINE_CHANNEL_ACCESS_TOKEN'. ")
    exit()

# Instantiate LINE Bot SDK core components
# WebhookParser: For manually parsing and verifying
parser = WebhookParser(channel_secret)
# Configuration: Holds the Access Token used to authenticate API calls when sending messages.
configuration = Configuration(access_token=channel_access_token)
# Instantiate the main MessagingApi client for sending replies.
line_bot_api = MessagingApi(ApiClient(configuration))

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
    Processes a text message in background, calls the AI, and pushes the reply.
    """
    print(f"Processing message for user: {user_id}")
    context = get_wedding_context_string()

    try:
        reply_text = get_ai_reply(context=context, user_question=user_question)
        print(f"AI reply generated: '{reply_text[:30]}...'")

        line_bot_api.push_message(
            PushMessageRequest(
                to=user_id,
                messages=[TextMessage(text=reply_text)]
            )
        )
        print("Push message sent.")
    except Exception as e:
        # Catch any error in background (e.g. AI API calling fault.).
        print(f"An error occurred in background task for user {user_id}: {e}")

# --- Section 5 : Local Development Block ---
# This block only runs when the script is executed directly (e.g., python main.py).
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)


