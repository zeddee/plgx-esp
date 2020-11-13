# -*- coding: utf-8 -*-
import base64
import os
import re
from contextlib import contextmanager

from celery import Celery
from flask import current_app
import json

from polylogyx.constants import  PolyLogyxServerDefaults
from polylogyx.extensions import threat_intel
from polylogyx.models import  CarveSession, CarvedBlock


re._pattern_type = re.Pattern
from polylogyx.models import DistributedQueryTask, DistributedQuery, Node, DefaultQuery
from polylogyx.constants import DefaultInfoQueries

LOCK_EXPIRE = 60 * 2

celery = Celery(__name__)
threat_frequency = 60
celery.conf.update(
    worker_pool_restarts=True,
)


try:
    threat_frequency = int(os.environ.get("THREAT_INTEL_ALERT_FREQUENCY"))
except Exception as e:
    print(e)

celery.conf.beat_schedule = {
   "scan_and_match_with_threat_intel": {
        "task": "polylogyx.tasks.scan_result_log_data_and_match_with_threat_intel",
        "schedule": 300.0,
        'options': {'queue': 'default_queue_tasks'}
    }, "send_intel_alerts": {
        "task": "polylogyx.tasks.send_threat_intel_alerts",
        "schedule": threat_frequency * 60,
        'options': {'queue': 'default_queue_tasks'}
    }
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
def analyze_result(result, node):
    # learn_from_result.s(result, node).delay()
    current_app.rule_manager.handle_log_entry(result, node)
    purge_older_data(node['id'])
    return


@celery.task()
def learn_from_result(result, node):
    from polylogyx.utils import learn_from_result
    learn_from_result(result, node)
    return


@celery.task()
def build_carve_session_archive(session_id):
    from polylogyx.models import db
    carve_session = CarveSession.query.filter(CarveSession.session_id == session_id).first_or_404()
    if carve_session.archive:
        current_app.logger.error("Archive already exists for session %s", session_id)
        return

    # build archive file from carve blocks

    out_file_name = session_id + carve_session.carve_guid
    # Check the first four bytes for the zstd header. If not no
    # compression was used, it's a generic .tar
    carve_block_data = db.session.query(CarvedBlock.data).filter(CarvedBlock.session_id == session_id).order_by(
        "block_id").all()
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
    carve_session.status = CarveSession.StatusCompleted
    carve_session.update(carve_session)
    db.session.commit()


@celery.task()
def example_task(one, two):
    print('Adding {0} and {1}'.format(one, two))
    return one + two


@celery.task()
def purge_older_data(node_id):
    import datetime as dt
    from polylogyx.models import db,Settings, ResultLog
    from sqlalchemy import asc, and_
    max_delete_count = 1024
    current_app.logger.info("Purged Started")
    try:
        delete_setting = Settings.query.filter(Settings.name == 'purge_data_duration').first()
        since = dt.datetime.now() - dt.timedelta(hours=24 * int(delete_setting.setting))
        deleted_count = ResultLog.query.filter(ResultLog.id.in_(
            db.session.query(ResultLog.id).filter(and_(ResultLog.node_id==node_id,ResultLog.timestamp < since)).order_by(asc(ResultLog.id)).limit(max_delete_count))).delete(
            synchronize_session='fetch')
        db.session.commit()
        current_app.logger.info("Purged {} rows".format(deleted_count))
    except Exception as e:
        current_app.logger.error(e)

    current_app.logger.info("Purged Finished")


@celery.task()
def send_recon_on_checkin(node):
    from polylogyx.database import db
    try:
        node_obj = Node.query.filter(Node.id == node.get('id')).first()
        send_queries(node_obj, db)
    except Exception as e:
        current_app.logger.error(e)


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

        for key, value in DefaultInfoQueries.DEFAULT_VERSION_INFO_QUERIES.items():
            platform = node.platform
            if not platform == "windows" and not platform == "darwin" and not platform == "freebsd":
                platform = "linux"
            default_query = DefaultQuery.query.filter(DefaultQuery.name == key).filter(DefaultQuery.platform == platform).first()
            query = DistributedQuery.create(sql=default_query.sql,
                                            description=value
                                            )
            task = DistributedQueryTask(node=node, distributed_query=query, save_results_in_db=True)
            db.session.add(task)

        db.session.commit()

    except Exception as e:
        current_app.logger.error(e)