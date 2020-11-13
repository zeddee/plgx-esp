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
from polylogyx.models import ThreatIntelCredentials, OsquerySchema
from polylogyx.settings import CurrentConfig, RABBITMQ_HOST
import time, json

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


@manager.option('--file_path', default='polylogyx/resources/osquery_schema.json')
def update_osquery_schema(file_path):
    from polylogyx.models import OsquerySchema
    try:
        f = open(file_path, "r")
    except FileNotFoundError:
        print("File is not present for the path given!")
        exit(0)
    except Exception as e:
        print(str(e))
        exit(0)

    file_content = f.read()
    schema_json = json.loads(file_content)
    for table_dict in schema_json:
        table = OsquerySchema.query.filter(OsquerySchema.name == table_dict['name']).first()
        if table:
            table.update(schema=table_dict['schema'], description=table_dict['description'], platform=table_dict['platform'])
        else:
            if not table_dict['platform'] == ['freebsd'] and not table_dict['platform'] == ['posix']:
                OsquerySchema.create(name=table_dict['name'], schema=table_dict['schema'], description=table_dict['description'], platform=table_dict['platform'])
    app.logger.info('Osquery Schema is updated to postgres through the file input {} successfully'.format(file_path))
    exit(0)


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
        credentials={}
        credentials['key'] = VT_API_KEY
        ThreatIntelCredentials.create(intel_name='virustotal', credentials=credentials)
    OTX_API_KEY=None
    try:
        OTX_API_KEY=os.environ.get('ALIENVAULT_OTX_KEY')
    except Exception as e:
        print ("Alienvault OTX key not provided")
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
    while not ws.closed:
        message = str(ws.receive())
        if not  ws.closed:
            declare_queue(message,ws,None)
            ws.send('Fetching results for query with query id : ' + message)


@sio.on('message', namespace='/test')
def message(sid, message):
    print(' mapping query ' + str(message) + ' to session ' + str(sid))
    declare_queue(message,None,sid)


@sio.on('disconnect request', namespace='/test')
def disconnect_request(sid):
    sio.disconnect(sid, namespace='/test')


@sio.on('connect', namespace='/test')
def test_connect(sid, environ):
    print("%s connected" % (sid))


@sio.on('disconnect', namespace='/test')
def test_disconnect(sidDisconnected):
    room = sidDisconnected
    # for dqid, sid in clients.items():
    #     if sid == room:
    #         close_queue(dqid)
    with app.app_context():
        try:
            leave_room(room)
        except Exception as e:
            print (e)
        print('Client disconnected')


def push_results_to_websocket(resultstr, queryId,ws,sid):
    with app.app_context():

        try:
            results = ast.literal_eval(str(resultstr.decode("utf-8")))
            if ws:
                try:
                    ws.send(resultstr)
                except:
                    current_app.logger.info('Websocket connection closed.')
            elif sid:
                try:
                    sio.emit('message', results, room=sid,
                             namespace='/test')
                except:
                    current_app.logger.info('Websocket connection closed. Sending over ui')


                current_app.logger.info('sending message to session ' + ' for distributed query ' + str(
                    queryId))
        except:
            current_app.logger.error('Error parsing results')


def declare_queue(distributedQueryId,ws,sid):

    client = ConsumerThread( int(distributedQueryId),ws,sid)
    try:
        client.start()
    except Exception as e:
        current_app.logger.error(e)


class ConsumerThread(threading.Thread):
    def __init__(self,query_id,ws,sid, *args, **kwargs):
        super(ConsumerThread, self).__init__(*args, **kwargs)
        self._is_interrupted = False

        self._query_id = str(query_id)
        self.ws = ws
        self.sid = sid
        self.max_wait_time=60*10
        self.inactivity_timeout=30
        self.current_time_elapsed=0


        self.query_string="live_query_"+str(self._query_id)

    def stop(self):
        self._is_interrupted = True

    # Not necessarily a method.
    def callback_func(self, channel, method, properties, body):
        push_results_to_websocket(body, self._query_id,self.ws,self.sid)

        print("{} received '{}'".format(self._query_id, body))

    def run(self):
        credentials = pika.PlainCredentials("guest", "guest")

        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=RABBITMQ_HOST, credentials=credentials))
        channel = connection.channel()
        channel.exchange_declare(exchange=self.query_string)

        result = channel.queue_declare(queue=self.query_string, exclusive=True,
                                       arguments={'x-message-ttl': self.max_wait_time * 1000,
                                                  'x-expires': self.max_wait_time * 1000})
        queue_name = result.method.queue

        channel.queue_bind(exchange=self.query_string, queue=queue_name)

        try:
            for message in channel.consume(self.query_string, inactivity_timeout=self.inactivity_timeout):

                method, properties, body = message
                if not body:
                    self.current_time_elapsed += self.inactivity_timeout
                    if self.current_time_elapsed >= self.max_wait_time:
                        channel.stop_consuming()
                        connection.close()
                    continue

                self.callback_func(channel, method, properties, body)
                print(body)
        except pika.exceptions.ConnectionClosed as e:
            channel.stop_consuming()
            connection.close()

            print('Connection already closed {0}'.format(self.query_string))
        except pika.exceptions.ChannelClosed as e:
            channel.stop_consuming()
            connection.close()

            print('Channel already closed {0}'.format(self.query_string))
        print('Exiting thread for query id : {}'.format(self._query_id))


def close_queue(distributedQueryId):
    pass
    channel = distributedQueryId
    # pubsub = r.pubsub()
    # pubsub.unsubscribe(channel)
    print ('closing {channel}'.format(**locals()))


@app.after_request
def add_response_headers(response):
    response.headers.add('Access-Control-Allow-Methods', 'PUT, GET, POST, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,x-access-token,content-type')
    response.headers.add('Access-Control-Expose-Headers', 'Content-Type,Content-Length,Authorization,X-Pagination')
    return response


if __name__ == '__main__':
    manager.run()

