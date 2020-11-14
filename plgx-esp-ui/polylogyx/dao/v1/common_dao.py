from polylogyx.models import ResultLog, Options, db, Node, OsquerySchema,VirusTotalAvEngines
from polylogyx.constants import PolyLogyxServerDefaults

from operator import and_
from sqlalchemy import desc


def del_result_log_obj(since):
    return ResultLog.query.filter(ResultLog.timestamp < since).delete()


def options_query():
    return Options.query.filter(Options.name == PolyLogyxServerDefaults.plgx_config_all_options).first()


def options_filter_by_key(k):
    return Options.query.filter(Options.name == k).first()


def create_option(k,v):
    return Options.create(name=k, option=v)


def create_option_by_option(option):
    return Options.create(name=PolyLogyxServerDefaults.plgx_config_all_options, option=option)


def result_log_query(lines, type, node_id, query_name, start, limit):
    base_qs = db.session.query(ResultLog.node_id, ResultLog.name, ResultLog.columns).filter(ResultLog.action != "removed").filter(ResultLog.node_id.in_(node_id)).filter(ResultLog.name == query_name).filter(
      ResultLog.columns[type].astext.in_(lines)).filter(and_(Node.state!=Node.REMOVED, Node.state!=Node.DELETED)).join(Node, ResultLog.node_id == Node.id)
    results = base_qs.offset(start).limit(limit).all()
    count = base_qs.count()
    return {'count':count, 'results':results}


def result_log_query_for_export(lines, type, node_id, query_name):
    return db.session.query(ResultLog.columns).filter(ResultLog.name == query_name).filter(ResultLog.node_id.in_(node_id)).filter(
        ResultLog.columns[type].astext.in_(lines)).filter(and_(Node.state!=Node.REMOVED, Node.state!=Node.DELETED)).join(Node, ResultLog.node_id == Node.id).all()


def result_log_search_results(filter,node_ids,query_name,offset,limit):
    base_qs = db.session.query(ResultLog.columns).filter(*filter).filter(ResultLog.node_id.in_(node_ids)).filter(
    ResultLog.name == query_name).filter(and_(Node.state!=Node.REMOVED, Node.state!=Node.DELETED)).join(Node, ResultLog.node_id == Node.id)
    count = base_qs.count()
    results = base_qs.offset(offset).limit(limit).all()
    return {'count':count, 'results':results}


def result_log_query_count(lines,type):
    return db.session.query(ResultLog.node_id, ResultLog.name, db.func.count(ResultLog.columns)).filter(
        ResultLog.columns[type].astext.in_(lines)).filter(and_(Node.state!=Node.REMOVED, Node.state!=Node.DELETED)).join(Node, ResultLog.node_id == Node.id).group_by(ResultLog.node_id,ResultLog.name).all()


def result_log_search_results_count(filter):
    return db.session.query(ResultLog.node_id, ResultLog.name, db.func.count(ResultLog.columns)).filter(*filter).filter(and_(Node.state!=Node.REMOVED, Node.state!=Node.DELETED))\
        .join(Node, ResultLog.node_id == Node.id).group_by(ResultLog.node_id, ResultLog.name).all()


def fetch_virus_total_av_engines():
    av_engines=db.session.query(VirusTotalAvEngines.name,VirusTotalAvEngines.status).all()
    data={}
    for av_engine in av_engines:
        data[av_engine.name]={}
        data[av_engine.name]['status']=av_engine.status
    return data


def update_av_engine_status(av_engines):
    for key in list(av_engines.keys()):
        av_engine=db.session.query(VirusTotalAvEngines).filter(VirusTotalAvEngines.name==key).first()
        if av_engine:
            av_engine.update(status=av_engines[key]['status'])
    av_engine_data={"av_engines":av_engines}
    return av_engine_data


def results_with_indicators_filtered(lines, type, node_ids, query_name, start, limit, start_date, end_date):
    base_qs = db.session.query(ResultLog).filter(ResultLog.action != "removed").filter(
      ResultLog.columns[type].astext.in_(lines)).filter(and_(Node.state!=Node.REMOVED, Node.state!=Node.DELETED)).join(Node, ResultLog.node_id == Node.id)
    if node_ids:
        base_qs = base_qs.filter(ResultLog.node_id.in_(node_ids))
    if query_name:
        base_qs = base_qs.filter(ResultLog.name == query_name)
    base_qs = base_qs.filter(ResultLog.timestamp >= start_date).filter(ResultLog.timestamp <= end_date).order_by(desc(ResultLog.timestamp))
    results = base_qs.offset(start).limit(limit).all()
    count = base_qs.count()
    return {'count': count, 'results': [result.as_dict() for result in results]}


def results_with_indicators_filtered_to_export(lines, type, node_ids, query_name, start_date, end_date):
    query_set = db.session.query(ResultLog.columns).filter(ResultLog.columns[type].astext.in_(lines)).filter(and_(Node.state!=Node.REMOVED, Node.state!=Node.DELETED)).join(Node, ResultLog.node_id == Node.id)
    if node_ids:
        query_set = query_set.filter(ResultLog.node_id.in_(node_ids))
    if query_name:
        query_set = query_set.filter(ResultLog.name == query_name)
    query_set = query_set.filter(ResultLog.timestamp >= start_date).filter(ResultLog.timestamp <= end_date)
    return query_set.all()


def record_query(node_id, query_name):
    return db.session.query(ResultLog.columns).filter(
            and_(ResultLog.node_id == (node_id), and_(ResultLog.name == query_name, ResultLog.action != 'removed'))).filter(and_(Node.state!=Node.REMOVED, Node.state!=Node.DELETED)).join(Node, ResultLog.node_id == Node.id).all()


def result_log_search_query(filter, node_ids, query_name, offset, limit, start_date, end_date):
    base_qs = db.session.query(ResultLog).filter(*filter).filter(and_(Node.state!=Node.REMOVED, Node.state!=Node.DELETED)).join(Node, ResultLog.node_id == Node.id)
    if node_ids:
        base_qs = base_qs.filter(ResultLog.node_id.in_(node_ids))
    if query_name:
        base_qs = base_qs.filter(ResultLog.name == query_name)
    base_qs = base_qs.filter(ResultLog.timestamp >= start_date).filter(ResultLog.timestamp <= end_date).order_by(desc(ResultLog.timestamp))
    results = base_qs.offset(offset).limit(limit).all()
    count = base_qs.count()
    return {'count': count, 'results': [result.as_dict() for result in results]}


def get_osquery_agent_schema():
    return OsquerySchema.query.order_by(OsquerySchema.name.asc()).all()
