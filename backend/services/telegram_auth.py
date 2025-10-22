import hashlib, hmac, urllib.parse, json
from config import Config

def verify_telegram_init_data(init_data):
    try:
        if not init_data:
            return None
        if isinstance(init_data, dict):
            parsed = init_data
        else:
            parsed = dict(urllib.parse.parse_qsl(init_data))
        hash_to_check = parsed.pop("hash", None)
        data_check_items = sorted((k, v) for k, v in parsed.items())
        data_check_string = "\n".join(f"{k}={v}" for k,v in data_check_items)

        secret_key = hmac.new(b"WebAppData", Config.TELEGRAM_BOT_TOKEN.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        if hash_to_check and calculated_hash != hash_to_check:
            return None
        user_json = parsed.get("user")
        if user_json:
            try:
                return json.loads(user_json)
            except Exception:
                return parsed
        return parsed
    except Exception as e:
        print("[telegram_auth] error:", e)
        return None
