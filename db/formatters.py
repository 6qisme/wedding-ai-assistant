# db/formatters.py

def format_guest_reply(payload: dict) -> str:
    """

    """
    status = payload.get("status")
    data = payload.get("data", [])

    if status == "too_short":
        return "請輸入完整姓名喔！，例如：我要找張三"
    if status == "not_found":
        return "找不到符合的來賓，請確認姓名或嘗試暱稱"
    if status == "too_many":
        return "找到太多符合的人囉！請輸入更完整的姓名～"
    
    if status == "ok":
        lines = []
        role_rank = {"self":0, "spouse": 1, "child": 2, "guest":3, "other":4}
        for bundle in data:
            who = bundle.get("who") or " (未知代表人) "
            lines.append(f"- {who}一家 -")

            fam_sorted = sorted(
                bundle.get("family", []),
                key=lambda m:(role_rank.get(m.get("relation_role"), 9 ), str(m.get("show_name","")))
            )
            for f in fam_sorted:
                name = f.get("show_name", " (無名字) ")
                role = f.get("relation_role", " (未知身分) ")
                seat = f.get("seat_number")
                seat_str = str(seat) if seat not in (None, "", 0) else "未安排"
                lines.append(f"{name}：桌{seat_str}({role})")

            lines.append("") # Blank line
        
        return "\n".join(lines).strip()
    
    return "發生未知的錯誤，請再試一次喔！"
    

    

    # if not bundles:
    #     return "我查不到喔！請輸入完整名稱或部份姓名／暱稱。"
    
    # lines = []
    # for b in bundles:
    #     lines.append(f"- {b['who']}一家 -")
    #     fam_sorted = sorted(
    #         b["family"],
    #         key=lambda x: (x["relation_role"] != "self", x["relation_role"])
    #     )
    #     for f in fam_sorted:
    #         seat = f["seat_number"] or " (未安排) "
    #         lines.append(f"{f['show_name']}：桌 {seat} ({f['relation_role']})")
    #     lines.append("")  # 空行分隔

    # return "\n".join(lines).strip()