import os, subprocess
from datetime import datetime
from config import Config

def create_backup():
    if not Config.BACKUP_ENABLED:
        print("[backup] disabled")
        return None
    backup_dir = os.path.join(os.getcwd(), "backups")
    os.makedirs(backup_dir, exist_ok=True)
    filename = f"smart_bonus_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    filepath = os.path.join(backup_dir, filename)
    try:
        subprocess.run(["pg_dump", Config.SQLALCHEMY_DATABASE_URI, "-f", filepath], check=True)
        return filepath
    except Exception as e:
        print("[backup] error:", e)
        return None
