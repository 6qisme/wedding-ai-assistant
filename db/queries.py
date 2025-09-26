# db/queries.py

from db.db_connection import run_query

def find_self_rows(keyword: str):
    q = f"%{keyword}%"
    sql = """
    SELECT guest_code,
           COALESCE(display_name, name, alias) AS show_name,
           seat_number,
           group_code,
           relation_role
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
    result = []
    self_rows = find_self_rows(keyword)
    if not self_rows:
        return[]
    for r in self_rows:
        gc = r["guest_code"]
        family = find_family_by_guest_code(gc)
        result.append({"who": r["show_name"], "family": family})
    return result

if __name__ == "__main__":
    bundles = find_guest_and_family("黃")
    from db.formatters import format_guest_reply
    print(format_guest_reply(bundles))
