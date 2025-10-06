# intents.py

import re

def classify_intents(text: str) -> list[str]:
    """
    Return list of intents.
    Currently only distinguish seat lookup.
    """
    intents = []
    if any(k in text for k in ["座","位","桌","找", "坐"]):
        intents.append("seat_lookup")

    return intents

def extract_keyword(text: str) -> str:
    phrases = [
        r"我要找", r"幫我找", r"請幫我找", r"找一下", r"查一下", r"查詢", r"查",
        r"請問", r"問", r"麻煩", r"謝謝",
        r"座位", r"位置", r"座", r"位", r"桌", r"坐在哪裡", r"坐在哪", r"在哪裡", r"在哪",
        r"我的", r"我座", r"我坐", r"我", r"的", r"的位子", r"的座位" , r"坐哪", r"坐哪裡"
    ]
    pattern = "(" + "|".join(phrases) + ")"
    text = re.sub(pattern, "", text)

    text = re.sub(r"[^\w\s\.\-\u4e00-\u9fff]", "", text).strip()

    return text if len(text) >= 2 and len(text)<=20 else "" #