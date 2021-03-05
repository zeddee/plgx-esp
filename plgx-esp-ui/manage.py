# set async_mode to 'threading', 'eventlet', 'gevent' or 'gevent_uwsgi' to
# force a mode else, the best mode is selected automatically from what's
# installed
# -*- coding: utf-8 -*-
import ast
import glob
import threading
from os.path import abspath, dirname, join

import pika

from flask import current_app
from flask_migrate import MigrateCommand
from flask_script import Command, Manager, Server, Shell
from flask_script.commands import Clean, ShowUrls
from flask_socketio import leave_room
from flask_sockets import Sockets

from polylogyx import create_app, db
from polylogyx.models import ThreatIntelCredentials
from polylogyx.settings import CurrentConfig, RABBITMQ_HOST, RABBIT_CREDS, RabbitConfig
import json
import socketio

from polylogyx.utils import validate_osquery_query


app = create_app(config=CurrentConfig)


async_mode = 'gevent'
sio = socketio.Server(logger=True, async_mode=async_mode)
sockets = Sockets(app)
app.wsgi_app = socketio.Middleware(sio, app.wsgi_app)

with app.app_context():
    validate_osquery_query('select * from processes;')


def _make_context():
    return {'app': app, 'db': db}


class SSLServer(Command):

    def run_server(self):
            from gevent import pywsgi
            from werkzeug.debug import DebuggedApplication
            from geventwebsocket.handler import WebSocketHandler

            validate_osquery_query('select * from processes;')
            pywsgi.WSGIServer(('', 5000), DebuggedApplication(app),
                              handler_class=WebSocketHandler, keyfile='../nginx/private.key',
                              certfile='../nginx/certificate.crt').serve_forever()

    def run(self, *args, **kwargs):
        if __name__ == '__main__':
            from werkzeug.serving import run_with_reloader
            run_with_reloader(self.run_server())


manager = Manager(app)
manager.add_command('server', Server())

manager.add_command('shell', Shell(make_context=_make_context))
manager.add_command('db', MigrateCommand)
manager.add_command('clean', Clean())
manager.add_command('urls', ShowUrls())
manager.add_command('ssl', SSLServer())


@manager.add_command
class test(Command):
    name = 'test'
    capture_all_args = True

    def run(self, remaining):
        import pytest
        test_path = join(abspath(dirname(__file__)), 'tests')

        if remaining:
            test_args = remaining + ['--verbose']
        else:
            test_args = [test_path, '--verbose']

        exit_code = pytest.main(test_args)
        return exit_code


@manager.option('--specs_dir')
@manager.option('--export_type', default='sql', choices=['sql', 'json'])
def extract_ddl(specs_dir, export_type):
    """
    Extracts CREATE TABLE statements or JSON Array of schema from osquery's table specifications

    python manage.py extract_ddl --specs_dir /Users/polylogyx/osquery/specs --export_type sql  ----> to export to osquery_schema.sql file
    python manage.py extract_ddl --specs_dir /Users/polylogyx/osquery/specs --export_type json  ----> to export to osquery_schema.json file
    """
    from polylogyx.extract_ddl import extract_schema, extract_schema_json

    spec_files = []
    spec_files.extend(glob.glob(join(specs_dir, '*.table')))
    spec_files.extend(glob.glob(join(specs_dir, '**', '*.table')))
    if export_type == 'sql':
        ddl = sorted([extract_schema(f) for f in spec_files], key=lambda x: x.split()[2])
        opath = join(dirname(__file__), 'polylogyx', 'resources', 'osquery_schema.sql')
        content = '\n'.join(ddl)
    elif export_type == 'json':
        full_schema = []
        for f in spec_files:
            table_dict = extract_schema_json(f)
            if table_dict['platform']:
                full_schema.append(table_dict)
        opath = join(dirname(__file__), 'polylogyx', 'resources', 'osquery_schema.json')
        content = json.dumps(full_schema)
    else:
        print("Export type given is invalid!")
        opath = None
        content = None

    with open(opath, 'w') as f:
        if export_type == 'sql':
            f.write('-- This file is generated using "python manage.py extract_ddl"'
                    '- do not edit manually\n')
        f.write(content)
    app.logger.info('Osquery Schema is exported to the file {} successfully'.format(opath))


@manager.option('--IBMxForceKey')
@manager.option('--IBMxForcePass')
@manager.option('--VT_API_KEY')
def add_api_key(IBMxForceKey, IBMxForcePass, VT_API_KEY):
    import os
    ibm_x_force_credentials = ThreatIntelCredentials.query.filter(ThreatIntelCredentials.intel_name == 'ibmxforce').first()

    vt_credentials = ThreatIntelCredentials.query.filter(ThreatIntelCredentials.intel_name == 'virustotal').first()
    if vt_credentials :
        app.logger.info('Virus Total Key already exists')
    else:
        credentials = {}
        credentials['key'] = VT_API_KEY
        ThreatIntelCredentials.create(intel_name='virustotal', credentials=credentials)
    OTX_API_KEY = None
    try:
        OTX_API_KEY = os.environ.get('ALIENVAULT_OTX_KEY')
    except Exception as e:
        print("Alienvault OTX key not provided")
    if OTX_API_KEY:
        otx_credentials = ThreatIntelCredentials.query.filter(ThreatIntelCredentials.intel_name == 'alienvault').first()
        if otx_credentials :
            app.logger.info('AlienVault  Key already exists')
        else:
            credentials={}
            credentials['key'] = OTX_API_KEY
            ThreatIntelCredentials.create(intel_name='alienvault', credentials=credentials)

    if ibm_x_force_credentials:
        app.logger.info('Ibm Key already exists')
    else:
        credentials={}
        credentials['key'] = IBMxForceKey
        credentials['pass'] = IBMxForcePass
        ThreatIntelCredentials.create(intel_name='ibmxforce', credentials=credentials)

    exit(0)


@sockets.route('/distributed/result')
def echo_socket(ws):
    """Websocket URL to fetch the results of LiveQuery published from ESP container"""
    while not ws.closed:
        message = str(ws.receive())
        if not  ws.closed:
            ws.send('Fetching results for query with query id : {}'.format(message))
            client = ConsumerThread("live_query", message, ws, None)
            try:
                client.start()
            except Exception as e:
                current_app.logger.error(e)


class ConsumerThread(threading.Thread):
    """Consumes the messages from rabbitmq exchange and closes the exchange and queue
            after the time interval(max_wait_time) set
    Pushes the actual query results to the websocket
    """
    def __init__(self, type, ObjectID, ws, sid, *args, **kwargs):
        super(ConsumerThread, self).__init__(*args, **kwargs)
        self._is_interrupted = False
        self.ObjectID = ObjectID
        self.ws = ws
        self.sid = sid
        self.type = type
        self.exchange_name = "{}_{}".format(self.type, self.ObjectID)
        self.current_time_elapsed = 0

    def stop(self):
        self._is_interrupted = True

    def run(self):
        """Consumes the messages from rabbitmq exchange and closes the exchange and queue
        after the time interval(max_wait_time) set"""

        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=RABBITMQ_HOST, credentials=RABBIT_CREDS))
        channel = connection.channel()
        try:
            for message in channel.consume(self.exchange_name, inactivity_timeout=RabbitConfig.inactivity_timeout):
                method, properties, body = message
                if not body:
                    self.current_time_elapsed += RabbitConfig.inactivity_timeout
                    if self.current_time_elapsed >= RabbitConfig.max_wait_time:
                        channel.stop_consuming()
                        channel.exchange_delete(self.exchange_name)
                        channel.queue_delete(self.exchange_name)
                        connection.close()
                    continue

                self.push_results_to_websocket(body)
                print(body)

        except pika.exceptions.ConnectionClosed as e:
            channel.stop_consuming()
            connection.close()
            print('Connection already closed {0}'.format(self.exchange_name))

        except pika.exceptions.ChannelClosed as e:
            channel.stop_consuming()
            connection.close()
        connection.close()

    def push_results_to_websocket(self, resultstr):
        """Pushes the results to the websocket end, connected to fetch results of LiveQuery"""
        with app.app_context():
            try:
                results = ast.literal_eval(str(resultstr.decode("utf-8")))
                if self.ws:
                    try:
                        self.ws.send(resultstr)
                    except:
                        current_app.logger.info('Websocket connection closed.')
                elif self.sid:
                    try:
                        sio.emit('message', results, room=self.sid,
                                 namespace='/test')
                    except:
                        current_app.logger.info('Websocket connection closed. Sending over ui')
            except:
                current_app.logger.error('Error parsing results')


@sio.on('message', namespace='/test')
def message(sid, message):
    print(' mapping query ' + str(message) + ' to session ' + str(sid))
    client = ConsumerThread("live_query", message, None, sid)
    try:
        client.start()
    except Exception as e:
        current_app.logger.error(e)


@sio.on('disconnect request', namespace='/test')
def disconnect_request(sid):
    sio.disconnect(sid, namespace='/test')


@sio.on('connect', namespace='/test')
def test_connect(sid, environ):
    print("%s connected" % (sid))


@sio.on('disconnect', namespace='/test')
def test_disconnect(sidDisconnected):
    room = sidDisconnected
    with app.app_context():
        try:
            leave_room(room)
        except Exception as e:
            print (e)
        print('Client disconnected')


def declare_queue(ObjectID, type='live_query'):
    """Creates exchange, queue(non-exclusive) and binds the the exchange to the queue"""
    exchange_name = "{}_{}".format(type, ObjectID)

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=RABBIT_CREDS))
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange_name)
    result = channel.queue_declare(queue=exchange_name, exclusive=False,
                                   arguments={'x-message-ttl': RabbitConfig.max_wait_time * 1000,
                                              'x-expires': RabbitConfig.max_wait_time * 1000})
    queue_name = result.method.queue
    channel.queue_bind(exchange=exchange_name, queue=queue_name)
    print("A Queue and Echange are declared with name: {}".format(queue_name))


@app.after_request
def add_response_headers(response):
    response.headers.add('Access-Control-Allow-Methods', 'PUT, GET, POST, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,x-access-token,content-type')
    response.headers.add('Access-Control-Expose-Headers', 'Content-Type,Content-Length,Authorization,X-Pagination')
    return response


if __name__ == '__main__':
    manager.run()

