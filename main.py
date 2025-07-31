# main.py

# --- Section 1: Core Library Imports  ---

import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv

# Import necessary components from the line-bot-sdk. 
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

# Local application imports
from ai_core import get_ai_reply
from data_provider import get_wedding_context_string

# --- Section 2: Initialization and Environment setup  ---

# Load environment variables for the .env file for local development.
# On a cloud platform like Render, this is not needed and will safely be ignored.
load_dotenv()

# Initialize the FastAPI application, 'app' is the core instance of our web service.
app = FastAPI()

# Retrieve credentials from environment variables.
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

# Safety check
if not channel_secret or not channel_access_token:
    print("error: You must set 'LINE_CHANNEL_SECRET' and 'LINE_CHANNEL_ACCESS_TOKEN'. ")
    exit()

# Instantiate LINE Bot SDK core components
# WebhookHandler: Verifies that the signature comes from LINE's official servers.
handler = WebhookHandler(channel_secret)
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

# Webhook endpoint, reciving all messages from LINE.
# @app.post("/webhook"), only accept POST method from this path.
@app.post("/webhook")
async def webhook(request: Request):
    # Get 'X-Line-Signature'
    signature = request.headers['X-Line-Signature']

    # Get the request body as bytes.
    body = await request.body()

    try:
        # Send request and signature to verify by handler.
        # If the signature is false, an InvalidSignatureError is raised.
        handler.handle(body.decode(), signature)
    except InvalidSignatureError:
        # If signature false, refuse the request and return  "400" error.
        print("Invalid signature detected. Request rejected.")
        raise HTTPException(status_code=400, detail='Invalid signature.')
    
    return 'OK'

# --- Section 4: Event Processing Logic ---
# Defines the logic for handling incoming messages.

# Message Handler, focus on text messages.
# The @handler.add(...) decorator  registers the function below as the handler for message events.
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    # 1. Retrieve wedding information from data_provider
    context = get_wedding_context_string()

    # 2. Retrieve user question
    user_question = event.message.text

    # 3. Consolidates wedding information and user question to ai_core handle.
    reply_text = get_ai_reply(context=context, user_question=user_question)

    # 4. Sending AI's reply to user.
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=reply_text)]
        )
    )

# --- Section 5 : Local Development Block ---
# This block only runs when the script is executed directly (e.g., python main.py).
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)


