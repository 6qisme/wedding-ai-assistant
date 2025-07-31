# data_provider.py

# This module is responsible for providing all necessary wedding information as a single, consolidated string.
# It acts as the "single source of truth" for the AI model.

def get_wedding_context_string() -> str:
    """
    Consolidates all wedding information details into a single, well formatted string.
    This string will be injected into the AI's system prompt to provide context.

    :return: A string containing all wedding information.
    """

    context = """
    # 婚禮基本資訊
    - 新郎: QQ
    - 新娘: ShuYu
    - 日期: 2025年10月26日 (星期六)
    - 地點: 台北 W 飯店

    # 時間流程
    - 迎賓接待: 11:00
    - 宴會開始: 12:00
    - 逐桌敬酒: 13:00
    - 送客時間: 15:00

    # 交通資訊
    - 地址: 台北某個地方
    - 捷運: 台北小巨蛋站
    - 停車: 飯店提供免費停車，請告知接待人員

    # 其他資訊
    - 服裝: 正式服裝
    - 禮金: 現場設有禮金桌，感謝您的祝福
    - 小驚喜: 現場設有CandyBar以及限量香水禮品
    """
    return context.strip()

    