# db/formatters.py

def format_guest_reply(bundles: list) -> str:
    """
    將 guest + family 的查詢結果格式化變成使用者可讀的文字。
    bundles: list[dict]，格式例如：
    [
        {   
            "who": "王先生",
            "family": [
                {"show_name": "王先生", "seat_number": 5, "relation_role": "self"},
                {"show_name": "王媽媽", "seat_number": 5, "relation_role": "mother"}
            ]
        }
    ]
    """
    if not bundles:
        return "我查不到喔！請輸入完整名稱或部份姓名／暱稱。"
    
    lines = []
    for b in bundles:
        lines.append(f"- {b['who']}一家 -")
        fam_sorted = sorted(
            b["family"],
            key=lambda x: (x["relation_role"] != "self", x["relation_role"])
        )
        for f in fam_sorted:
            seat = f["seat_number"] or " (未安排) "
            lines.append(f"{f['show_name']}：桌 {seat} ({f['relation_role']})")
        lines.append("")  # 空行分隔

    return "\n".join(lines).strip()