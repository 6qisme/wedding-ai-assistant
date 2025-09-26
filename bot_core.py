# bot_core.py

from intents import classify_intents, extract_keyword
from db.queries import find_guest_and_family
from db.formatters import format_guest_reply
from dotenv import load_dotenv
load_dotenv(".env")

def handle_message(text: str) -> str:
    intents = classify_intents(user_input)
    answers = []
    for intent in intents:
        if intent == "seat_lookup":
            bundles = find_guest_and_family(extract_keyword(user_input))
            return format_guest_reply(bundles)
        elif intent == "wedding_location":
            return "婚禮地點在台北 XX 飯店"
        elif intent == "wedding_time":
            return "婚禮時間是 2025/2/2 中午十二點"
        else:
            return "婚禮的問題都可以問我喔!"
    print("\n".join(answers))
        
if __name__ == "__main__":
    while True:
        user_input = input("你：")
        if user_input.lower() in ["quit", "exit"]:
            break
        print("AI：", handle_message(user_input))