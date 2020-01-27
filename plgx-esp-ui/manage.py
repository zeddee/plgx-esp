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
from flask_assets import ManageAssets
from flask_migrate import MigrateCommand
from flask_script import Command, Manager, Server, Shell
from flask_script.commands import Clean, ShowUrls
from flask_socketio import leave_room
from flask_sockets import Sockets

from polylogyx import create_app, db
from polylogyx.assets import assets
from polylogyx.models import  ThreatIntelCredentials
from polylogyx.settings import CurrentConfig, RABBITMQ_HOST
import time

import socketio

from polylogyx.utils import validate_osquery_query

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



if __name__ == '__main__':
    manager.run()

