from polylogyx.models import Tag

def get_all_tags():
    return Tag.query.all()
