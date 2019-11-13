# -*- coding: utf-8 -*-
import base64

import datetime as dt
import sqlalchemy
from celery import Celery
from flask import current_app, json
from kombu import Exchange,Queue

from polylogyx.models import Settings, AlertEmail, \
    Node, EmailRecipient, ResultLog

celery = Celery(__name__)
default_exchange = Exchange('default', type='direct')

celery.conf.task_queues = (
    Queue('worker3', default_exchange, routing_key='default'),

)
celery.conf.task_default_queue = 'worker3'
celery.conf.task_default_exchange = 'default'
celery.conf.task_default_routing_key = 'default'
celery.conf.beat_schedule = {
    "send-alert-emails": {
        "task": "polylogyx.tasks.send_alert_emails",
        "schedule": 86400.0
    }, "purge_old_data": {
        "task": "polylogyx.tasks.purge_old_data",
        "schedule": 86400.0
    },"cache_dashboard_data": {
        "task": "polylogyx.tasks.cache_top_query_count",
        "schedule": 300.0
    }
}


def update_sender_email(db):
    emailSenderObj = db.session.query(Settings).filter(Settings.name == 'email').first()
    if not emailSenderObj:
        current_app.logger.info( "Email credentials are not set..")
        return False

    try:

        emailSender = emailSenderObj.setting
        emailPassword = base64.b64decode(
            db.session.query(Settings).filter(Settings.name == 'password').first().setting)
        smtpPort = db.session.query(Settings).filter(Settings.name == 'smtpPort').first().setting
        smtpAddress = db.session.query(Settings).filter(Settings.name == 'smtpAddress').first().setting
        emailRecipients = db.session.query(EmailRecipient).filter(EmailRecipient.status == 'active').all()
        emailRecipientList = []
        if emailRecipients and len(emailRecipients) > 0:
            for emailRecipient in emailRecipients:
                emailRecipientList.append(emailRecipient.recipient)
                current_app.config['EMAIL_RECIPIENTS'] = emailRecipientList

        current_app.config['MAIL_USERNAME'] = emailSender
        current_app.config['MAIL_PASSWORD'] = emailPassword
        current_app.config['MAIL_SERVER'] = smtpAddress
        current_app.config['MAIL_PORT'] = int(smtpPort)
        return True
    except Exception as e:
        current_app.logger.info( "Incomplete email credentials")
        current_app.logger.error(e)
        return False


@celery.task()
def cache_dashboard_data():
    from polylogyx.models import DashboardData, db
    from polylogyx.constants import QueryConstants, EventQueries, UtilQueries, KernelQueries, PlugInQueries

    dahboard_data = {}
    try:
        dahboard_data['product_state'] = format_records(db.engine.execute(sqlalchemy.text(QueryConstants.PRODUCT_STATE_QUERY)))

        dahboard_data['product_signatures'] = format_records(db.engine.execute(sqlalchemy.text(QueryConstants.PRODUCT_SIGNATURES_QUERY)))

        dahboard_data['kernel_version'] = format_records(db.engine.execute(sqlalchemy.text(KernelQueries.KERNEL_VERSION_QUERY)))

        dahboard_data['chrome_ie_extensions'] = format_records(
            db.engine.execute(sqlalchemy.text(KernelQueries.CHROME_IE_EXTENSIONS_QUERY)))

        dahboard_data['file_events'] = format_records(db.engine.execute(sqlalchemy.text(EventQueries.TOTAL_FILE_EVENTS)))

        dahboard_data['unsigned_binary'] = format_records(db.engine.execute(sqlalchemy.text(UtilQueries.UNSIGNED_BINARY)))
        dahboard_data['virus_total'] = format_records(db.engine.execute(sqlalchemy.text(PlugInQueries.VIRUS_TOTAL_QUERY)))
        dahboard_data['ibm_threat_intel'] = format_records(db.engine.execute(sqlalchemy.text(PlugInQueries.IBM_THREAT_INTEL_QUERY)))

        dahboard_data['top_5_programs'] = format_records(db.engine.execute(sqlalchemy.text(UtilQueries.TOP_FIVE_PROGRAM)))
        dahboard_data['bottom_5_programs'] = format_records(db.engine.execute(sqlalchemy.text(UtilQueries.BOTTOM_FIVE_PROGRAM)))

        dahboard_data['etc_hosts'] = format_records(db.engine.execute(sqlalchemy.text(UtilQueries.ETC_HOSTS_QUERY)))

        dashboard_windows = db.session.query(DashboardData).filter(DashboardData.name == 'dashboard_windows').first()

        dahboard_Linux_data = {}
        dahboard_Linux_data['kernel_version'] = format_records(
            db.engine.execute(sqlalchemy.text(KernelQueries.KERNEL_VERSION_LINUX_QUERY)))

        dahboard_Linux_data['chrome_ie_extensions'] = format_records(
            db.engine.execute(sqlalchemy.text(KernelQueries.CHROME_FIREFOX_EXTENSIONS_QUERY)))

        dahboard_Linux_data['etc_hosts'] = format_records(db.engine.execute(sqlalchemy.text(UtilQueries.ETC_HOSTS_LINUX_QUERY)))
        dahboard_Linux_data['packages'] = format_records(db.engine.execute(sqlalchemy.text(KernelQueries.RMP_DEB_PACKAGES)))

        dahboard_Linux_data['file_events'] = format_records(db.engine.execute(sqlalchemy.text(EventQueries.TOTAL_FILE_EVENTS_LINUX)))

        dahboard_Linux_data['top_5_programs'] = format_records(db.engine.execute(sqlalchemy.text(UtilQueries.TOP_FIVE_PROGRAM_LINUX)))
        dahboard_Linux_data['top_5_ports'] = format_records(db.engine.execute(sqlalchemy.text(UtilQueries.TOP_FIVE_PORTS_LINUX)))
        dahboard_Linux_data['top_5_ips'] = format_records(db.engine.execute(sqlalchemy.text(UtilQueries.TOP_FIVE_IPS_LINUX)))
        dahboard_Linux_data['bottom_5_programs'] = format_records(
            db.engine.execute(sqlalchemy.text(UtilQueries.BOTTOM_FIVE_PROGRAM_LINUX)))

        dahboard_Linux_data['socket_events'] = format_records(db.engine.execute(sqlalchemy.text(EventQueries.TOTAL_SOCKET_EVENTS_LINUX)))

        if not dashboard_windows:
            DashboardData.create(name='dashboard_windows', data=json.dumps(dahboard_data, cls=DecimalEncoder))
        else:
            dashboard_windows.update(data=json.dumps(dahboard_data, cls=DecimalEncoder), updated_at=dt.datetime.utcnow())
            db.session.commit()
        dashboard_linux = db.session.query(DashboardData).filter(DashboardData.name == 'dashboard_linux').first()
        if not dashboard_linux:
            DashboardData.create(name='dashboard_linux', data=json.dumps(dahboard_data, cls=DecimalEncoder))
        else:
            dashboard_linux.update(data=json.dumps(dahboard_Linux_data, cls=DecimalEncoder),
                                   updated_at=dt.datetime.utcnow())
            db.session.commit()
    except Exception as e:
        current_app.logger.error(e.message)


@celery.task()
def cache_top_query_count():
    from polylogyx.models import DashboardData, db
    from sqlalchemy import text
    results = db.session.query(ResultLog.name, db.func.count(ResultLog.id).label('total')).group_by(
        ResultLog.name).order_by(text('total DESC')).limit(5).all()
    dashboard_data = {}
    query_data={}
    for result in results:
        query_data[result[0]]=result[1]
    dashboard_data['top_queries'] = query_data
    dashboard_data_obj = db.session.query(DashboardData).filter(DashboardData.name == 'dashboard').first()
    if not dashboard_data_obj:
        DashboardData.create(name='dashboard', data=json.dumps(dashboard_data, cls=DecimalEncoder))
    else:
        dashboard_data_obj.update(data=json.dumps(dashboard_data, cls=DecimalEncoder),
                               updated_at=dt.datetime.utcnow())

        db.session.commit()
@celery.task()
def send_alert_emails():
    from polylogyx.models import db

    email_credentials_valid = update_sender_email(db)
    if email_credentials_valid:
        nodes = Node.query.all()
        for node in nodes:
            try:
                send_pending_node_emails(node, db)
            except Exception  as e:
                current_app.logger.error(e.message)


@celery.task()
def purge_old_data():
    from polylogyx import db
    try:
        delete_setting = db.session.query(Settings).filter(Settings.name == 'purge_data_duration').first()

        if delete_setting and int(delete_setting.setting) > 0:
            since = dt.datetime.now() - dt.timedelta(hours=24 * int(delete_setting.setting))
            ResultLog.query.filter(ResultLog.timestamp < since).delete()
            db.session.commit()
            current_app.logger.info("Deleting data old more than : " + delete_setting.setting)
        else:
            current_app.logger.info("Deleting limit not set, skipping ")
    except Exception as e:
        current_app.logger.error(e)


def format_records(results):
    result_list = []
    keys = results.keys()

    data_list = results.fetchall()
    for data in data_list:
        result = {}
        for index, key in enumerate(keys):
            result[key] = data[index]
        result_list.append(result)
    return result_list


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        import decimal
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


def send_pending_node_emails(node, db):
    alert_emails = AlertEmail.query.filter(AlertEmail.node == node).filter(AlertEmail.status == None).all()
    body = ''
    for alert_email in alert_emails:
        body = body + alert_email.body
    if body:

        try:
            db.session.query(AlertEmail).filter(AlertEmail.status == None).filter(AlertEmail.node == node).update(
                {'status': 'PENDING'})
            db.session.commit()
            send_email(node, body,db)
        except Exception  as e:
            current_app.logger.error(e.message)

        db.session.query(AlertEmail).filter(AlertEmail.status == None).filter(AlertEmail.node == node).update(
            {'status': 'PENDING'})
        db.session.commit()
        send_email(node, body, db)



def send_email(node, body, db):
    from polylogyx.utils import send_email
    send_email(body=body, subject=node.display_name + ' Alerts Today',
              config=current_app.config, node=node,db=db)
    try:
        db.session.query(AlertEmail).filter(AlertEmail.status == 'PENDING').filter(AlertEmail.node == node).update(
            {'status': 'COMPLETED'})
        db.session.commit()
    except Exception  as e:
        current_app.logger.error(e.message)
