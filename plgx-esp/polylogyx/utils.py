# -*- coding: utf-8 -*-
import ast
import datetime as dt
import json
import sqlite3
import string
import threading
import uuid
from collections import namedtuple

import jinja2
from jinja2 import Markup, Template
from operator import itemgetter
from os.path import basename, join, splitext

from flask_mail import Message, Mail
from sqlalchemy import func

from polylogyx.plugins import AbstractAlerterPlugin
from polylogyx.constants import DEFAULT_PLATFORMS, PolyLogyxServerDefaults, public_server

import pkg_resources
import requests
import six
from flask import current_app, flash, render_template

from polylogyx.database import db
from polylogyx.models import (
    DistributedQuery, DistributedQueryTask,
    Node, Pack, Query, ResultLog, querypacks,
    Options, Tag, DefaultQuery, DefaultFilters, StatusLog)

Field = namedtuple('Field', ['name', 'action', 'columns', 'timestamp','uuid'])

# Read DDL statements from our package
schema = pkg_resources.resource_string('polylogyx', join('resources', 'osquery_schema.sql'))
schema = schema.decode('utf-8')
schema = [x for x in schema.strip().split('\n') if not x.startswith('--')]

# SQLite in Python will complain if you try to use it from multiple threads.
# We create a threadlocal variable that contains the DB, lazily initialized.
osquery_mock_db = threading.local()


def assemble_configuration(node):
    platform = node.platform
    if platform not in DEFAULT_PLATFORMS:
        platform = 'linux'
    platform_filter = DefaultFilters.query.filter(DefaultFilters.platform == platform).first()
    configuration = {}
    if platform_filter and platform_filter.filters:
        configuration = platform_filter.filters
    configuration['options'] = assemble_options(node)
    configuration['schedule'] = assemble_schedule(node)
    configuration['packs'] = assemble_packs(node)

    return configuration


def assemble_options(node):
    options = {'disable_watchdog': True, 'logger_tls_compress': True}

    # https://github.com/facebook/osquery/issues/2048#issuecomment-219200524
    if current_app.config['POLYLOGYX_EXPECTS_UNIQUE_HOST_ID']:
        options['host_identifier'] = 'uuid'
    else:
        options['host_identifier'] = 'hostname'

    options['schedule_splay_percent'] = 10
    existing_option = Options.query.filter(Options.name == PolyLogyxServerDefaults.plgx_config_all_options).first()
    if existing_option:
        existing_option_value = json.loads(existing_option.option)
        options = merge_two_dicts(options, existing_option_value)

    return options


def assemble_file_paths(node):
    file_paths = {}
    for file_path in node.file_paths.options(db.lazyload('*')):
        file_paths.update(file_path.to_dict())
    return file_paths


def assemble_schedule(node):
    schedule = {}
    for query in node.queries.options(db.lazyload('*')):
        schedule[query.name] = query.to_dict()
    platform = node.platform
    if platform not in DEFAULT_PLATFORMS:
        platform = 'linux'

    for default_query in DefaultQuery.query.filter(DefaultQuery.status == True).filter(
            DefaultQuery.platform == platform).all():
        schedule[default_query.name] = default_query.to_dict()

    return schedule


def assemble_packs(node):
    packs = {}
    for pack in node.packs.join(querypacks).join(Query) \
            .options(db.contains_eager(Pack.queries)).all():
        packs[pack.name] = pack.to_dict()
    return packs


def assemble_distributed_queries(node):
    '''
    Retrieve all distributed queries assigned to a particular node
    in the NEW state. This function will change the state of the
    distributed query to PENDING, however will not commit the change.
    It is the responsibility of the caller to commit or rollback on the
    current database session.
    '''
    now = dt.datetime.utcnow()
    pending_query_count = 0
    query_recon_count = db.session.query(db.func.count(DistributedQueryTask.id)) \
        .filter(
        DistributedQueryTask.node == node,
        DistributedQueryTask.status == DistributedQueryTask.NEW,
        DistributedQueryTask.priority == DistributedQueryTask.HIGH,

    )
    for r in query_recon_count:
        pending_query_count = r[0]
    if pending_query_count > 0:
        query = db.session.query(DistributedQueryTask) \
            .join(DistributedQuery) \
            .filter(
            DistributedQueryTask.node == node,
            DistributedQueryTask.status == DistributedQueryTask.NEW,
            DistributedQuery.not_before < now,
            DistributedQueryTask.priority == DistributedQueryTask.HIGH,

        ).options(
            db.lazyload('*'),
            db.contains_eager(DistributedQueryTask.distributed_query)
        )
    else:
        query = db.session.query(DistributedQueryTask) \
            .join(DistributedQuery) \
            .filter(
            DistributedQueryTask.node == node,
            DistributedQueryTask.status == DistributedQueryTask.NEW,
            DistributedQuery.not_before < now,
            DistributedQueryTask.priority == DistributedQueryTask.LOW,
        ).options(
            db.lazyload('*'),
            db.contains_eager(DistributedQueryTask.distributed_query)
        ).limit(1)

    queries = {}
    for task in query:
        if task.sql:
            queries[task.guid] = task.sql
        else:
            queries[task.guid] = task.distributed_query.sql
        task.update(status=DistributedQueryTask.PENDING,
                    timestamp=now,
                    commit=False)

        # add this query to the session, but don't commit until we're
        # as sure as we possibly can be that it's been received by the
        # osqueryd client. unfortunately, there are no guarantees though.
        db.session.add(task)
    return queries


def merge_two_dicts(x, y):
    if not x:
        x = {}
    if not y:
        y = {}
    z = x.copy()  # start with x's keys and values
    z.update(y)  # modifies z with y's keys and values & returns None
    return z


def create_query_pack_from_upload(upload):
    '''
    Create a pack and queries from a query pack file. **Note**, if a
    pack already exists under the filename being uploaded, then any
    queries defined here will be added to the existing pack! However,
    if a query with a particular name already exists, and its sql is
    NOT the same, then a new query with the same name but different id
    will be created (as to avoid clobbering the existing query). If its
    sql is identical, then the query will be reused.

    '''
    # The json package on Python 3 expects a `str` input, so we're going to
    # read the body and possibly convert to the right type
    body = upload.data.read()
    if not isinstance(body, six.string_types):
        body = body.decode('utf-8')

    try:
        data = json.loads(body)
    except ValueError:
        flash(u"Could not load pack as JSON - ensure it is JSON encoded",
              'danger')
        return None
    else:
        if 'queries' not in data:
            flash(u"No queries in pack", 'danger')
            return None

        name = splitext(basename(upload.data.filename))[0]
        pack = Pack.query.filter(Pack.name == name).first()

    if not pack:
        current_app.logger.debug("Creating pack %s", name)
        pack = Pack.create(name=name, **data)

    for query_name, query in data['queries'].items():
        if not validate_osquery_query(query['query']):
            flash('Invalid osquery query: "{0}"'.format(query['query']), 'danger')
            return None

        q = Query.query.filter(Query.name == query_name).first()

        if not q:
            q = Query.create(name=query_name, **query)
            pack.queries.append(q)
            current_app.logger.debug("Adding new query %s to pack %s",
                                     q.name, pack.name)
            continue

        if q in pack.queries:
            continue

        if q.sql == query['query']:
            current_app.logger.debug("Adding existing query %s to pack %s",
                                     q.name, pack.name)
            pack.queries.append(q)
        else:
            q2 = Query.create(name=query_name, **query)
            current_app.logger.debug(
                "Created another query named %s, but different sql: %r vs %r",
                query_name, q2.sql.encode('utf-8'), q.sql.encode('utf-8'))
            pack.queries.append(q2)

    else:
        pack.save()
        flash(u"Imported query pack {0}".format(pack.name), 'success')

    return pack


def get_node_health(node):
    checkin_interval = current_app.config['POLYLOGYX_CHECKIN_INTERVAL']
    if isinstance(checkin_interval, (int, float)):
        checkin_interval = dt.timedelta(seconds=checkin_interval)
    if (dt.datetime.utcnow() - node.last_checkin) > checkin_interval:
        return u'danger'
    else:
        return ''


# Not super-happy that we're duplicating this both here and in the JS, but I
# couldn't think of a nice way to pass from JS --> Python (or the other
# direction).
PRETTY_OPERATORS = {
    'equal': 'equals',
    'not_equal': "doesn't equal",
    'begins_with': 'begins with',
    'not_begins_with': "doesn't begins with",
    'contains': 'contains',
    'not_contains': "doesn't contain",
    'ends_with': 'ends with',
    'not_ends_with': "doesn't end with",
    'is_empty': 'is empty',
    'is_not_empty': 'is not empty',
    'less': 'less than',
    'less_or_equal': 'less than or equal',
    'greater': 'greater than',
    'greater_or_equal': 'greater than or equal',
    'matches_regex': 'matches regex',
    'not_matches_regex': "doesn't match regex",
}


def pretty_operator(cond):
    return PRETTY_OPERATORS.get(cond, cond)


PRETTY_FIELDS = {
    'query_name': 'Query name',
    'action': 'Action',
    'host_identifier': 'Host identifier',
    'timestamp': 'Timestamp',
}


def pretty_field(field):
    return PRETTY_FIELDS.get(field, field)


_js_escapes = {
    '\\': '\\u005C',
    '\'': '\\u0027',
    '"': '\\u0022',
    '>': '\\u003E',
    '<': '\\u003C',
    '&': '\\u0026',
    '=': '\\u003D',
    '-': '\\u002D',
    ';': '\\u003B',
    u'\u2028': '\\u2028',
    u'\u2029': '\\u2029'
}
# Escape every ASCII character with a value less than 32.
_js_escapes.update(('%c' % z, '\\u%04X' % z) for z in range(32))


def jinja2_escapejs_filter(value):
    retval = []
    if not value:
        return ''
    else:
        for letter in value:
            if letter in _js_escapes.keys():
                retval.append(_js_escapes[letter])
            else:
                retval.append(letter)

        return jinja2.Markup("".join(retval))


# Since 'string.printable' includes control characters
PRINTABLE = string.ascii_letters + string.digits + string.punctuation + ' '


def quote(s, quote='"'):
    buf = [quote]
    for ch in s:
        if ch == quote or ch == '\\':
            buf.append('\\')
            buf.append(ch)
        elif ch == '\n':
            buf.append('\\n')
        elif ch == '\r':
            buf.append('\\r')
        elif ch == '\t':
            buf.append('\\t')
        elif ch in PRINTABLE:
            buf.append(ch)
        else:
            # Hex escape
            buf.append('\\x')
            buf.append(hex(ord(ch))[2:])

    buf.append(quote)
    return ''.join(buf)


def _carve(string):
    return str(string).title()


def create_mock_db():
    mock_db = sqlite3.connect(':memory:')
    mock_db.create_function("carve", 1, _carve)

    for ddl in schema:
        mock_db.execute(ddl)
    cursor = mock_db.cursor()
    cursor.execute("SELECT name,sql FROM sqlite_master WHERE type='table';")
    from polylogyx.constants import PolyLogyxServerDefaults

    extra_schema = current_app.config.get('POLYLOGYX_EXTRA_SCHEMA', [])
    for ddl in extra_schema:
        mock_db.execute(ddl)
    for osquery_table in cursor.fetchall():
        PolyLogyxServerDefaults.POLYLOGYX_OSQUERY_SCHEMA_JSON[osquery_table[0]] = osquery_table[1]
    return mock_db


def create_tags(*tags):
    values = []
    existing = []

    # create a set, because we haven't yet done our association_proxy in
    # sqlalchemy

    for value in (v.strip() for v in set(tags) if v.strip()):
        tag = Tag.query.filter(Tag.value == value).first()
        if not tag:
            values.append(Tag.create(value=value))
        else:
            existing.append(tag)
    else:
        if values:
            flash(u"Created tag{0} {1}".format(
                's' if len(values) > 1 else '',
                ', '.join(tag.value for tag in values)),
                'info')
    return values + existing


def validate_osquery_query(query):
    # Check if this thread has an instance of the SQLite database
    db = getattr(osquery_mock_db, 'db', None)
    if db is None:
        db = create_mock_db()
        osquery_mock_db.db = db

    try:
        db.execute(query)
    except sqlite3.Error:
        current_app.logger.exception("Invalid query: %s", query)
        return False

    return True


def learn_from_result(result, node):
    if not result['data']:
        return

    capture_columns = set(
        map(itemgetter(0),
            current_app.config['POLYLOGYX_CAPTURE_NODE_INFO']
            )
    )

    if not capture_columns:
        return

    node_info = node.get('node_info', {})
    orig_node_info = node_info.copy()

    for _, action, columns, _, _, in extract_results(result):
        # only update columns common to both sets
        for column in capture_columns & set(columns):

            cvalue = node_info.get(column)  # current value
            value = columns.get(column)

            if action == 'removed' and (cvalue is None or cvalue != value):
                pass
            elif action == 'removed' and cvalue == value:
                node_info.pop(column)
            elif action == 'added' and (cvalue is None or cvalue != value):
                node_info[column] = value

    # only update node_info if there's actually a change

    if orig_node_info == node_info:
        return

    node = Node.get_by_id(node['id'])
    node.update(node_info=node_info)
    return

def process_result(result, node):
    if not result['data']:
        return
    result_logs=[]
    subject_dn = []

    for name, action, columns, timestamp,uuid in extract_results(result):
        if 'subject_dn' in columns and columns['subject_dn'] and columns['subject_dn'] != '':
            subject_dn.append(columns['subject_dn'])
        else:
            result_logs.append( ResultLog(name=name,uuid=uuid, action=action, columns=columns, timestamp=timestamp, node_id=node['id']))
    return  result_logs



def extract_results(result):
    """
    extract_results will convert the incoming log data into a series of Fields,
    normalizing and/or aggregating both batch and event format into batch
    format, which is used throughout the rest of polylogyx.
    """
    if not result['data']:
        return

    timefmt = '%a %b %d %H:%M:%S %Y UTC'
    strptime = dt.datetime.strptime

    for entry in result['data']:

        if 'uuid' not in entry:
            entry['uuid']=str(uuid.uuid4())

        name = entry['name']

        timestamp = strptime(entry['calendarTime'], timefmt)

        if 'columns' in entry:
            yield Field(name=name,
                        action=entry['action'],
                        columns=entry['columns'],
                        timestamp=timestamp,uuid=entry['uuid'])

        elif 'diffResults' in entry:
            added = entry['diffResults']['added']
            removed = entry['diffResults']['removed']
            for (action, items) in (('added', added), ('removed', removed)):
                # items could be "", so we're still safe to iter over
                # and ensure we don't return an empty value for columns
                for columns in items:
                    yield Field(name=name,
                                action=action,
                                columns=columns,
                                timestamp=timestamp,uuid=entry['uuid'])

        elif 'snapshot' in entry:
            for columns in entry['snapshot']:
                yield Field(name=name,
                            action='snapshot',
                            columns=columns,
                            timestamp=timestamp,uuid=entry['uuid'])

        else:
            current_app.logger.error("Encountered a result entry that "
                                     "could not be processed! %s",
                                     json.dumps(entry))


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, dt.datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


def render_column(value, column):
    renders = current_app.config.get('DOORMAN_COLUMN_RENDER', {})
    if column not in renders:
        return value

    template = renders[column]

    try:
        if callable(template):
            return template(value)
        else:
            template = Template(template, autoescape=True)
            rendered = template.render(value=value)

            # return a markup object so that the template where this is
            # rendered is not escaped again

            return Markup(rendered)
    except Exception:
        current_app.logger.exception(
            "Failed to render %s, returning original value",
            column
        )
        return value


class Serializer(object):
    @staticmethod
    def serialize(object):
        return json.dumps(object, default=lambda o: o.__dict__.values()[0])


def check_and_save_intel_alert(scan_type, scan_value, data, source, severity):
    from polylogyx.models import Alerts, db
    result_logs = ResultLog.query.filter(ResultLog.columns[scan_type].astext == scan_value).all()
    for result_log in result_logs:
        alert_count = db.session.query(func.count(Alerts.id)).filter(Alerts.source == source).filter(
            Alerts.result_log_uid == result_log.uuid).scalar()
        if alert_count == 0:
            save_intel_alert(data=data, source=source, severity=severity, query_name=result_log.name,
                             uuid=result_log.uuid, columns=result_log.columns, node_id=result_log.node_id)


def save_intel_alert(data, source, severity, query_name, uuid, columns, node_id):
    from polylogyx.models import Alerts
    alert = Alerts.create(message=columns, query_name=query_name, result_log_uid=uuid,
                          node_id=node_id,
                          rule_id=None, type=Alerts.THREAT_INTEL, source=source, source_data=data, recon_queries={},
                          severity=severity)
    from polylogyx.rules import IntelMatch
    intel = {'type': Alerts.THREAT_INTEL, 'source': source, 'severity': severity, 'query_name': query_name}
    json_data = ""
    if data:
        json_data = json.dumps(data)
    intel_match = IntelMatch(intel=intel,
                             result=columns, data=json_data, alert_id=alert.id,
                             node=node_id)
    node = db.session.query(Node).filter(Node.id == node_id).first().to_dict()
    send_alert(node, None, intel_match)


def send_alert(node, rule_match, intel_match):
    from polylogyx.models import current_app as app
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
        alerters[name] = klass(config)
    for alerter in alerters:
        try:
            alerters[alerter].handle_alert(node, rule_match, intel_match)
        except Exception as e:
            current_app.logger.error(e)


def flatten_json(input):
    output = dict(input)
    if 'columns' in output:
        for key, value in output['columns'].items():
            output[key] = value
            output.pop('columns', None)

    return output


def append_node_information_to_result_log(node, input):
    output = dict(input)
    try:
        output['platform'] = node['platform']
        output['last_checkin'] = node['last_checkin']
        output['is_active'] = node['is_active']
        output['last_ip'] = node['last_ip']

        if 'os_info' in node:
            os_info = node['os_info']
            output['osname'] = os_info.get("name", "")
            output['version'] = os_info['version']
        if 'node_info' in node:
            node_info = node['node_info']

            output['computername'] = node_info['computer_name']
            output['hardware_model'] = node_info['hardware_model']
            output['hardware_vendor'] = node_info['hardware_vendor']
            output['cpu_physical_cores'] = node_info['cpu_physical_cores']
    except Exception as e:
        current_app.logger.error(e)

    return output


def append_node_and_rule_information_to_alert(node, input):
    output = dict(input)
    try:
        output['platform'] = node['platform']
        output['is_active'] = node['is_active']
        output['last_ip'] = node['last_ip']
        output['platform'] = node['platform']

        if 'os_info' in node:
            os_info = node['os_info']
            output['osname'] = os_info['name']
        if 'network_info' in node:
            network_info = node['network_info']
            output['macaddress'] = network_info['mac_address']
        if 'node_info' in node:
            node_info = node['node_info']

            output['computername'] = node_info['computer_name']
            output['hardware_model'] = node_info['hardware_model']
    except Exception as e:
        print(e)
    return output



def extract_result_logs(result):
    """
    extract_results will convert the incoming log data into a series of Fields,
    normalizing and/or aggregating both batch and event format into batch
    format, which is used throughout the rest of polylogyx.
    """
    Field = namedtuple('Field', ['name', 'action', 'columns', 'timestamp', 'uuid','node_id'])

    for data in result:

        if not data.uuid:
            data.uuid = str(uuid.uuid4())

        yield Field(name=data.name,
                    action=data.action,
                    columns=data.columns,
                    timestamp=data.timestamp, uuid=data.uuid, node_id=data.node_id)


