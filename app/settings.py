from .models import Setting
from . import db

def get_setting(key, default):
    setting = Setting.query.filter_by(key=key).first()

    if not setting:
        new_setting = Setting(key=key, value=default)

        db.session.add(new_setting)
        db.session.commit()

        return default
    
    return setting.value

def set_setting(key, value):
    setting = Setting.query.filter_by(key=key).first()

    if not setting:
        new_setting = Setting(key=key, value=value)

        db.session.add(new_setting)
        db.session.commit()
    else:
        new_setting = db.session.query(Setting).get(setting.id)
        new_setting.value = value
        db.session.commit()
