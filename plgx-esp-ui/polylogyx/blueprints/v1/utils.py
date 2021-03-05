import json, sqlalchemy, six
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from functools import wraps
import datetime as dt
from operator import and_
from flask import jsonify, current_app, request, abort
from flask_restplus import reqparse, marshal
import unicodecsv as csv
from io import BytesIO
from flask import send_file

from polylogyx.models import Node, Settings, db, EmailRecipient, ResultLog, Rule, Alerts
from polylogyx.dao.v1 import rules_dao, packs_dao, alerts_dao, hosts_dao as node_dao, hosts_dao, queries_dao, \
    dashboard_dao
from polylogyx.util.constants import DEFAULT_EVENT_STATE_QUERIES
from polylogyx.constants import PolyLogyxServerDefaults

'''Common utils/ all methods used in blueprints folder will be defined here'''

process_guid_column = 'process_guid'
parent_process_guid_column = 'parent_process_guid'


def tag_name_format(Tags):
    '''used in packs queries nodes'''
    data = [tag.to_dict() for tag in Tags]
    return data


def get_body_data(request):
    return json.loads(request.data)


def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    # return datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S')
    return value.strftime("%Y-%m-%d") + ' ' + value.strftime("%H:%M:%S")


def validate_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.data:
            response = {}
            response['status'] = 'failure'
            response['message'] = 'Data missing'
            return jsonify(response)
        else:
            try:
                request.data = json.loads(request.data)
                return f(*args, **kwargs)
            except:
                current_app.logger.error("%s - Invalid data", request.remote_addr)
                abort(400)

        return f(*args, **kwargs)

    return decorated_function


def validate_command(request_data):
    response = {}
    types = ['file', 'process']
    status = 'failure'
    message = 'Invalid Data'

    for type in types:
        try:
            if request_data.get('target').get(type):

                node = Node.query.filter(
                    Node.host_identifier == request_data.get('target').get(type).get(
                        'device').get(
                        'hostname')).first()
                if node: return True, node
        except:
            status = 'failure'
            message = 'Please provide a valid command'

    response['status'] = status
    response['message'] = message
    return False, jsonify(response)


def validate_ip(s):
    a = s.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True


def save_or_update_setting(setting, v, k):
    if setting:
        setting.setting = v
        setting.update(setting)
    else:
        Settings.create(name=k, setting=v)


def save_email_recipients(emails):
    emailListStr = None
    emailRecipients = []
    db.session.query(EmailRecipient).update({EmailRecipient.status: 'inactive'})
    for email in emails:
        emailRecipients.append(email)
        try:
            emailRecipient = db.session.query(EmailRecipient).filter(EmailRecipient.recipient == email).one()
        except MultipleResultsFound:
            emailRecipient = None
        except NoResultFound:
            emailRecipient = None

        if (emailRecipient):
            emailRecipient.status = 'active'
            emailRecipient.updated_at = dt.datetime.utcnow()
            # EmailRecipient.update(emailRecipient)

        else:
            emailRecipient = EmailRecipient()
            emailRecipient.status = 'active'
            emailRecipient.created_at = dt.datetime.now()
            emailRecipient.recipient = email
            emailRecipient.updated_at = dt.datetime.utcnow()
            # EmailRecipient.create(emailRecipient)
        db.session.add(emailRecipient)
        if emailListStr:
            emailListStr = emailListStr + ',' + email
        else:
            emailListStr = email
    db.session.commit()
    alerter_plugins = current_app.config.get('POLYLOGYX_ALERTER_PLUGINS', {})
    if 'email' in alerter_plugins:
        emailAlerter = alerter_plugins['email']
        emailAlerter[1]['recipients'] = [
            emailListStr,
        ]
        alerter_plugins['email'] = emailAlerter
    current_app.config['POLYLOGYX_ALERTER_PLUGINS'] = alerter_plugins

    current_app.config['EMAIL_RECIPIENTS'] = emailRecipients
    response_json = {}
    response_json['status'] = 'success'
    response_json['message'] = 'Successfully configured email recipients'


def json_serial(obj):
    if isinstance(obj, (dt.datetime, dt.date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


# request parsing function
def requestparse(args_to_add, type_list, help_list, required = None, choices = None, default = None, nullable_list = None):
    """function which parse the request body data into dictionary"""
    if not required: required = [True for i in args_to_add]
    if not choices: choices = [None for i in args_to_add]
    if not default: default = [None for i in args_to_add]
    if not nullable_list: nullable_list = [None for i in args_to_add]

    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument('x-access-token', location='headers', type=str, help="JWT Access token(From Login API)", required=True)
    for i in range(len(args_to_add)):
        if required[i]:
            nullable = False
            if nullable_list[i]:
                nullable = True
        else:
            nullable = True
        if not args_to_add[i]=='file':
            if type_list[i] == list:
                parser.add_argument(args_to_add[i], action='append', help=help_list[i], required=required[i],
                                    choices=choices[i], default=default[i], nullable=nullable)
            else:
                parser.add_argument(args_to_add[i], type=type_list[i], help=help_list[i], required=required[i], choices=choices[i], default=default[i], nullable=nullable)
        else:
            if type_list[i] == list:
                parser.add_argument(args_to_add[i], action='append', help=help_list[i], required=required[i], location = 'files', nullable=nullable)
            else:
                parser.add_argument(args_to_add[i], type=type_list[i], help=help_list[i], required=required[i],
                                    location='files', nullable=nullable)
    return parser


def respcls(message, status=None, data=None):
    '''returns a response dictionary needed to apply to wrappers'''
    if (status is not None and data is not None):
        return {'message': message, 'status': status, 'data': data}
    elif status is not None:
        return {'message': message, 'status': status}
    else:
        return {'message': message}


def save_intel_alert(data, source, severity, query_name, uuid, columns, node_id):
    from polylogyx.models import Alerts
    from collections import namedtuple
    IntelMatch = namedtuple('IntelMatch', ['intel', 'result', 'node'])

    alertsObj = Alerts.create(message=columns, query_name=query_name, result_log_uid=uuid,
                              node_id=node_id,
                              rule_id=1, type=Alerts.THREAT_INTEL, source=source, source_data=data, recon_queries={},
                              severity=severity)

    intel = {'type': Alerts.THREAT_INTEL, 'source': source, 'severity': severity, 'query_name': query_name}
    intel_match = IntelMatch(intel=intel,
                             result=columns,
                             node=node_id)
    node = db.session.query(Node).filter(Node.id == node_id).first().to_dict()
    return send_alert(node, None, intel_match)


def send_alert(node, rule_match, intel_match):
    from polylogyx.models import current_app as app
    from polylogyx.plugins import AbstractAlerterPlugin
    alerters = app.config.get('POLYLOGYX_ALERTER_PLUGINS', {})

    for name, (plugin, config) in alerters.items():
        package, classname = plugin.rsplit('.', 1)
        from importlib import import_module
        module = import_module(package)
        klass = getattr(module, classname, None)

        if klass is None:
            raise ValueError('Could not find a class named "{0}" in package "{1}"'.format(classname, package))

        if not issubclass(klass, AbstractAlerterPlugin):
            raise ValueError('{0} is not a subclass of AbstractAlerterPlugin'.format(name))
        alerter_obj = klass(config)

        try:
            alerter_obj.handle_alert(node, rule_match, intel_match)
            return True
        except Exception as e:
            current_app.logger.error(e)
            return False


def add_pack_through_json_data(args):
    from polylogyx.wrappers.v1 import parent_wrappers
    from polylogyx.utils import create_tags, validate_osquery_query
    from flask_restplus import marshal

    if 'tags' in args:
        tags = args['tags'].split(',')
    else:
        tags = []
    name = args['name']
    queries = args['queries']
    category = args['category']
    platform = args.get('platform', None)
    version = args.get('version', None)
    description = args.get('description', None)
    shard = args.get('shard', None)

    pack = packs_dao.get_pack_by_name(name)
    if not pack:
        pack = packs_dao.add_pack(name, category, platform, version, description, shard)

    for query_name, query in queries.items():
        if not validate_osquery_query(query['query']):
            message = ('Invalid osquery query: "{0}"'.format(query['query']))
            return marshal({'message': message}, parent_wrappers.failure_response_parent)
        q = queries_dao.get_query_by_name(query_name)

        if not q:
            q = queries_dao.add_query(query_name, **query)
            pack.queries.append(q)
            current_app.logger.debug("Adding new query %s to pack %s",
                                     q.name, pack.name)
            continue
        else:
            if q.sql == query['query']:
                current_app.logger.debug("Adding existing query %s to pack %s",
                                         q.name, pack.name)
                pack.queries.append(q)
            else:
                q2 = queries_dao.add_query(query_name, **query)
                current_app.logger.debug(
                    "Created another query named %s, but different sql: %r vs %r",
                    query_name, q2.sql.encode('utf-8'), q.sql.encode('utf-8'))
                pack.queries.append(q2)

            if q in pack.queries:
                continue

    if pack:
        if tags:
            pack.tags = create_tags(*tags)
        pack.save()
    return pack


def get_node_id_by_host_id(host_identifier):
    node = node_dao.get_node_by_host_identifier(host_identifier)
    if node:
        return node.id


def get_host_id_by_node_id(node_id):
    node = node_dao.getNodeById(node_id)
    if node:
        return node.host_identifier


def get_nodes_for_host_id(host_identifier):
    return Node.query.filter(Node.host_identifier == host_identifier).all()


def get_queries_or_packs_of_node(node_id):
    return db.session.query(
        ResultLog.name).distinct(ResultLog.name). \
        filter(ResultLog.node_id == (node_id)). \
        all()


def get_results_by_query(startPage, perPageRecords, node_id, name, args=None):
    searchTerm = None
    columns = []
    columnsDefined = False
    try:
        startPage = int(args['start'])
        perPageRecords = int(args['length'])
        if 'search[value]' in args and (args['search[value]'] != ""):
            searchTerm = (args['search[value]'])
        if (args['columns[0][data]']):
            columnsDefined = True
    except:
        print('error in request')
    results = []
    count = db.session.query(ResultLog).filter(
        and_(ResultLog.name == name, and_(ResultLog.node_id == node_id, ResultLog.action != 'removed'))).count()
    countFiltered = count

    if searchTerm:
        queryCountStr = "select count(distinct id) from result_log join jsonb_each_text(result_log.columns) e on true where  node_id='" + str(
            node_id) + "' and e.value ilike " + "'%" + searchTerm + "%'" + " and name=" + "'" + name + "'" + " and action!='removed'"

        filtered_quer = db.engine.execute(sqlalchemy.text(queryCountStr))
        for r in filtered_quer:
            countFiltered = r[0]

        queryStr = "select distinct id,columns from result_log join jsonb_each_text(result_log.columns) e on true where  node_id='" + str(
            node_id) + "' and e.value ilike " + "'%" + searchTerm + "%'" + " and name=" + "'" + name + "'" + " and action!='removed' order by id desc OFFSET " + str(
            startPage) + "  LIMIT " + str(perPageRecords)
        record_query = db.engine.execute(sqlalchemy.text(queryStr))
        for r in record_query:
            results.append(r[1])

    else:
        record_query = db.session.query(ResultLog.columns).filter(
            and_(ResultLog.node_id == (node_id), and_(ResultLog.name == name, ResultLog.action != 'removed'))).order_by(
            sqlalchemy.desc(ResultLog.id)).offset(
            startPage).limit(
            perPageRecords).all()
        results = [r for r, in record_query]

        if results:
            firstRecord = results[0]

            TO_CAPTURE_COlUMNS = []
            if 'action' in firstRecord:
                if 'PROC_' in firstRecord['action']:
                    TO_CAPTURE_COlUMNS = ['utc_time', 'action', 'path', 'parent_path']
                elif 'Close' in firstRecord['action'] or 'Accept' in firstRecord['action'] or 'Connect' in firstRecord[
                    'action']:
                    TO_CAPTURE_COlUMNS = ['utc_time', 'action', 'process_name', 'protocol', 'local_address',
                                          'local_port', 'remote_address' 'remote_port']
                elif 'DELETE' in firstRecord['action'] or 'READ' in firstRecord['action'] or 'WRITE' in firstRecord[
                    'action']:
                    TO_CAPTURE_COlUMNS = ['utc_time', 'action', 'process_name', 'md5', 'target_path']

            elif 'event_type' in firstRecord:
                if 'dns_req' == firstRecord['event_type'] or 'dns_res' == firstRecord['event_type']:
                    TO_CAPTURE_COlUMNS = ['domain_name', 'resolved_ip', 'utc_time', 'request_type', 'request_class']
                elif 'http_req' == firstRecord['event_type']:
                    TO_CAPTURE_COlUMNS = ['utc_time', 'url', 'remote_port', 'process_name']

            if len(TO_CAPTURE_COlUMNS) == 0:
                for key in firstRecord.keys():
                    columns.append({'data': key, 'title': key})
            else:
                columns.append({"className": 'details-control',
                                "orderable": False,
                                "data": None,
                                "defaultContent": ''})
                for key in firstRecord.keys():
                    if key in TO_CAPTURE_COlUMNS:
                        columns.append({'data': key, 'title': key})

    output = {}
    try:
        output['sEcho'] = str(int(request.values['sEcho']))
    except:
        print('error in echo')
    output['iRecordsFiltered'] = str(countFiltered)
    output['iTotalRecords'] = str(count)
    output['pageLength'] = str(perPageRecords)

    output['iTotalDisplayRecords'] = str(countFiltered)
    aaData_rows = results

    # add additional rows here that are not represented in the database
    # aaData_row.append(('''''' % (str(row[ self.index ]))).replace('\\', ''))
    if not columnsDefined:
        output['columns'] = columns
    output['aaData'] = aaData_rows

    return output


class UnSupportedSeachColumn(Exception):
    pass


class RuleParser:

    def parse_condition(self, d):
        from polylogyx.rules import OPERATOR_MAP

        op = d['operator']
        value = d['value']

        # If this is a "column operator" - i.e. operating on a particular
        # value in a column - then we need to give a custom extraction
        # function that knows how to get this value from a query.
        column_name = None
        if d['field'] == 'column':
            # Strip 'column_' prefix to get the 'real' operator.
            if op.startswith('column_'):
                op = op[7:]
            if isinstance(value, six.string_types):
                column_name = value
            else:
                # The 'value' array will look like ['column_name', 'actual value']
                column_name, value = value
        klass = OPERATOR_MAP.get(op)
        if not klass:
            raise ValueError("Unsupported operator: {0}".format(op))

        inst = self.make_condition(klass, d['field'], value, column_name=column_name)
        return inst

    def parse_group(self, d):
        from polylogyx.rules import AndCondition, OrCondition

        if len(d['rules']) == 0:
            raise ValueError("A group contains no rules")
        upstreams = [self.parse(r) for r in d['rules']]
        condition = d['condition']
        if condition == 'AND' or condition == 'and':
            return self.make_condition(AndCondition, upstreams)
        elif condition == 'OR' or condition == 'or':
            return self.make_condition(OrCondition, upstreams)

        raise ValueError("Unknown condition: {0}".format(condition))

    def parse(self, d):
        if 'condition' in d:
            return self.parse_group(d)
        return self.parse_condition(d)

    def make_condition(self, klass, *args, **kwargs):
        from polylogyx.rules import BaseCondition

        """
        Memoizing constructor for conditions.  Uses the input config as the cache key.
        """
        conditions = {}

        # Calculate the memoization key.  We do this by creating a 3-tuple of
        # (condition class name, args, kwargs).  There is some nuance to this,
        # though: we need to put args/kwargs in the right format.  We
        # recursively iterate through lists/dicts and convert them to tuples,
        # and extract the memoization key from instances of BaseCondition.
        def tupleify(obj):
            if isinstance(obj, BaseCondition):
                return obj.__network_memo_key
            elif isinstance(obj, tuple):
                return tuple(tupleify(x) for x in obj)
            elif isinstance(obj, list):
                return tuple(tupleify(x) for x in obj)
            elif isinstance(obj, dict):
                items = ((tupleify(k), tupleify(v)) for k, v in obj.items())
                return tuple(sorted(items))
            else:
                return obj

        args_tuple = tupleify(args)
        kwargs_tuple = tupleify(kwargs)

        key = (klass.__name__, args_tuple, kwargs_tuple)
        if key in conditions:
            return conditions[key]

        # Instantiate the condition class.  Also, save the memoization key on
        # the class, so it can be retrieved (above).
        inst = klass(*args, **kwargs)
        inst.__network_memo_key = key

        # Save the condition
        conditions[key] = inst
        return inst


class SearchParser:

    def parse_condition(self, d):
        from polylogyx.search_rules import OPERATOR_MAP

        op = d['operator']
        value = d['value']

        # If this is a "column operator" - i.e. operating on a particular
        # value in a column - then we need to give a custom extraction
        # function that knows how to get this value from a query.
        column_name = None
        if d['field'] == 'column':
            # Strip 'column_' prefix to get the 'real' operator.
            if op.startswith('column_'):
                op = op[7:]
            if isinstance(value, six.string_types):
                column_name = value
            else:
                # The 'value' array will look like ['column_name', 'actual value']
                column_name, value = value
        if not column_name:
            column_name = d['field']
        klass = OPERATOR_MAP.get(op)

        if not klass:
            raise ValueError("Unsupported operator: {0}".format(op))

        if column_name not in PolyLogyxServerDefaults.search_supporting_columns:
            raise UnSupportedSeachColumn("Unsupported column '{}'".format(column_name))

        inst = self.make_condition(klass, d['field'], value, column_name=column_name)
        return inst

    def parse_group(self, d):
        from polylogyx.search_rules import AndCondition, OrCondition

        if len(d['rules']) == 0:
            raise ValueError("A group contains no rules")
        upstreams = [self.parse(r) for r in d['rules']]
        condition = d['condition']
        if condition == 'AND' or condition == 'and':
            return self.make_condition(AndCondition, upstreams)
        elif condition == 'OR' or condition == 'or':
            return self.make_condition(OrCondition, upstreams)

        raise ValueError("Unknown condition: {0}".format(condition))

    def parse(self, d):
        if 'condition' in d:
            return self.parse_group(d)
        return self.parse_condition(d)

    def make_condition(self, klass, *args, **kwargs):
        from polylogyx.search_rules import BaseCondition

        """
        Memoizing constructor for conditions.  Uses the input config as the cache key.
        """
        conditions = {}

        # Calculate the memoization key.  We do this by creating a 3-tuple of
        # (condition class name, args, kwargs).  There is some nuance to this,
        # though: we need to put args/kwargs in the right format.  We
        # recursively iterate through lists/dicts and convert them to tuples,
        # and extract the memoization key from instances of BaseCondition.
        def tupleify(obj):
            if isinstance(obj, BaseCondition):
                return obj.__network_memo_key
            elif isinstance(obj, tuple):
                return tuple(tupleify(x) for x in obj)
            elif isinstance(obj, list):
                return tuple(tupleify(x) for x in obj)
            elif isinstance(obj, dict):
                items = ((tupleify(k), tupleify(v)) for k, v in obj.items())
                return tuple(sorted(items))
            else:
                return obj

        args_tuple = tupleify(args)
        kwargs_tuple = tupleify(kwargs)

        key = (klass.__name__, args_tuple, kwargs_tuple)
        if key in conditions:
            return conditions[key]

        # Instantiate the condition class.  Also, save the memoization key on
        # the class, so it can be retrieved (above).
        inst = klass(*args, **kwargs)
        inst.__network_memo_key = key

        # Save the condition
        conditions[key] = inst
        return inst


def get_response(results):
    from polylogyx.wrappers.v1 import parent_wrappers
    if results:
        firstRecord = results[0][0]
        headers = []
        for key in firstRecord.keys():
            headers.append(key)

        bio = BytesIO()
        writer = csv.writer(bio)
        writer.writerow(headers)

        for data in results:
            row = []
            row.extend([data[0].get(column) for column in headers])
            writer.writerow(row)

        bio.seek(0)

        response = send_file(
            bio,
            mimetype='text/csv',
            as_attachment=True,
            attachment_filename='alert_source_results.csv'
        )
        response.direct_passthrough = False
        return response
    else:
        return marshal(respcls("Data couldn't find for the alert source given!", "failure"),
                       parent_wrappers.common_response_wrapper, skip_none=True)


def add_rule_name_to_alerts_response(dictionary_list_data):
    from polylogyx.dao import rules_dao
    for dict_item in dictionary_list_data:
        if dict_item['type'] == 'rule':
            if 'rule_name' not in dict_item:
                dict_item['rule_name'] = rules_dao.get_rule_name_by_id(dict_item['rule_id'])
    return dictionary_list_data


def fetch_alert_node_query_status():
    limits = 5
    rules = dashboard_dao.get_rules_data(limits)
    nodes = dashboard_dao.get_host_data(limits)
    queries = dashboard_dao.get_querries(limits)

    alerts = {}
    top_five_alerts = {}

    # rules count
    rule = []
    for row_list in rules:
        rule_ele = {'rule_name': row_list[1], 'count': row_list[2]}
        rule.append(rule_ele)
    top_five_alerts['rule'] = rule

    # host count
    hosts = []
    for row_list in nodes:
        host_ele = {'host_identifier': row_list[1], 'count': row_list[2]}
        hosts.append(host_ele)
    top_five_alerts['hosts'] = hosts

    # queries count
    query = []
    for row_list in queries:
        query_ele = {'query_name': row_list[0], 'count': row_list[1]}
        query.append(query_ele)
    top_five_alerts['query'] = query
    alerts['top_five'] = top_five_alerts

    # fetching alerts count by severity and type
    alert_count = dashboard_dao.get_alert_count()

    alert_name = {'ioc': {'INFO': 0, 'LOW': 0, 'WARNING': 0, 'CRITICAL': 0},
                  'rule': {'INFO': 0, 'LOW': 0, 'WARNING': 0, 'CRITICAL': 0},
                  'virustotal': {'INFO': 0, 'LOW': 0, 'WARNING': 0, 'CRITICAL': 0},
                  'ibmxforce': {'INFO': 0, 'LOW': 0, 'WARNING': 0, 'CRITICAL': 0},
                  'alienvault': {'INFO': 0, 'LOW': 0, 'WARNING': 0, 'CRITICAL': 0}}
    for alert in alert_count:
        alert_name[alert[0]][alert[1]] = alert[2]

    for key in alert_name.keys():
        alert_name[key]['TOTAL'] = alert_name[key]['INFO'] + alert_name[key]['LOW'] + alert_name[key]['WARNING'] + \
                                   alert_name[key]['CRITICAL']

    alerts['source'] = alert_name

    return alerts


def fetch_dashboard_data():
    distribution_and_status = {}
    counts = dashboard_dao.get_platform_count()

    distribution_and_status['hosts_platform_count'] = counts

    checkin_interval = current_app.config['POLYLOGYX_CHECKIN_INTERVAL']
    current_time = dt.datetime.utcnow() - checkin_interval
    online_nodes = dashboard_dao.get_online_node_count(current_time)
    offline_nodes = dashboard_dao.get_offline_node_count(current_time)

    distribution_and_status['hosts_status_count'] = {'online': online_nodes, 'offline': offline_nodes}

    return distribution_and_status


def get_alerts_data(source, start_date, end_date, node, rule_id):
    try:
        data = []
        alerts_severity = alerts_dao.get_alerts_severity_with_id_timestamp(source, start_date, end_date, node, rule_id)

        for alert in alerts_severity:
            color = ""
            if alert[1]:
                if alert[1] == Rule.WARNING:
                    color = "green-m"
                elif alert[1] == Rule.INFO:
                    color = ""
                elif alert[1] == Rule.CRITICAL:
                    color = "yellow"

            data.append({"start": alert[2].timestamp() * 1000, "content": "",
                         "event_id": alert[0], "className": color})
        return data
    except Exception as e:
        print(e, 'error in request')


def get_results_by_alert_source(start, limit, source, searchterm="", resolved=False, event_ids=None, start_date=None,
                                end_date=None, node_id=None, query_name=None, rule_id=None, events_count=False):
    """ Alerts by source Result Set. """
    if resolved:
        filter = alerts_dao.resolved_alert()
    else:
        filter = alerts_dao.non_resolved_alert()

    base_query = alerts_dao.get_record_query_by_dsc_order(filter, source, searchterm, event_ids, node_id, query_name, rule_id, events_count)

    if not resolved and start_date and end_date:
        base_query = base_query.filter(Alerts.created_at >= start_date).filter(Alerts.created_at <= end_date)

    count = base_query.count()

    total_count = alerts_dao.get_record_query_total_count(filter, source, node_id, query_name, rule_id)
    record_query = base_query.offset(start).limit(limit).all()
    alerts = []
    for alert_log_pair in record_query:
        if events_count:
            alert = alert_log_pair[0].as_dict()
            alert['aggregated_events_count'] = alert_log_pair[1]
        else:
            alert = alert_log_pair.as_dict()
        alert['alerted_entry'] = alert.pop('message')
        alert['intel_data'] = alert.pop('source_data')
        alert['hostname'] = node_dao.getAllNodeById(alert['node_id']).display_name

        if alert['source'] == 'rule':
            alert['rule'] = {'name': rules_dao.get_rule_name_by_id(alert['rule_id']), 'id': alert['rule_id']}
            del alert['intel_data']
        elif source == 'self' or source == 'IOC' or source == 'ioc':
            del alert['rule_id']
            del alert['intel_data']
            if 'rule' in alert:
                del alert['rule']
        else:
            del alert['rule_id']
            if 'rule' in alert:
                del alert['rule']
        alerts.append(alert)

    output = {'count': count, 'total_count': total_count, 'results': alerts}
    return output


def time_in_alert(alert):
    try:
        if 'time' in alert.message:
            time = alert.message['time']
            time = int(time)
            return time
    except Exception as e:
        print(e)


def alerts_details(alert):
    from polylogyx.wrappers.v1.alert_wrappers import alerts_wrapper

    alerts_data = marshal(alert, alerts_wrapper)
    if alerts_data['source'] == 'rule':
        alerts_data['rule'] = {'name': rules_dao.get_rule_name_by_id(alerts_data['rule_id']),
                               'id': alerts_data['rule_id']}
    host = hosts_dao.getNodeById(alerts_data['node_id'])
    alerts_data['hostname'] = host.display_name
    alerts_data['platform'] = host.platform

    return alerts_data


def get_platform(alert):
    platform = alert.node.platform
    if platform not in ['windows', 'freebsd', 'darwin']:
        platform = 'linux'

    return platform


def get_start_dat_end_date(args):
    end_date = dt.datetime.utcnow()
    end_date = dt.datetime.strptime(end_date.today().strftime('%Y-%m-%d'), '%Y-%m-%d')+dt.timedelta(days=1)
    start_date = dt.datetime.strptime(end_date.today().strftime('%Y-%m-%d'), '%Y-%m-%d') - dt.timedelta(weeks=1)+dt.timedelta(days=1)
    if 'date' in args and args['date']:
        type = args['type']
        duration = args['duration']
        date = dt.datetime.strptime(args['date'], '%Y-%m-%d')
        difference_time = 0
        if duration == 1:
            difference_time = dt.timedelta(hours=1)
        elif duration == 2:
            difference_time = dt.timedelta(days=1)
        elif duration == 3:
            difference_time = dt.timedelta(weeks=1)
        elif duration == 4:
            difference_time = dt.timedelta(days=30)
        if type == 1:
            start_date = date
            end_date = start_date + difference_time
        elif type == 2:
            end_date = date
            start_date = end_date - difference_time
    return start_date+dt.timedelta(days=1), end_date+dt.timedelta(days=1)
