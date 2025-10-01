# db/formatters.py

def format_guest_reply(payload: dict) -> str:
    """
    Convert DB query payload into a user-facing text response.
    - Too_short / not_found / Too_many: return user guidance in Chinese
    - ok : return a full family seating list (role + table)
    """
    status = payload.get("status")
    data = payload.get("data", [])

    if status == "too_short":
        return "請輸入完整姓名喔！，例如：我要找張三"
    if status == "not_found":
        return "找不到符合的來賓，請確認姓名或嘗試暱稱"
    if status == "too_many":
        return "找到太多符合的人囉！請輸入更完整的姓名，例如「王小明」而不是「小明」。"
    
    if status == "ok":
        lines = ["感謝蒞臨 座位如下：", ""]
        role_rank = {"self":0, "spouse": 1, "child": 2, "guest":3, "other":4}
        
        for bundle in data:
            who = bundle.get("who") or " (未知代表人) "
            # lines.append(f"- 感謝{who}蒞臨 -")

            fam_sorted = sorted(
                bundle.get("family", []),
                key=lambda m:(role_rank.get(m.get("relation_role"), 9 ), str(m.get("show_name","")))
            )
            for f in fam_sorted:
                name = f.get("show_name", " (無名字) ")
                role = f.get("relation_role", " (未知身分) ")
                seat = f.get("seat_number")
                seat_str = f"{seat} 桌" if seat not in (None, "", 0) else "未安排"
                lines.append(f"- {name} ({role})：{seat_str}")

            lines.append("") # Blank line
        
        return "\n".join(lines).strip()
    
    return "發生未知的錯誤，請再試一次喔！"
