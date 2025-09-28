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
    if not keyword or len(keyword) < 2 or len(keyword)>20:
        return {"status": "too_short", "data":[]}
    
    self_rows = find_self_rows(keyword)
    if not self_rows:
        return {"status": "not_found", "data":[]}
    
    if len(self_rows) > 5:
        return {"status": "too_many", "data": []}
    
    result = []
    seen = set()
    for r in self_rows:
        # Find anchor
        if r["relation_role"] == "self":
            anchor = r["guest_code"]
        else:
            anchor = r.get("representative") or r["guest_code"]

        if anchor in seen: # If this guest_code had been processed than skip. 
            continue

        seen.add(anchor) # Record data to avoid duplicate processing

        family = find_family_by_guest_code(anchor)
        who = next((m["show_name"] for m in family if m["relation_role"] == "self"),
                   family[0]["show_name"] if family else " (未知代表人) ") # Screen out representatives
        result.append({"who": who, "family": family})
    
    return {"status": "ok", "data": result}

if __name__ == "__main__":
    bundles = find_guest_and_family("劉")
    from db.formatters import format_guest_reply
    print(format_guest_reply(bundles))
