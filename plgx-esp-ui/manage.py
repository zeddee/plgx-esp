# set async_mode to 'threading', 'eventlet', 'gevent' or 'gevent_uwsgi' to
# force a mode else, the best mode is selected automatically from what's
# installed
# -*- coding: utf-8 -*-
import ast
import glob
import threading
from os.path import abspath, dirname, join

import pika
import werkzeug.serving

import sqlalchemy
from flask import current_app, json
from flask_assets import ManageAssets
from flask_migrate import MigrateCommand
from flask_script import Command, Manager, Server, Shell
from flask_script.commands import Clean, ShowUrls
from flask_socketio import leave_room
from flask_sockets import Sockets

from polylogyx import create_app, db
from polylogyx.assets import assets
from polylogyx.models import Settings, ThreatIntelCredentials
from polylogyx.settings import CurrentConfig, RABBITMQ_HOST
from polylogyx.constants import websockets, clients


import time
import socketio

from polylogyx.utils import validate_osquery_query
# import gevent.monkey
# gevent.monkey.patch_all()
# from urllib3.util.ssl_ import create_urllib3_context
# create_urllib3_context()
constant_file_event = 'win_file_events'
constant_process_event = 'win_process_events'


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
manager.add_command("assets", ManageAssets(assets))
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


@manager.command
def extract_ddl(specs_dir):
    """Extracts CREATE TABLE statements from osquery's table specifications"""
    from polylogyx.extract_ddl import extract_schema

    spec_files = []
    spec_files.extend(glob.glob(join(specs_dir, '*.table')))
    spec_files.extend(glob.glob(join(specs_dir, '**', '*.table')))

    ddl = sorted([extract_schema(f) for f in spec_files], key=lambda x: x.split()[2])

    opath = join(dirname(__file__), 'polylogyx', 'resources', 'osquery_schema.sql')
    with open(opath, 'w') as f:
        f.write('-- This file is generated using "python manage.py extract_ddl"'
                '- do not edit manually\n')
        f.write('\n'.join(ddl))


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
        if ws.closed:
            try:
                close_queue(websockets[ws])
            except:
                print('redis channel is not opened yet')
        else:
            websockets[ws] = message
            declare_queue(message)
            ws.send('Fetching results for query with query id : ' + message)


@sio.on('message', namespace='/test')
def message(sid, message):
    print(' mapping query ' + str(message) + ' to session ' + str(sid))
    clients[int(message)] = sid
    declare_queue(message)


@sio.on('disconnect request', namespace='/test')
def disconnect_request(sid):
    sio.disconnect(sid, namespace='/test')


@sio.on('connect', namespace='/test')
def test_connect(sid, environ):
    print("%s connected" % (sid))


@sio.on('disconnect', namespace='/test')
def test_disconnect(sidDisconnected):
    room = sidDisconnected
    for dqid, sid in clients.items():
        if sid == room:
            close_queue(dqid)
    with app.app_context():
        try:
            leave_room(room)
        except Exception as e:
            print (e)
        print('Client disconnected')


def get_key_by_value(list, queryIdStr):
    for ws, queryId in list.items():
        if str(queryIdStr) == queryId:
            return ws
    return None


def push_results_to_websocket(resultstr, queryId):
    from polylogyx.constants import clients

    with app.app_context():

        try:
            results = ast.literal_eval(str(resultstr.decode("utf-8")))
            try:
                try:
                    ws = get_key_by_value(websockets, str(queryId))
                    ws.send(resultstr)
                except:
                    current_app.logger.info('Websocket connection closed. Sending over ui')

                sio.emit('message', results, room=clients[int(queryId)],
                         namespace='/test')
                current_app.logger.info('sending message to session ' + ' for distributed query ' + str(
                    queryId))
            except:
                current_app.logger.warn("Socket closed for query id : " + str(queryId))

        except:
            current_app.logger.error('Error parsing results')


def declare_queue(distributedQueryId):
    client = ConsumerThread( int(distributedQueryId))
    client.start()


class ConsumerThread(threading.Thread):
    def __init__(self,query_id, *args, **kwargs):
        super(ConsumerThread, self).__init__(*args, **kwargs)

        self._query_id = str(query_id)

    # Not necessarily a method.
    def callback_func(self, channel, method, properties, body):
        push_results_to_websocket(body, self._query_id)

        print("{} received '{}'".format(self._query_id, body))

    def run(self):
        credentials = pika.PlainCredentials("guest", "guest")

        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=RABBITMQ_HOST, credentials=credentials))
        channel = connection.channel()
        channel.exchange_declare(exchange=self._query_id)

        result = channel.queue_declare(queue=self._query_id, exclusive=True, arguments={'x-message-ttl': 1000000,'x-expires':300000})
        queue_name = result.method.queue

        channel.queue_bind(exchange=self._query_id, queue=queue_name)


        channel.basic_consume(self.callback_func,
                              result.method.queue,
                              no_ack=True)

        channel.start_consuming()


def close_queue(distributedQueryId):
    pass
    channel = distributedQueryId
    # pubsub = r.pubsub()
    # pubsub.unsubscribe(channel)
    print ('closing {channel}'.format(**locals()))



if __name__ == '__main__':
    manager.run()

# class Listener(threading.Thread):
#     def __init__(self, r, channel):
#         threading.Thread.__init__(self, name=channel)
#         self.redis = r
#         self.channel = channel
#         self.pubsub = self.redis.pubsub(ignore_subscribe_messages=True)
#         self.pubsub.subscribe(channel)
#
#     def send_over_socket(self, results):
#         push_results_to_websocket(results, self.channel)
#         print (self.channel, ":", 'Received data')
#
#     def run(self):
#         current_pull=0
#         self.pop_and_push(time.time() + 60 * 10,current_pull)
#
#     def pop_and_push(self, timeout,current_pull):
#         if time.time() > timeout:
#             return ''
#         message = r.lpop(self.channel)
#         current_pull=current_pull+1
#         if message and current_pull<=50:
#             self.send_over_socket(message)
#             self.pop_and_push(timeout,current_pull)
#         else:
#             time.sleep(5)
#             current_pull=0
#             self.pop_and_push(timeout,current_pull)


