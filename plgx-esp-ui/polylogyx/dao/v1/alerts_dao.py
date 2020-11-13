from polylogyx.models import db, Alerts, ResultLog, Rule, Node, NodeQueryCount, AlertLog
from polylogyx.util.constants import DEFAULT_PROCESS_GRAPH_QUERIES

from sqlalchemy import func, cast, INTEGER, desc, or_, and_, asc
from sqlalchemy.orm import lazyload
import sqlalchemy


process_guid_column = 'process_guid'
parent_process_guid_column = 'parent_process_guid'


def get_alert_by_id(alert_id):
    return Alerts.query.filter_by(id=alert_id).first()


def get_alert_source(source, start_date, end_date, node, rule_id):
    qs = db.session.query(Alerts.message).filter(Alerts.source == source)
    if node:
        qs = qs.filter(Alerts.node_id == node.id)
    if rule_id:
        qs = qs.filter(Alerts.rule_id == rule_id)
    if start_date and end_date:
        qs = qs.filter(Alerts.created_at >= start_date).filter(Alerts.created_at <= end_date)
    return qs.order_by(desc(Alerts.id)).all()


def get_distinct_alert_source(resolved, start_date, end_date, node, rule_id):
    if not resolved:
        qs = db.session.query(Alerts).with_entities(Alerts.source, db.func.count(Alerts.source)).filter(
            or_(Alerts.status == None, Alerts.status != Alerts.RESOLVED)).filter(
            and_(Node.state != Node.REMOVED, Node.state != Node.DELETED)).join(Node,
            Alerts.node_id == Node.id).order_by(Alerts.source).group_by(Alerts.source)
    else:
        qs = db.session.query(Alerts).with_entities(Alerts.source, db.func.count(Alerts.source)).filter(
            Alerts.status == Alerts.RESOLVED).filter(
            and_(Node.state != Node.REMOVED, Node.state != Node.DELETED)).join(Node, Alerts.node_id == Node.id).order_by(
            Alerts.source).group_by(Alerts.source)
    if node:
        qs = qs.filter(Alerts.node_id == node.id)
    if rule_id:
        qs = qs.filter(Alerts.rule_id == rule_id)
    if start_date and end_date:
        qs = qs.filter(Alerts.created_at >= start_date).filter(Alerts.created_at <= end_date)
    return qs.all()


def get_alerts_severity_with_id_timestamp(source, start_date, end_date, node, rule_id):
    qs = db.session.query(Alerts).with_entities(Alerts.id, Alerts.severity, Alerts.created_at).filter(
        Alerts.source == source).filter(
        or_(Alerts.status == None, Alerts.status != Alerts.RESOLVED)).filter(
        and_(Node.state != Node.REMOVED, Node.state != Node.DELETED)).join(Node, Alerts.node_id == Node.id).order_by(desc(Alerts.id))
    if node:
        qs = qs.filter(Alerts.node_id == node.id)
    if rule_id:
        qs = qs.filter(Alerts.rule_id == rule_id)
    if start_date and end_date:
        qs = qs.filter(Alerts.created_at >= start_date).filter(Alerts.created_at <= end_date)
    return qs.all()


def get_alerts_by_alert_id(alert_id):
    return Alerts.query.filter_by(id=alert_id).first()


def edit_alerts_status_by_alert(alert_ids, status=False):
    if status:
        Alerts.query.filter(Alerts.id.in_(alert_ids)).update({Alerts.status: Alerts.RESOLVED}, synchronize_session=False)
    else:
        Alerts.query.filter(Alerts.id.in_(alert_ids)).update({Alerts.status: Alerts.OPEN}, synchronize_session=False)
    db.session.commit()
    return


def non_resolved_alert():
    return or_(Alerts.status == None, Alerts.status != Alerts.RESOLVED)


def resolved_alert():
    return Alerts.status == Alerts.RESOLVED


def get_record_query_by_dsc_order(filter, source, searchTerm='', event_ids=None, node_id=None, query_name=None, rule_id=None, events_count=None):
    if events_count:
        query_set = db.session.query(Alerts, db.func.count(AlertLog.id)).outerjoin(AlertLog)
    else:
        query_set = db.session.query(Alerts)
    query_set = query_set.filter(filter).filter(and_(Node.state != Node.REMOVED, Node.state != Node.DELETED)).join(Node, Alerts.node_id == Node.id)
    if event_ids:
        query_set = query_set.filter(Alerts.id.in_(event_ids))
    if node_id:
        query_set = query_set.filter(Alerts.node_id == node_id)
    if query_name:
        query_set = query_set.filter(Alerts.query_name == query_name)
    if rule_id:
        query_set = query_set.filter(Alerts.rule_id == rule_id)
    if source:
        query_set = query_set.filter(Alerts.source == source)
    if searchTerm:
        if source and source == Alerts.RULE:
            query_set = query_set.filter(or_(
                Alerts.severity.ilike('%' + searchTerm + '%'),
                Node.node_info['computer_name'].astext.ilike('%' + searchTerm + '%'),
                Node.node_info['display_name'].astext.ilike('%' + searchTerm + '%'),
                Node.node_info['hostname'].astext.ilike('%' + searchTerm + '%'),
                Rule.name.ilike('%' + searchTerm + '%'),
                cast(Alerts.created_at, sqlalchemy.String).ilike('%' + searchTerm + '%')
            )).join(Rule, Alerts.rule_id == Rule.id)
        else:
            query_set = query_set.filter(or_(
                Alerts.severity.ilike('%' + searchTerm + '%'),
                Node.node_info['computer_name'].astext.ilike('%' + searchTerm + '%'),
                Node.node_info['display_name'].astext.ilike('%' + searchTerm + '%'),
                Node.node_info['hostname'].astext.ilike('%' + searchTerm + '%'),
                cast(Alerts.created_at, sqlalchemy.String).ilike('%' + searchTerm + '%')
            ))
    if events_count:
        query_set = query_set.group_by(Alerts.id)
    return query_set.order_by(desc(Alerts.id))


def get_record_query_total_count(filter, source, node_id=None, query_name=None, rule_id=None):
    base_query = db.session.query(Alerts)
    if source:
        base_query = base_query.filter(Alerts.source == source)
    if node_id:
        base_query = base_query.filter(Alerts.node_id == node_id)
    if query_name:
        base_query = base_query.filter(Alerts.query_name == query_name)
    if rule_id:
        base_query = base_query.filter(Alerts.rule_id == rule_id)
    return base_query.filter(filter).filter(and_(Node.state != Node.REMOVED, Node.state != Node.DELETED)).join(Node, Alerts.node_id == Node.id).count()


def get_all_events_of_an_alert(alert):
    return db.session.query(AlertLog).filter(AlertLog.alert_id == alert.id).all()
