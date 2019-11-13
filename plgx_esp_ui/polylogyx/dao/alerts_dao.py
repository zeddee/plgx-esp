from polylogyx.models import db, Alerts, ResultLog

from sqlalchemy import func,cast,INTEGER
from sqlalchemy.sql import label


def get_alerts_by_node(node):
    return Alerts.query.filter(Alerts.node == node).all()

def get_alerts_by_rule(rule):
    return Alerts.query.filter(Alerts.rule == rule).all()

def get_alerts_by_query(query_name):
    return Alerts.query.filter(Alerts.query_name == query_name).all()

def get_all_alerts():
    return Alerts.query.all()

def result_log_query(scheduled_query,time,alert):
    return db.session.query(ResultLog.columns).filter(
                    cast(ResultLog.columns["time"].astext, INTEGER) <= time + scheduled_query[
                        'before_event_interval']).filter(
                    cast(ResultLog.columns["time"].astext, INTEGER) >= time - scheduled_query[
                        'after_event_interval']).filter(
                    ResultLog.name == scheduled_query['name']).filter(ResultLog.action != 'REMOVED').filter(
                    ResultLog.node_id == alert.node.id).all()

def get_alert_by_id(alert_id):
    return Alerts.query.filter_by(id=alert_id).first()

def get_alerts_for_input(node=None,rule_id=None,query_name=None):
    message = None
    if node :
        if query_name and rule_id:
            data = Alerts.query.filter(Alerts.query_name == query_name, Alerts.rule_id == rule_id, Alerts.node == node).all()
            if not data: message = "host_identifier or query_name or rule_id is invalid or might be there is no matching data"
        elif query_name:
            data=Alerts.query.filter(Alerts.query_name == query_name, Alerts.node == node).all()
            if not data: message = "host_identifier or query_name is invalid or might be there is no matching data"
        elif rule_id:
            data=Alerts.query.filter(Alerts.rule_id == rule_id, Alerts.node == node).all()
            if not data: message = "host_identifier or rule_id is invalid or might be there is no matching data"
        else:
            data=Alerts.query.filter(Alerts.node == node).all()
            if not data: message = "host_identifier is invalid or might be there is no matching data"
    else :
        if query_name and rule_id:
            data=Alerts.query.filter(Alerts.query_name == query_name, Alerts.rule_id == rule_id).all()
            if not data: message = "query_name or rule_id is invalid or might be there is no matching data"
        elif query_name:
            data=Alerts.query.filter(Alerts.query_name == query_name).all()
            if not data: message = "query_name is invalid or might be there is no matching data"
        elif rule_id:
            data=Alerts.query.filter(Alerts.rule_id == rule_id).all()
            if not data: message = "rule_id is invalid or might be there is no matching data"
        else:
            data=None
            message = "no data is given to view alerts"
    return (data,message)