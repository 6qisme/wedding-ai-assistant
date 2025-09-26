# intents.py

import re

def classify_intents(text: str) -> str:
    intents = []
    if any(k in text for k in ["座","位","桌","找", "坐"]):
        intents.append("seat_lookup")
    if any(k in text for k in ["地點","地址","哪裡"]):
        intents.append("wedding_location")
    if any(k in text for k in ["時間","幾點","日期"]):
        intents.append("wedding_time")
    if not intents:
        intents.append("smalltalk")
    return intents

def extract_keyword(text: str) -> str:
    noise = ["我要找", "找", "桌", "位", "座", "坐", "哪", "哪裡"]
    for n in noise:
        text = text.replace(n, "")
    text = re.sub(r"[^\w\s\.\-\u4e00-\u9fff]", "", text)
    return text.strip()