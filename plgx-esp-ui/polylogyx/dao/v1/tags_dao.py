from polylogyx.models import Tag
from sqlalchemy import desc


def get_all_tags(searchterm=""):
    return Tag.query.filter(Tag.value.ilike('%' + searchterm + '%')).order_by(
        desc(Tag.id))


def get_tags_total_count():
    return Tag.query.count()


def delete_tag(tag):
    tag.delete()


def create_tag_obj(tag):
    tag_existing = Tag.query.filter(Tag.value == tag).first()
    if tag_existing:
        return tag_existing
    else:
        return Tag.create(value=tag)


def get_tag_by_value(tag):
    return Tag.query.filter(Tag.value == tag).first()
