from extensions import db
from models.settings import SystemSetting

def get_setting(key, default=None):
    setting = SystemSetting.query.get(key)
    return setting.setting_value if setting else default

def set_setting(key, value):
    setting = SystemSetting.query.get(key)
    if not setting:
        setting = SystemSetting(setting_key=key, setting_value=value)
        db.session.add(setting)
    else:
        setting.setting_value = value
    db.session.commit()
    return value
