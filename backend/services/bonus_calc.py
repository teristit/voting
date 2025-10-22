from extensions import db

def calculate_bonus_for_session(session_id: int):
    try:
        sql = db.text("SELECT * FROM calculate_session_results(:sid)")
        rows = db.session.execute(sql, {"sid": session_id}).fetchall()
        return [dict(r._mapping) for r in rows]
    except Exception as e:
        print("[bonus_calc] error:", e)
        return []
