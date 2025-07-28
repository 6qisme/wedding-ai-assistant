# data_provider.py

# A Python dictionary that serves as a static database.
# All public information about the wedding is stored here. 
_WEDDING_INFO_DB = {
    "婚禮時間": "2025年10月26日 星期六 中午12:00入席",
    "婚禮地點": "台北東方文華酒店 7F豪瑞奇廳",
    "地址": "台北的某個地方",
    "交通方式": "騎車或開車都有停車位",
    "dress_code": "開心就好,但不要太噁",
    "預設回覆": "真是個好問題!但我目前還無法回答，您可以嘗試問我關於「時間」、「地點」或「交通」的問題。"
}

def get_wedding_info(user_question: str) -> str:
    """
    Finds and returns corresponding information from the static database
    based on keywords in the user's question.

    :param user_question:The original question string from the user.
    :return: The found answer or a default reply.
    """

    if "時間" in user_question or "時候" in user_question or "幾點" in user_question:
        return _WEDDING_INFO_DB["婚禮時間"]
    elif "地點" in user_question or "哪裡" in user_question or "地址" in user_question:
        # Reply with both "location" and "address" for convenience.
        return f"{_WEDDING_INFO_DB['婚禮地點']}\n地址:{_WEDDING_INFO_DB['地址']}"
    elif "交通" in user_question or "怎麼去" in user_question :
        return _WEDDING_INFO_DB["交通方式"]
    elif "穿" in user_question or "服裝" in user_question:
        return _WEDDING_INFO_DB["dress_code"]
    else:
        # If no keywords match the conditions above.
        return _WEDDING_INFO_DB["預設回覆"]
    