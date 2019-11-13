# -*- coding: utf-8 -*-
import base64
import datetime as dt
import gzip
import json
import os
import random
import string
from functools import wraps
from io import BytesIO
from operator import itemgetter

from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import and_

from polylogyx.constants import PolyLogyxServerDefaults, KernelQueries, DefaultInfoQueries
from polylogyx.database import db
from polylogyx.extensions import log_tee
from polylogyx.models import (
    Node, Tag,
    DistributedQueryTask,
    StatusLog,
    CarveSession, CarvedBlock)
from polylogyx.tasks import notify_of_node_enrollment, save_distributed_query_data, build_carve_session_archive
from polylogyx.tasks import save_schedule_query_data

blueprint = Blueprint('api', __name__)


def node_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # in v1.7.4, the Content-Encoding header is set when
        # --logger_tls_compress=true
        remote_addr = get_ip()
        if 'Content-Encoding' in request.headers and \
                request.headers['Content-Encoding'] == 'gzip':
            request._cached_data = gzip.GzipFile(
                fileobj=BytesIO(request.get_data())).read()

        request_json = request.get_json()

        if not request_json or 'node_key' not in request_json:
            current_app.logger.error(
                "%s - Request did not contain valid JSON data. This could "
                "be an attempt to gather information about this endpoint "
                "or an automated scanner.",
                remote_addr
            )
            # Return nothing
            return ""

        node_key = request_json.get('node_key')
        node = Node.query.filter_by(node_key=node_key) \
            .options(db.lazyload('*')).first()

        if not node:
            current_app.logger.error(
                "%s - Could not find node with node_key %s",
                remote_addr, node_key
            )
            return jsonify(node_invalid=True)

        if not node.node_is_active():
            send_checkin_queries(node)
            current_app.logger.info(
                "[Checkin] Last checkin time for node : str(node.id) is  :: " + str(node.last_checkin))
            return jsonify(node_invalid=True)

        node.update(
            last_checkin=dt.datetime.utcnow(),
            last_ip=remote_addr,
            commit=False
        )

        return f(node=node, *args, **kwargs)

    return decorated_function


@blueprint.route('/')
def index():
    return '', 204


@blueprint.route('/enroll', methods=['POST', 'PUT'])
@blueprint.route('/v1/enroll', methods=['POST', 'PUT'])
def enroll():
    '''
    Enroll an endpoint with osquery.
    :returns: a `node_key` unique id. Additionally `node_invalid` will
        be true if the node failed to enroll.
    '''
    remote_addr = get_ip()
    request_json = request.get_json()
    if not request_json:
        current_app.logger.error(
            "%s - Request did not contain valid JSON data. This could "
            "be an attempt to gather information about this endpoint "
            "or an automated scanner.",
            remote_addr
        )
        # Return nothing
        return ""

    enroll_secret = request_json.get(
        current_app.config.get('POLYLOGYX_ENROLL_OVERRIDE', 'enroll_secret'))

    if not enroll_secret:
        current_app.logger.error(
            "%s - No enroll_secret provided by remote host",
            remote_addr
        )
        return jsonify(node_invalid=True)

    # If we pre-populate node table with a per-node enroll_secret,
    # let's query it now.

    if current_app.config.get('POLYLOGYX_ENROLL_SECRET_TAG_DELIMITER'):
        delimiter = current_app.config.get('POLYLOGYX_ENROLL_SECRET_TAG_DELIMITER')
        enroll_secret, _, enroll_tags = enroll_secret.partition(delimiter)
        enroll_tags = set([tag.strip() for tag in enroll_tags.split(delimiter)[:10]])
    else:
        enroll_secret, enroll_tags = enroll_secret, set()

    node = Node.query.filter(Node.enroll_secret == enroll_secret).first()

    if not node and enroll_secret not in current_app.config['POLYLOGYX_ENROLL_SECRET']:
        current_app.logger.error("%s - Invalid enroll_secret %s",
                                 remote_addr, enroll_secret
                                 )
        return jsonify(node_invalid=True)

    host_identifier = request_json.get('host_identifier')

    if node and node.enrolled_on:
        current_app.logger.warn(
            "%s - %s already enrolled on %s, returning existing node_key",
            remote_addr, node, node.enrolled_on
        )

        if node.host_identifier != host_identifier:
            current_app.logger.info(
                "%s - %s changed their host_identifier to %s",
                remote_addr, node, host_identifier
            )
            node.host_identifier = host_identifier

        node.update(
            last_checkin=dt.datetime.utcnow(),
            last_ip=remote_addr
        )
        send_checkin_queries(node)
        return jsonify(node_key=node.node_key, node_invalid=False)

    existing_node = None
    if host_identifier:
        existing_node = Node.query.filter(
            Node.host_identifier == host_identifier
        ).first()

    if existing_node and not existing_node.enroll_secret:
        current_app.logger.warning(
            "%s - Duplicate host_identifier %s, already enrolled %s",
            remote_addr, host_identifier, existing_node.enrolled_on
        )

        if current_app.config['POLYLOGYX_EXPECTS_UNIQUE_HOST_ID'] is True:
            current_app.logger.info(
                "%s - Unique host identification is true, %s already enrolled "
                "returning existing node key %s",
                remote_addr, host_identifier, existing_node.node_key
            )
            existing_node.update(
                last_checkin=dt.datetime.utcnow(),
                last_ip=remote_addr
            )
            send_checkin_queries(existing_node)
            return jsonify(node_key=existing_node.node_key, node_invalid=False)

    now = dt.datetime.utcnow()

    if node:
        node.update(host_identifier=host_identifier,
                    last_checkin=now,
                    enrolled_on=now,
                    last_ip=remote_addr)
    else:
        node = Node(host_identifier=host_identifier,
                    last_checkin=now,
                    enrolled_on=now,
                    last_ip=remote_addr)

        enroll_tags.update(current_app.config.get('POLYLOGYX_ENROLL_DEFAULT_TAGS', []))

        for value in sorted((t.strip() for t in enroll_tags if t)):
            tag = Tag.query.filter_by(value=value).first()
            if tag and tag not in node.tags:
                node.tags.append(tag)
            elif not tag:
                node.tags.append(Tag(value=value))

        node.save()

    current_app.logger.info("%s - Enrolled new node %s",
                            remote_addr, node
                            )
    notify_of_node_enrollment.apply_async(queue='default_queue_tasks', args = [node.to_dict()])
    # notify_of_node_enrollment.delay(node.to_dict())
    send_checkin_queries(node)
    update_system_details(request_json, node)

    return jsonify(node_key=node.node_key, node_invalid=False)


@blueprint.route('/start_uploads', methods=['POST', 'PUT'])
@blueprint.route('/v1/start_uploads', methods=['POST', 'PUT'])
@node_required
def upload_file(node=None):
    sid = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    data = request.get_json()
    CarveSession.create(node_id=node.id, session_id=sid, carve_guid=data['carve_id'], status=CarveSession.StatusInProgress,carve_size=data['carve_size'],
                       block_size=data['block_size'], block_count=data['block_count'],request_id=data['request_id'])

    return jsonify(session_id=sid)


@blueprint.route('/upload_blocks', methods=['POST', 'PUT'])
@blueprint.route('/v1/upload_blocks', methods=['POST', 'PUT'])
def upload_blocks():
    data = request.get_json()
    carveSession = CarveSession.query.filter(CarveSession.session_id == data['session_id']).first_or_404()

    if CarvedBlock.query.filter(and_(CarvedBlock.session_id==data['session_id'],CarvedBlock.block_id==data['block_id'])).first():
        return
    size = len(data['data'])

    CarvedBlock.create(data=data['data'],block_id=data['block_id'],session_id=data['session_id'],request_id=data['request_id'],size=size)
    carveSession.completed_blocks = carveSession.completed_blocks + 1

    # Are we expecting to receive more blocks?
    if carveSession.completed_blocks < carveSession.block_count:
        carveSession.update(carveSession)
        db.session.commit()

        print ('Gathering more blocks')
        return jsonify(node_invalid=False)
    carveSession.status=CarveSession.StatusBuilding
    # If not, let's reassemble everything

    db.session.commit()
    build_carve_session_archive.apply_async(queue='default_queue_tasks', args=[carveSession.session_id])
    # debug("File successfully carved to: %s" % out_file_name)

    return jsonify(node_invalid=False)


@blueprint.route('/config', methods=['POST', 'PUT'])
@blueprint.route('/v1/config', methods=['POST', 'PUT'])
@node_required
def configuration(node=None):
    '''
    Retrieve an osquery configuration for a given node.
    :returns: an osquery configuration file
    '''

    '''
    Retrieve an osquery configuration for a given node.
    :returns: an osquery configuration file
    '''
    remote_addr=get_ip()
    current_app.logger.info(
        "%s - %s checking in to retrieve a new configuration",
        remote_addr, node
    )
    config = node.get_config()

    # write last_checkin, last_ip
    node.update(last_config=dt.datetime.utcnow())
    db.session.add(node)
    db.session.commit()
    return jsonify(node_invalid=False, **config)


@blueprint.route('/log', methods=['POST', 'PUT'])
@blueprint.route('/v1/log', methods=['POST', 'PUT'])
@node_required
def logger(node=None):
    '''
    '''
    remote_addr=get_ip()
    data = request.get_json()
    log_type = data['log_type']
    log_level = current_app.config['POLYLOGYX_MINIMUM_OSQUERY_LOG_LEVEL']

    if current_app.debug:
        current_app.logger.debug(json.dumps(data, indent=2))

    if log_type == 'status':
        current_app.logger.info("[S] Status logs for node: " + str(node.id))

        log_tee.handle_status(data, host_identifier=node.host_identifier)
        status_logs = []
        for item in data.get('data', []):
            if int(item['severity']) < log_level:
                continue
            status_logs.append(StatusLog(node_id=node.id, **item))
        else:
            node.update(last_status=dt.datetime.utcnow())
            db.session.add(node)

            db.session.bulk_save_objects(status_logs)
            db.session.commit()

    elif log_type == 'result':
        current_app.logger.info("[S] Schedule query results for node: " + str(node.id))

        try:
            # db.session.bulk_save_objects(process_result(data, node.to_dict()))
            node.update(last_result=dt.datetime.utcnow())
            save_schedule_query_data.apply_async(queue='result_log_queue', args=[data, node.to_dict()])
            # save_schedule_query_data.delay(data, node.to_dict())
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(node_invalid=True)
        # handle_result.delay(data, node.host_identifier, node.to_dict())
        log_tee.handle_result(data, host_identifier=node.host_identifier)
        db.session.add(node)
        db.session.commit()

    else:
        current_app.logger.error("%s - Unknown log_type %r",
                                 remote_addr, log_type
                                 )
        current_app.logger.info(json.dumps(data))
        # still need to write last_checkin, last_ip
        db.session.add(node)
        db.session.commit()

    return jsonify(node_invalid=False)


@blueprint.route('/distributed/read', methods=['POST', 'PUT'])
@blueprint.route('/v1/distributed/read', methods=['POST', 'PUT'])
@node_required
def distributed_read(node=None):
    '''
    '''
    data = request.get_json()
    remote_addr=get_ip()

    current_app.logger.info(
        "%s - %s checking in to retrieve distributed queries",
        remote_addr, node
    )

    queries = node.get_new_queries()

    # need to write last_checkin, last_ip, and update distributed
    # query state
    node.update(last_query_read=dt.datetime.utcnow())

    db.session.add(node)
    db.session.commit()

    return jsonify(queries=queries, node_invalid=False)


@blueprint.route('/distributed/write', methods=['POST', 'PUT'])
@blueprint.route('/v1/distributed/write', methods=['POST', 'PUT'])
@node_required
def distributed_write(node=None):
    '''
    '''
    data = request.get_json()
    remote_addr=get_ip()

    if current_app.debug:
        current_app.logger.debug(json.dumps(data, indent=2))

    queries = data.get('queries', {})
    statuses = data.get('statuses', {})

    for guid, results in queries.items():
        task = DistributedQueryTask.query.filter(
            DistributedQueryTask.guid == guid,
            DistributedQueryTask.status == DistributedQueryTask.PENDING,
            DistributedQueryTask.node == node,
        ).first()

        if not task:
            current_app.logger.error(
                "%s - Got result for distributed query not in PENDING "
                "state: %s: %s",
                remote_addr, guid, json.dumps(data)
            )
            continue

        # non-zero status indicates sqlite errors

        if not statuses.get(guid, 0):
            status = DistributedQueryTask.COMPLETE
        else:
            current_app.logger.error(
                "%s - Got non-zero status code (%d) on distributed query %s",
                remote_addr, statuses.get(guid), guid
            )
            status = DistributedQueryTask.FAILED
        current_app.logger.info(
            'Got results for query: ' + str(task.distributed_query.id) + ' for node: ' + str(node.id))
        if task.save_results_in_db:
            if task.distributed_query.alert:
                task.data = results
            if 'system_info' in str(task.distributed_query.sql) and len(results) > 0:
                update_system_info(node, results[0])
            elif 'os_version' in str(task.distributed_query.sql) and len(results) > 0:
                update_os_info(node, results[0])

            elif KernelQueries.MAC_ADDRESS_QUERY in str(task.distributed_query.sql) and len(results) > 0:
                update_mac_address(node, results)
            elif task.distributed_query.description and (
                    (task.distributed_query.description in DefaultInfoQueries.DEFAULT_INFO_QUERIES) or (
                    task.distributed_query.description in DefaultInfoQueries.DEFAULT_HASHES_QUERY) or (
                            task.distributed_query.description in DefaultInfoQueries.DEFAULT_INFO_QUERIES_LINUX)):
                current_app.logger.info('saving in db')
                save_distributed_query_data.apply_async(queue='default_queue_tasks',
                                                        args=[node.id, results, task.distributed_query.description])
                data = {}
                node_data = {'id': node.id}
                if node.node_info and 'computer_name' in node.node_info:
                    node_data['name'] = node.node_info['computer_name']
                else:
                    current_app.logger.error('System name is empty')
                    node_data['host_identifier'] = node.host_identifier

                data['node'] = node_data
                data['data'] = results
                data['query_id'] = task.distributed_query.id

                push_live_query_results_to_websocket(data, task.distributed_query.id)
                # save_distributed_query_data.delay(node.id, results, task.distributed_query.description)

        else:
            data = {}
            node_data = {'id': node.id}
            if node.node_info and 'computer_name' in node.node_info:
                node_data['name'] = node.node_info['computer_name']
            else:
                current_app.logger.error('System name is empty')
                node_data['host_identifier'] = node.host_identifier

            data['node'] = node_data
            data['data'] = results
            data['query_id'] = task.distributed_query.id

            push_live_query_results_to_websocket(data, task.distributed_query.id)

        for columns in results:
            pass
            # result = DistributedQueryResult(
            #     columns,
            #     distributed_query=task.distributed_query,
            #     distributed_query_task=task
            # )
            # db.session.add(result)
        else:
            task.status = status
            db.session.add(task)

    else:
        # need to write last_checkin, last_ip on node
        node.update(last_query_write=dt.datetime.utcnow())

        db.session.add(node)
        db.session.commit()

    return jsonify(node_invalid=False)


def push_live_query_results_to_websocket(results, queryId):
    import pika
    from polylogyx.settings import RABBITMQ_HOST,credentials
    queryId = str(queryId)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=RABBITMQ_HOST, credentials=credentials))
    channel = connection.channel()

    try:
        channel.basic_publish(exchange=queryId,
                              routing_key=queryId,
                              body=json.dumps(results))
    except Exception as e:
        current_app.logger.error(e)
    connection.close()


def update_mac_address(node, mac_address_obj):
    db.session.query(Node).filter(Node.id == node.id).update({"network_info": mac_address_obj})
    db.session.commit()


def update_system_info(node, system_info):
    try:
        capture_columns = set(
            map(itemgetter(0),
                current_app.config['POLYLOGYX_CAPTURE_NODE_INFO']
                )
        )
        if not capture_columns:
            return
        node_info = node.node_info
        if node_info is None:
            node_info = {}
        for column in capture_columns & set(system_info):
            if column != 'cpu_brand':
                value = system_info.get(column)
                node_info[column] = value.strip()

        db.session.query(Node).filter(Node.id == node.id).update({"node_info": node_info})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)

    return node


def update_os_info(node, system_info):
    node.os_info = system_info
    db.session.query(Node).filter(Node.id == node.id).update({"os_info": system_info})
    db.session.commit()


def fetch_system_info(data):
    return data['system_info']


def fetch_platform(data):
    return data['os_version']['platform']


def get_ip():
    trusted_proxies = {'127.0.0.1'}  # define your own set
    route = request.access_route + [request.remote_addr]

    remote_addr = next((addr for addr in reversed(route)
                        if addr not in trusted_proxies), request.remote_addr)
    if remote_addr == '::1':
        remote_addr = '127.0.0.1'
    elif remote_addr[:7] == "::ffff:":
        remote_addr = remote_addr[7:]

    return remote_addr


def send_checkin_queries(node):
    from polylogyx.tasks import send_recon_on_checkin

    # send_recon_on_checkin.delay(node.to_dict())

    send_recon_on_checkin.apply_async(queue='default_queue_tasks', args=[node.to_dict()])

def update_system_details(request_json, node):
    if 'host_details' in request_json and request_json.get('host_details'):
        host_details = request_json.get('host_details')
        platform = fetch_platform(host_details)
        system_info = fetch_system_info(host_details)
        node.platform = platform
        if system_info:
            update_system_info(node, system_info)
