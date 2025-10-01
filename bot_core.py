# bot_core.py

import os 

from intents import classify_intents, extract_keyword
from db.queries import find_guest_and_family
from db.formatters import format_guest_reply
from data_provider import get_wedding_context_string
from ai_core import get_ai_reply
from dotenv import load_dotenv
load_dotenv()

def handle_message(user_input: str) -> str:
    """
    Handle user input with the following strategy:
    1. Always include wedding information from JSON (static data).
    2. If the intent is seat lookup, also query the database for seat info.
    3. Combine all context and let GPT generate the final reply.
    """
    db_result = None
    # Step 1: Always include wedding info
    wedding_context = get_wedding_context_string()

    # Step 2: Add seat info if needed
    intents = classify_intents(user_input)

    if "seat_lookup" in intents:
        keyword = extract_keyword(user_input)
        if not keyword:
            return "抱歉，我不太確定你要找誰的座位，麻煩您重新查詢，查詢範例：「我要找王小明的座位」，謝謝您！"
        db_result = find_guest_and_family(keyword)
        reply = format_guest_reply(db_result)

        DEBUG_VERBOSE = os.getenv("DEBUG_VERBOSE", "false").lower() == "true"

        if DEBUG_VERBOSE:
            print("========== DEBUG CONTEXT ==========")
            print("User question:", user_input)
            print("Seat context:\n", db_result or "(空)")
            print("Seat context(format):\n",reply)
        return reply

    
    # Step 3 : Merge contexts into one string
    full_context = wedding_context

    DEBUG_VERBOSE = os.getenv("DEBUG_VERBOSE", "false").lower() == "true"
    if DEBUG_VERBOSE:
        print("========== DEBUG CONTEXT ==========")
        print("User question:", user_input)
        print("===================================")
        print("Wedding context (first 500):\n",full_context[:500],"...")

    # Step 4: Let GPT generate a natural reply
    try:
        reply = get_ai_reply(context=full_context, user_question=user_input)
        return reply
    except Exception as e:
        print(f"reply_error: {e}")
        return "出了點狀況～請稍後再嘗試～"


if __name__ == "__main__":
    while True:
        user_input = input("你：")
        if user_input.lower() in ["quit", "exit"]:
            break
        print("AI：", handle_message(user_input))