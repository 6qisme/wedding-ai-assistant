# bot_core.py

import os
from typing import Optional, Dict

from dotenv import load_dotenv

from intents import classify_intents, extract_keyword
from db.queries import find_guest_and_family
from db.formatters import format_guest_reply
from data_provider import get_wedding_context_string
from ai_core import get_ai_reply

# Load environment variables from .env for local CLI testing
load_dotenv()

# Get environment variables
STATIC_BASE_URL = os.getenv("STATIC_BASE_URL", "http://127.0.0.1:8000/static")
STATIC_FULL_SEATMAP = os.getenv("STATIC_FULL_SEATMAP", "sample_map.example.webp")
DEBUG_VERBOSE = os.getenv("DEBUG_VERBOSE", "false").lower() == "true"

def handle_message(user_input: str) -> Dict[str, Optional[str]]:
    """
    Handle user input with the following strategy:
    1. Always include wedding information from JSON (static data).
    2. If the intent is seat lookup, also query the database for seat info.
    3. Otherwise, generate a natural-language reply via the AI model.

    :param user_input: User's message text.
    :return: A dictionary containing:
             - "text": reply text content.
             - "image_url": Optional seat map URL (if applicable).
    """
    result = {"text": "", "image_url": None}
    db_result = None

    # Step 1: Always include wedding info
    wedding_context = get_wedding_context_string()

    # Step 2: Add seat info if needed
    intents = classify_intents(user_input)

    if "seat_lookup" in intents:
        keyword = extract_keyword(user_input)
        if not keyword:
            result["text"] = (
                "抱歉，我不太確定你要找誰的座位，"
                "麻煩您重新查詢，查詢範例：「我要找王小明的座位」，謝謝您！"
            )
            return result
        
        # Query database
        db_result = find_guest_and_family(keyword)

        # Format reply context
        reply_text = format_guest_reply(db_result)
        result["text"] = reply_text

        tables = sorted({
            member.get("seat_number")
            for bundle in db_result.get("data",[])
            for member in bundle.get("family", [])
            if member.get("seat_number") not in (None, "", 0)
        })

        # Return seat chart URL
        if tables:
            result["image_url"] = f"{STATIC_BASE_URL}/maps/{STATIC_FULL_SEATMAP}"            
        
        
        if DEBUG_VERBOSE:
            print("========== DEBUG CONTEXT ==========")
            print("User question:", user_input)
            print("Seat context:\n", db_result or "(空)")
            print("Tables parsed:", tables)
            print("Image URL:", result["image_url"])

        return result

    
    # Step 3 : Merge contexts into one string
    full_context = wedding_context

    if DEBUG_VERBOSE:
        print("========== DEBUG CONTEXT ==========")
        print("User question:", user_input)
        print("===================================")
        print("Wedding context:\n",full_context[:1000],"...")

    # Step 4: Let GPT generate a natural reply
    try:
        reply = get_ai_reply(context=full_context, user_question=user_input)
        result["text"] = reply
        return result
    except Exception as e:
        result["text"] = "出了點狀況～請稍後再嘗試～"
        if DEBUG_VERBOSE:
            print(f"reply_error: {e}")
        return result 


if __name__ == "__main__":
    while True:
        user_input = input("你：")
        if user_input.lower() in ["quit", "exit"]:
            break
        r = handle_message(user_input)
        print("AI：", r["text"])
        if r["image_url"]:
            print("image_url:", r["image_url"])
