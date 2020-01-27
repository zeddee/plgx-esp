# -*- coding: utf-8 -*-
import base64
import datetime as dt
import os
import re
import uuid
from contextlib import contextmanager
from io import BytesIO

import requests
from celery import Celery
from flask import current_app
import json
from sqlalchemy import desc

from polylogyx.constants import TO_CAPTURE_COLUMNS, PolyLogyxServerDefaults
from polylogyx.extensions import threat_intel
from polylogyx.models import ResultLog, ResultLogScan, CarveSession, CarvedBlock
from polylogyx.utils import extract_result_logs, process_result

re._pattern_type = re.Pattern
from polylogyx.models import DistributedQueryTask, DistributedQuery, Node
from polylogyx.constants import DefaultInfoQueries

LOCK_EXPIRE = 60 * 2
# Field = namedtuple('Field', ['name', 'action', 'columns', 'timestamp', 'uuid', 'node_id'])

celery = Celery(__name__)
threat_frequency = 60
celery.conf.update(
    worker_pool_restarts=True,
)

# celery.conf.task_default_queue = 'default_queue_tasks'
celery.conf.update({
'task_routes': {
'save_schedule_query_data': {'queue': 'result_log_queue'}
}})

try:
    threat_frequency = int(os.environ.get("THREAT_INTEL_ALERT_FREQUENCY"))
except Exception as e:
    print(e)

celery.conf.beat_schedule = {
    "fetch-command-status": {
        "task": "polylogyx.tasks.fetch_command_status",
        "schedule":10,
        'options': {'queue': 'default_queue_tasks'}
    },"scan_and_match_with_threat_intel": {
        "task": "polylogyx.tasks.scan_result_log_data_and_match_with_threat_intel",
        "schedule": 60.0,
        'options': {'queue': 'default_queue_tasks'}
    }, "send_intel_alerts": {
        "task": "polylogyx.tasks.send_threat_intel_alerts",
        "schedule": threat_frequency * 60,
        'options': {'queue': 'default_queue_tasks'}
    }
    
    # , "update_phishtank_data": {
    #     "task": "polylogyx.tasks.update_phishtank_data",
    #     "schedule": threat_frequency * 60,
    #     'options': {'queue': 'default_queue_tasks'}
    # },

}

@contextmanager
def memcache_lock(lock_id, oid):
    import time
    from flask_caching import Cache

    cache = Cache(app=current_app, config={'CACHE_TYPE': 'simple'})

    monotonic_time = time.monotonic()
    timeout_at = monotonic_time + LOCK_EXPIRE - 3
    print('in memcache_lock and timeout_at is {}'.format(timeout_at))
    # cache.add fails if the key already exists
    status = cache.add(lock_id, oid, LOCK_EXPIRE)
    try:
        yield status
        print('memcache_lock and status is {}'.format(status))
    finally:
        # memcache delete is very slow, but we have to use it to take
        # advantage of using add() for atomic locking
        if monotonic_time < timeout_at and status:
            # don't release the lock if we exceeded the timeout
            # to lessen the chance of releasing an expired lock
            # owned by someone else
            # also don't release the lock if we didn't acquire it
            cache.delete(lock_id)


@celery.task()
def save_schedule_query_data(data, node):
    from polylogyx.database import db
    from flask import current_app
    try:
        db.session.bulk_save_objects(process_result(data, node))
        db.session.commit()
        # match_with_rules.delay(data,node)
        # match_data_with_uploaded_iocs.delay(data,node)

    except Exception as e:
        current_app.logger.error(e)


@celery.task()
def analyze_result(result, node):
    learn_from_result.s(result, node).delay()
    current_app.rule_manager.handle_log_entry(result, node)
    return


@celery.task()
def learn_from_result(result, node):
    from polylogyx.utils import learn_from_result
    learn_from_result(result, node)
    return


@celery.task()
def pull_and_match_with_rules():
    while True:
        analyse_result_log_data_with_rule_ioc_intel()

@celery.task()
def analyse_result_log_data_with_rule_ioc_intel():
    import time
    task_id = str(uuid.uuid4())
    from polylogyx.database import db
    sq = db.session.query(ResultLog.id).filter(ResultLog.status == ResultLog.NEW) \
        .order_by(ResultLog.id.asc()) \
        .limit(1000) \
        .with_for_update()
    count = db.session.query(ResultLog).filter(
        ResultLog.id.in_(sq.as_scalar())).update(
        {"status": ResultLog.PENDING, "task_id": task_id}, synchronize_session='fetch')

    if count > 0:
        print("Executing tasks for task_id : " + task_id)
        tasks = db.session.query(ResultLog).filter(ResultLog.task_id == task_id).all()
        check_for_iocs(tasks)
        match_with_rules(tasks)
        db.session.query(ResultLog).filter(
            ResultLog.task_id == task_id).update(
            {"status": ResultLog.COMPLETE}, synchronize_session='fetch')
        db.session.commit()
        time.sleep(5)
    else:
        print("No pending tasks!")
        db.session.commit()
        time.sleep(15)
    return

@celery.task()
def build_carve_session_archive(session_id):
    from polylogyx.models import db
    carve_session = CarveSession.query.filter(CarveSession.session_id ==session_id).first_or_404()
    if carve_session.archive:
        current_app.logger.error("Archive already exists for session %s", session_id)
        return

    # build archive file from carve blocks

    out_file_name = session_id + carve_session.carve_guid
    # Check the first four bytes for the zstd header. If not no
    # compression was used, it's a generic .tar
    carve_block_data=db.session.query(CarvedBlock.data).filter(CarvedBlock.session_id == session_id).order_by("block_id").all()
    if (base64.standard_b64decode(carve_block_data[0][0])[
                            0:4] == b'\x28\xB5\x2F\xFD'):
        out_file_name += '.zst'
    else:
        out_file_name += '.tar'
    carve_session.archive = out_file_name

    out_file_name = PolyLogyxServerDefaults.BASE_URL + '/carves/' + carve_session.node.host_identifier + '/' + out_file_name
    if not os.path.exists(PolyLogyxServerDefaults.BASE_URL + '/carves/' + carve_session.node.host_identifier + '/'):
        os.makedirs(PolyLogyxServerDefaults.BASE_URL + '/carves/' + carve_session.node.host_identifier + '/')
    f = open(out_file_name, 'wb')

    for data in carve_block_data:
        f.write(base64.standard_b64decode(data[0]))
    # break;
    f.close()
    carve_session.status=CarveSession.StatusCompleted
    carve_session.update(carve_session)
    db.session.commit()




@celery.task()
def example_task(one, two):
    print('Adding {0} and {1}'.format(one, two))
    return one + two


@celery.task()
def handle_result(data, host_identifier, node):
    from polylogyx.extensions import log_tee
    try:
        log_tee.handle_result(data, host_identifier=host_identifier, node=node)
    except Exception as e:
        current_app.logger.error(e)


@celery.task()
def notify_of_node_enrollment(node):
    '''
    Create a result that gets run through our Rule Manager whenever a new
    node is enrolled so that we may alert on this action.

    A rule can be created within PolyLogyx's rule manager to alert on
    any of the following conditions:
        - query name: polylogyx/tasks/node_enrolled
        - action: triggered
        - columns:
            - enrolled_on
            - last_ip
            - node_id
    '''
    entry = {
        'name': 'polylogyx/tasks/node_enrolled',
        'calendarTime': dt.datetime.utcnow().strftime('%a %b %d %H:%M:%S %Y UTC'),
        'action': 'triggered',
    }
    columns = entry['columns'] = {}
    columns['enrolled_on'] = node.get('enrolled_on')
    columns['last_ip'] = node.get('last_ip')
    columns['node_id'] = node.get('id')
    result = {'data': [entry]}
    current_app.rule_manager.handle_log_entry(result, node)
    return


@celery.task()
def alert_when_node_goes_offline():
    '''
    This task is intended to periodically comb the database to identify
    nodes that have not posted results in some time, checked in for some
    time, or have not posted results within some time of their last
    checkin. The purpose of this task is to identify nodes that go offline,
    or in some cases, nodes with corrupted osquery rocksdb databases.

    A rule can be created within PolyLogyx's rules manager to alert on
    any of the following conditions:
        - query name: polylogyx/tasks/node_offline_checks
        - action: triggered
        - columns:
            - since_last_result
            - since_last_result_days
            - since_last_result_seconds
            - since_last_checkin
            - since_last_checkin_days
            - since_last_checkin_seconds
            - since_last_checkin_to_last_result
            - since_last_checkin_to_last_result_days
            - since_last_checkin_to_last_result_seconds
    '''
    from collections import namedtuple
    from sqlalchemy import func
    from polylogyx.database import db
    from polylogyx.models import    Node, ResultLog

    _Node = namedtuple('Node', [
        'id', 'host_identifier', 'node_info', 'enrolled_on', 'is_active',
        'last_ip', 'last_checkin', 'last_result',
    ])
    query = db.session.query(
        ResultLog.node_id,
        Node.host_identifier,
        Node.node_info,
        Node.enrolled_on,
        Node.is_active,
        Node.last_ip,
        Node.last_checkin,
        func.max(ResultLog.timestamp),
    ).join(Node).filter(Node.is_active).group_by(ResultLog.node_id, Node.id)

    now = dt.datetime.utcnow()
    calendarTime = now.strftime('%a %b %d %H:%M:%S %Y UTC')

    for processed, node in enumerate(map(_Node._make, query), 1):
        entry = {
            'name': 'polylogyx/tasks/node_offline_checks',
            'calendarTime': calendarTime,
            'action': 'triggered',
        }
        columns = entry['columns'] = {}

        since_last_result = now - node.last_result
        since_last_checkin = now - node.last_checkin
        since_last_checkin_to_last_result = node.last_checkin - node.last_result

        columns['since_last_result_seconds'] = since_last_result.total_seconds()
        columns['since_last_checkin_seconds'] = since_last_checkin.total_seconds()
        columns['since_last_checkin_to_last_result_seconds'] = since_last_checkin_to_last_result.total_seconds()

        columns['since_last_result_days'] = since_last_result.days
        columns['since_last_checkin_days'] = since_last_checkin.days
        columns['since_last_checkin_to_last_result_days'] = since_last_checkin_to_last_result.days

        columns['since_last_result'] = since_last_result
        columns['since_last_checkin'] = since_last_checkin
        columns['since_last_checkin_to_last_result'] = since_last_checkin_to_last_result

        _node = dict(node._asdict())
        _node['display_name'] = node.node_info.get('display_name') or \
                                node.node_info.get('hostname') or \
                                node.node_info.get('computer_name') or \
                                node.host_identifier

        result = {'data': [entry]}
        current_app.rule_manager.handle_log_entry(result, _node)

    else:
        return processed


@celery.task()
def update_phishtank_data():
    import gzip
    from polylogyx.database import db
    from polylogyx.models import  PhishTank
    import pandas

    from polylogyx.constants import PolyLogyxServerDefaults
    base_path = PolyLogyxServerDefaults.BASE_URL + "/"
    baseURL = "http://data.phishtank.com/data/online-valid.json.gz"
    filename = base_path + "online-valid.json.gz"
    outFilePath = base_path + "online-valid.json"

    try:

        # response = urlopen(baseURL + filename)

        r = requests.get(baseURL + filename, allow_redirects=True, verify=False, stream=True)
        compressedFile = BytesIO()
        compressedFile.write(r.raw.read())
        #
        # Set the file's current position to the beginning
        # of the file so that gzip.GzipFile can read
        # its contents from the top.
        #
        compressedFile.seek(0)

        decompressedFile = gzip.GzipFile(fileobj=compressedFile, mode='rb')

        with open(outFilePath, 'wb') as outfile:
            outfile.write(decompressedFile.read())

        df = pandas.read_json(base_path + "online-valid.json")

        phishtank_ids = {}

        for index, row in df.iterrows():
            phish_tank_elem = PhishTank(id=row['phish_id'], phish_id=str(row['phish_id']), online=row['online'],
                                        verified=row['verified'],
                                        target=row['target'], url=row['url'], updated_at=dt.datetime.utcnow())

            phishtank_ids[row['phish_id']] = phish_tank_elem
            if index % 1000 == 0:
                for each in PhishTank.query.filter(PhishTank.id.in_(phishtank_ids.keys())).all():
                    phishtank_ids.pop(each.id)
                db.session.add_all(phishtank_ids.values())
                db.session.commit()
                phishtank_ids.clear()

        db.session.add_all(phishtank_ids.values())
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)


@celery.task()
def send_recon_on_checkin(node):
    from polylogyx.database import db
    try:
        node_obj = Node.query.filter(Node.id == node.get('id')).first()
        send_queries(node_obj, db)
    except Exception as e:
        current_app.logger.error(e)


@celery.task()
def save_distributed_query_data(node_id, results, description):
    from polylogyx.database import db
    from polylogyx.models import  NodeData, NodeReconData
    existingData = NodeData.query.filter(NodeData.node_id == node_id).filter(NodeData.name == description).first()

    if existingData:
        existingData.update(data=results, updated_at=dt.datetime.utcnow())
    else:
        existingData = NodeData.create(node_id=node_id, data=results, name=description,
                                       updated_at=dt.datetime.utcnow())
    node_recon_data = []
    for item in results:
        node_recon_data.append(
            NodeReconData(node_data_id=existingData.id, columns=item, updated_at=dt.datetime.utcnow()))
        try:
            db.session.query(NodeReconData).filter(NodeReconData.node_data_id == existingData.id).delete()
            db.session.commit()
        except Exception as e:
            current_app.logger.warn(e)
    db.session.bulk_save_objects(node_recon_data)
    db.session.commit()


@celery.task()
def scan_result_log_data_and_match_with_threat_intel():
    try:
        lock_id = 'scanResultLogDataAndMatchWithThreatIntel'

        with memcache_lock(lock_id, 'polylogyx') as acquired:
            if acquired:
                threat_intel.update_credentials()
                threat_intel.analyse_pending_hashes()
    except Exception as e:
        current_app.logger.error(e)


@celery.task()
def send_threat_intel_alerts():
    threat_intel.generate_alerts()





def clear_new_queries(node, db):
    try:
        db.session.query(DistributedQueryTask).filter(DistributedQueryTask.node_id == node.id).filter(
            DistributedQueryTask.save_results_in_db == True).filter(
            DistributedQueryTask.status == DistributedQueryTask.NEW).update({"status": DistributedQueryTask.NOT_SENT})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)


def send_queries(node, db):
    clear_new_queries(node, db)
    try:
        for key, value in DefaultInfoQueries.DEFAULT_QUERIES.items():
            query = DistributedQuery.create(sql=value,
                                            description=key,
                                            )
            task = DistributedQueryTask(node=node, distributed_query=query, save_results_in_db=True)
            db.session.add(task)
        db.session.commit()

    except Exception as e:
        current_app.logger.error(e)


def check_for_iocs(result):
    for name, action, columns, timestamp, uuid, node_id in extract_result_logs(result):
        try:
            for capture_column in TO_CAPTURE_COLUMNS:
                if capture_column in columns and columns[capture_column]:
                    result_log_scan = ResultLogScan.query.filter(
                        ResultLogScan.scan_value == columns[capture_column]).first()
                    if not result_log_scan:
                        ResultLogScan.create(scan_value=columns[capture_column], scan_type=capture_column,
                                             reputations={})
                    break
        except Exception as e:
            current_app.logger.error(e)


def match_with_rules(data):
    try:
        current_app.rule_manager.handle_result_log_entry(data)
    except Exception as e:
        current_app.logger.error(e)
    return



