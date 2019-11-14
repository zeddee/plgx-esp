from polylogyx.models import Query, db

def get_query_by_name(query_name):
    return Query.query.filter(Query.name == query_name).first()

def add_query(query_name, **query):
    return Query.create(name=query_name, **query)

def get_all_queries():
    return Query.query \
        .options(
        db.joinedload(Query.tags)
    ).filter(~Query.packs.any()).all()

def get_query_by_id(query_id):
    return Query.query.options(
                db.joinedload(Query.tags)
            ).filter(Query.id == query_id).first()

def create_query_obj(name,sql,interval,platform,version,description,value,shard,snapshot=False):
    return Query(name=name,sql=sql,interval=interval,platform=platform,version=version,description=description,value=value,shard=shard,snapshot=snapshot)

