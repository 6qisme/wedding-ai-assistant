# db/queries.py

from db.db_connection import run_query

def find_self_rows(keyword: str):
    q = f"%{keyword}%"
    sql = """
    SELECT guest_code,
           COALESCE(display_name, name, alias) AS show_name,
           seat_number,
           group_code,
           relation_role,
           representative
    FROM guests
    WHERE name ILIKE %s OR alias ILIKE %s OR display_name ILIKE %s    
    """
    return run_query(sql, (q, q, q))

def find_family_by_guest_code(guest_code: str):
    sql = """
    SELECT guest_code,
           COALESCE(display_name, name, alias) AS show_name,
           seat_number,
           group_code,
           relation_role
    FROM guests
    WHERE representative = %s OR guest_code = %s
    ORDER BY relation_role
    """
    return run_query(sql, (guest_code, guest_code))

def find_guest_and_family(keyword: str):
    bundles = []
    matches = find_self_rows(keyword)
    if not matches:
        return []
    
    seen = set()
    for r in matches:
        # 找錨點self
        if r["relation_role"] == "self":
            anchor = r["guest_code"]
        else:
            # representative 可能是 None or self
            # 非self都會有代表人的 guest_code
            anchor = r.get("representative") or r["guest_code"]

        # 避免同一個家族重複
        if anchor in seen:
            continue
        seen.add(anchor)

        family = find_family_by_guest_code(anchor)

        who = next((m["show_name"] for m in family if m["relation_role"] == "self"),
                    family[0]["show_name"] if family else " (未知代表人) ")
        bundles.append({"who": who, "family":family})

    return bundles

if __name__ == "__main__":
    bundles = find_guest_and_family("黃")
    from db.formatters import format_guest_reply
    print(format_guest_reply(bundles))
