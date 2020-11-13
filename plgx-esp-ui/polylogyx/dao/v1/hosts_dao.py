import datetime as dt

from flask import current_app

from sqlalchemy import or_, text, desc, and_, cast, not_
import sqlalchemy

from polylogyx.models import db, Node, ResultLog, Tag, StatusLog, NodeQueryCount, Alerts, Rule


def get_all_nodes():
    return Node.query.filter(and_(Node.state!=Node.REMOVED, Node.state!=Node.DELETED)).order_by(desc(Node.id)).all()


def get_node_by_host_identifier(host_identifier):
    return db.session.query(Node).filter(
            or_(Node.host_identifier == host_identifier, Node.node_key == host_identifier)).filter(Node.state!=Node.DELETED).first()


def get_disable_node_by_host_identifier(host_identifier):
    return db.session.query(Node).filter(Node.state == Node.REMOVED).filter(
        or_(Node.host_identifier == host_identifier, Node.node_key == host_identifier)).first()


def getDisableNodeById(node_id):
    return db.session.query(Node).filter(and_(Node.id == node_id, Node.state == Node.REMOVED)).first()


def get_all_node_by_host_identifier(host_identifier):
    return db.session.query(Node).filter(or_(
        Node.host_identifier == host_identifier, Node.node_key == host_identifier, Node.state!=Node.DELETED, Node.state!=Node.REMOVED)).first()


def get_host_id_and_name_by_node_id(node_id):
    node = getNodeById(node_id)
    if node:
        return {'hostname':node.display_name, 'host_identifier':node.host_identifier}


def getNodeById(node_id):
    return db.session.query(Node).filter(and_(Node.id == node_id)).filter(Node.state!=Node.DELETED).first()


def getAllNodeById(node_id):
    return db.session.query(Node).filter(Node.id == node_id).filter(Node.state!=Node.DELETED).first()


def getHostNameByNodeId(node_id):
    query = db.session.query(Node).filter(Node.id == node_id).filter(Node.state!=Node.DELETED).first()
    if query:
        return query.display_name



def get_result_log_count(node_id):
    return db.session.query(
        NodeQueryCount.query_name, NodeQueryCount.total_results).filter(NodeQueryCount.node_id == node_id).all()


def get_result_log_of_a_query(node_id, query_name, start, limit, searchterm):
    import sqlalchemy
    count_qs_total = db.session.query(NodeQueryCount.total_results).filter(NodeQueryCount.node_id==node_id).filter(NodeQueryCount.query_name==query_name).first()

    if searchterm:
        count_qs = db.engine.execute(sqlalchemy.text(
            "select count( id) from result_log join jsonb_each_text(result_log.columns) e on true where  node_id='" + str(
            node_id) + "' and e.value ilike " + "'%" + searchterm + "%'" + " and name=" + "'" + query_name + "'" + " and action!='removed' group by id order by id desc;"))
        query_results = db.engine.execute(sqlalchemy.text(
            "select  id,timestamp,action,columns from result_log join jsonb_each_text(result_log.columns) e on true where  node_id='" + str(
            node_id) + "' and e.value ilike " + "'%" + searchterm + "%'" + " and name=" + "'" + query_name + "'" + " and action!='removed' group by id order by id desc OFFSET " + str(
            start) + "  LIMIT " + str(limit) + ";"))
        query_count = count_qs.rowcount

    else:

        query_results = db.engine.execute(sqlalchemy.text(
            "select  id,timestamp,action,columns from result_log  where  node_id='" + str(
            node_id) + "' and name=" + "'" + query_name + "'" + " and action!='removed' order by id desc OFFSET " + str(
            start) + "  LIMIT " + str(limit) + ";"))


    total_count =0
    if count_qs_total:
        total_count=count_qs_total[0]
    if not searchterm:
        query_count=total_count
    return (query_count, query_results, total_count)


def extendNodesByNodeKeyList(nodeKeyList):
    return Node.query.filter(or_(
                        Node.node_key.in_(nodeKeyList), Node.host_identifier.in_(nodeKeyList))).all()


def extendNodesByTag(tags):
    return Node.query.filter(
                        Node.tags.any(
                            Tag.value.in_(tags))).all()


def node_result_log_search_results(filter, node_id, query_name):
    return db.session.query(ResultLog.columns).filter(*filter).filter(ResultLog.node_id == node_id).filter(ResultLog.name == query_name).all()


def node_result_log_results(node_id, query_name):
    return db.session.query(ResultLog.columns).filter(ResultLog.node_id == node_id).filter(ResultLog.name == query_name).all()


def get_hosts_filtered_status_platform_count():
    from sqlalchemy import and_
    linux_filter = [~Node.platform.in_(('windows', 'darwin'))]

    checkin_interval = current_app.config['POLYLOGYX_CHECKIN_INTERVAL']
    current_time = dt.datetime.utcnow() - checkin_interval
    linux_online = db.session.query(db.func.count(Node.id)).filter(or_(Node.is_active,
            Node.last_checkin > current_time)).filter(and_(*linux_filter)).filter(and_(Node.state!=Node.REMOVED, Node.state!=Node.DELETED)).scalar()
    linux_offline = db.session.query(db.func.count(Node.id)).filter(and_(not_(Node.is_active),
            Node.last_checkin < current_time)).filter(and_(*linux_filter)).filter(and_(Node.state!=Node.REMOVED, Node.state!=Node.DELETED)).scalar()

    windows_online = db.session.query(db.func.count(Node.id)).filter(or_(Node.is_active,
            Node.last_checkin > current_time)).filter(and_(Node.platform == "windows", Node.state!=Node.REMOVED, Node.state!=Node.DELETED)).scalar()
    windows_offline = db.session.query(db.func.count(Node.id)).filter(and_(not_(Node.is_active),
            Node.last_checkin < current_time)).filter(and_(Node.platform == "windows", Node.state!=Node.REMOVED, Node.state!=Node.DELETED)).scalar()

    darwin_online = db.session.query(db.func.count(Node.id)).filter(or_(Node.is_active,
            Node.last_checkin > current_time)).filter(and_(Node.platform == "darwin", Node.state!=Node.REMOVED, Node.state!=Node.DELETED)).scalar()
    darwin_offline = db.session.query(db.func.count(Node.id)).filter(and_(not_(Node.is_active),
            Node.last_checkin < current_time)).filter(and_(Node.platform == "darwin", Node.state!=Node.REMOVED, Node.state!=Node.DELETED)).scalar()
    return {'windows':{'online': windows_online, 'offline': windows_offline}, 'linux':{'online': linux_online, 'offline': linux_offline}, 'darwin':{'online': darwin_online, 'offline': darwin_offline}}


def get_hosts_paginated(status, platform, searchterm="", enabled=True, alerts_count=False):
    import sqlalchemy
    from polylogyx.blueprints.v1.utils import node_is_active

    filter = []
    if platform == 'linux':
        filter.append(~Node.platform.in_(('windows', 'darwin')))
    else:
        filter.append(Node.platform == platform)

    checkin_interval = current_app.config['POLYLOGYX_CHECKIN_INTERVAL']
    if alerts_count:
        query_set = db.session.query(Node, db.func.count(Alerts.id)).outerjoin(Alerts, and_(Alerts.node_id == Node.id, or_(Alerts.status == None, Alerts.status != Alerts.RESOLVED)))
    else:
        query_set = db.session.query(Node)
    if platform:
        query_set = query_set.filter(*filter)
    if enabled:
        query_set = query_set.filter(and_(Node.state!=Node.REMOVED, Node.state!=Node.DELETED))
    else:
        query_set = query_set.filter(Node.state == Node.REMOVED)
    if searchterm:
        query_set = query_set.filter(or_(
            Node.node_info['display_name'].astext.ilike('%' + searchterm + '%'),
            Node.node_info['computer_name'].astext.ilike('%' + searchterm + '%'),
            Node.node_info['hostname'].astext.ilike('%' + searchterm + '%'),
            Node.os_info['name'].astext.ilike('%' + searchterm + '%'),
            cast(Node.last_ip, sqlalchemy.String).ilike('%' + searchterm + '%'),
            Node.tags.any(Tag.value.in_([searchterm]))
        )
        )
    if status is not None:
        if status:
            query_set = query_set.filter(or_(Node.is_active,dt.datetime.utcnow() - Node.last_checkin < checkin_interval))
        else:
            query_set = query_set.filter(and_(not_(Node.is_active),dt.datetime.utcnow() - Node.last_checkin > checkin_interval))
    if alerts_count:
        query_set = query_set.group_by(Node)
    return query_set.order_by(desc(Node.is_active or node_is_active(Node)), desc(Node.id))


def get_hosts_total_count(status, platform, enabled=True):
    import sqlalchemy
    filter = []
    if platform == 'linux':
        filter.append(~Node.platform.in_(('windows', 'darwin')))
    else:
        filter.append(Node.platform == platform)

    checkin_interval = current_app.config['POLYLOGYX_CHECKIN_INTERVAL']
    if platform:
        qs = Node.query.filter(*filter)
    else:
        qs = Node.query
    if enabled:
        qs = qs.filter(and_(Node.state != Node.REMOVED, Node.state != Node.DELETED))
    else:
        qs = qs.filter(Node.state == Node.REMOVED)
    if status is not None:
        if status:
            qs = qs.filter(or_(Node.is_active,dt.datetime.utcnow() - Node.last_checkin < checkin_interval))
        else:
            qs = qs.filter(and_(not_(Node.is_active),dt.datetime.utcnow() - Node.last_checkin > checkin_interval))
    return qs.count()


def get_status_logs_of_a_node(node, searchterm=''):
    return StatusLog.query.filter_by(node=node).filter(or_(
        StatusLog.message.ilike('%' + searchterm + '%'),
        StatusLog.filename.ilike('%' + searchterm + '%'),
        StatusLog.version.ilike('%' + searchterm + '%'),
        cast(StatusLog.created, sqlalchemy.String).ilike('%' + searchterm + '%'),
        cast(StatusLog.line, sqlalchemy.String).ilike('%' + searchterm + '%'),
        cast(StatusLog.severity, sqlalchemy.String).ilike('%' + searchterm + '%')
        )
        )


def get_status_logs_total_count(node):
    return StatusLog.query.filter_by(node=node).count()


def get_tagged_nodes(tag_names):
    if tag_names is None:
        nodes = Node.query.filter(Node.tags == None).all()
    else:
        nodes = Node.query.filter(and_(Node.tags.any(Tag.value.in_(tag_names))), Node.state != Node.DELETED, Node.state != Node.REMOVED).all()
    return nodes


def is_tag_of_node(node, tag):
    if tag in node.tags:
        return True
    else:
        return False


def soft_remove_host(node):
    return node.update(state=Node.REMOVED, updated_at=dt.datetime.now())


def delete_host(node):
    return node.update(state=Node.DELETED, updated_at=dt.datetime.now())


def enable_host(node):
    return node.update(state=Node.ACTIVE, updated_at=dt.datetime.now())


def host_alerts_distribution_by_source(node):
    alert_count = db.session.query(Alerts.source, Alerts.severity, db.func.count(
        Alerts.id)).filter(or_(Alerts.status == None, Alerts.status != Alerts.RESOLVED))\
        .filter(Alerts.node_id == node.id).group_by(Alerts.source, Alerts.severity).all()

    alert_distro = {'ioc': {'INFO': 0, 'LOW': 0, 'WARNING': 0, 'CRITICAL': 0},
                  'rule': {'INFO': 0, 'LOW': 0, 'WARNING': 0, 'CRITICAL': 0},
                  'virustotal': {'INFO': 0, 'LOW': 0, 'WARNING': 0, 'CRITICAL': 0},
                  'ibmxforce': {'INFO': 0, 'LOW': 0, 'WARNING': 0, 'CRITICAL': 0},
                  'alienvault': {'INFO': 0, 'LOW': 0, 'WARNING': 0, 'CRITICAL': 0}}

    for alert in alert_count:
        alert_distro[alert[0]][alert[1]] = alert[2]

    for key in alert_distro.keys():
        alert_distro[key]['TOTAL'] = alert_distro[key]['INFO'] + alert_distro[key]['LOW'] + alert_distro[key]['WARNING'] + \
                                   alert_distro[key]['CRITICAL']
    return alert_distro


def host_alerts_distribution_by_rule(node):
    return db.session.query(Rule.name, db.func.count(Alerts.id)).filter(Alerts.source == Alerts.RULE)\
        .join(Alerts.rule).filter(or_(Alerts.status == None, Alerts.status != Alerts.RESOLVED))\
        .filter(Alerts.node_id == node.id).group_by(Rule.name).order_by(db.func.count(Alerts.rule_id).desc()).limit(5).all()

