from polylogyx.models import Pack

def get_all_packs():
    return Pack.query.all()

def get_pack_by_id(pack_id):
    return Pack.query.filter(Pack.id == pack_id).first()

def get_pack_by_name(name):
    return Pack.query.filter(Pack.name == name).first()

def add_pack(**data):
    return Pack.create(**data)
