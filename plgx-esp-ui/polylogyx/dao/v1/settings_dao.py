from polylogyx.models import Settings


def get_settings_by_name(name):
    return Settings.query.filter(Settings.name == name).first()


def create_settings(name, setting):
    return Settings.create(name=name, setting=setting)


def update_or_create_setting(name, setting):
    settings_obj = Settings.query.filter(Settings.name == name).first()
    if settings_obj:
        settings_obj.setting = setting
        return settings_obj.update(settings_obj)
    else:
        return Settings.create(name=name, setting=setting)
