# set async_mode to 'threading', 'eventlet', 'gevent' or 'gevent_uwsgi' to
# force a mode else, the best mode is selected automatically from what's
# installed
# -*- coding: utf-8 -*-
import datetime as dt
import glob
from os.path import abspath, dirname, join

from flask import json, current_app
from flask_migrate import MigrateCommand
from flask_script import Command, Manager, Server, Shell
from flask_script.commands import Clean, ShowUrls

from polylogyx import create_app, db
from polylogyx.extensions import bcrypt
from polylogyx.models import Query, Rule, Options, Settings, DefaultFilters, DefaultQuery, Config
from polylogyx.settings import CurrentConfig
from polylogyx.constants import PolyLogyxServerDefaults, UtilQueries, PolyLogyxConstants
from werkzeug.contrib.fixers import ProxyFix
import sys


app = create_app(config=CurrentConfig)
app.wsgi_app = ProxyFix(app.wsgi_app)



def _make_context():
    return {'app': app, 'db': db}

class SSLServer(Command):
    def run(self, *args, **kwargs):
        ssl_context = ('../nginx/certificate.crt', '../nginx/private.key')
        app.run(debug=True, use_debugger=True, use_reloader=False, passthrough_errors=True,host='0.0.0.0',port=9000,ssl_context=ssl_context, *args, **kwargs)
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




@manager.option('--filepath')
@manager.option('--platform')
@manager.option('--arch', default=DefaultFilters.ARCH_x64)
@manager.option('--type', default=Config.TYPE_DEFAULT)
def add_default_filters( filepath, platform, arch,type):
    is_active = False
    type=int(type)
    if type == 0 or type == 1:
        is_active = True
    config = db.session.query(Config).filter(Config.type == type).filter(Config.arch == arch).filter(
        Config.platform == platform).first()
    if not config:
        config = Config.create(platform=platform, arch=arch, type=type,is_active=is_active)
        config.save()
    existing_filter=DefaultFilters.query.filter_by(platform=platform, arch=arch,config_id=config.id).first()

    try:
        jsonStr = open(filepath, 'r').read()
        filter=json.loads(jsonStr)
        if existing_filter:
            existing_filter.filters = filter
            existing_filter.update(existing_filter)
            print("Filter already exists updating...")
        else:
            print("Filter does not exist, adding new...")
            DefaultFilters.create( filters=filter, platform=platform,created_at=dt.datetime.utcnow(), arch=arch,config_id=config.id)
    except Exception as error:
        print(str(error))

@manager.command
def delete_existing_unmapped_queries_filters():
    db.session.query(DefaultQuery).filter(DefaultQuery.config_id==None).delete()
    db.session.query(DefaultFilters).filter(DefaultFilters.config_id==None).delete()
    db.session.commit()


@manager.option('--filepath')
@manager.option('--platform')
@manager.option('--arch',   default=DefaultQuery.ARCH_x64)
@manager.option('--type',   default=Config.TYPE_DEFAULT)
def add_default_queries( filepath, platform,arch,type):
    try:
        sys.stderr.write('Adding queries for '+platform)
        jsonStr = open(filepath, 'r').read()
        query = json.loads(jsonStr)
        queries = query['schedule']
        is_active = False
        if int(type) == 0 or int(type) == 1:
            is_active = True
        config=db.session.query(Config).filter(Config.type==type).filter(Config.arch==arch).filter(Config.platform==platform).first()
        if not config:
            config=Config.create(platform=platform,arch=arch,type=type,is_active=is_active)
        for query_key in queries.keys():
            query_filter=DefaultQuery.query.filter_by(platform=platform).filter_by(name=query_key).filter_by(config_id=config.id)
            if arch==DefaultQuery.ARCH_x86:
                query_filter=query_filter.filter_by(arch=DefaultQuery.ARCH_x86)
            query=query_filter.first()
            try:
                if query:
                    sys.stderr.write("Query name " + query_key + " already exists, updating..!")
                    query.sql = queries[query_key]['query']
                    query.interval = queries[query_key]['interval']
                    query.status=queries[query_key]['status']
                    query.update(query)
                else:
                    sys.stderr.write(query_key+" does not exist, adding new...")
                    status=True
                    if "status" in queries[query_key]:
                        status=queries[query_key]['status']

                    DefaultQuery.create(name=query_key, sql=queries[query_key]['query'],arch=arch,config_id=config.id,
                                            interval=queries[query_key]['interval'], status=status, platform=platform,
                                            description=queries[query_key].get('description'))
            except Exception as error:
                sys.stderr.write(str(error))
    except Exception as error:
        raise(str(error))


@manager.option('packname')
@manager.option('--filepath')
def addpack(packname, filepath):
    from polylogyx.models import Pack

    if Pack.query.filter_by(name=packname).first():
        raise ValueError("Pack already exists!")

    try:
        jsonStr = open(filepath, 'r').read()
        data = json.loads(jsonStr)
        pack = Pack.create(name=packname)

        for query_name, query in data['queries'].items():
            q = Query.query.filter(Query.name == query_name).first()

            if not q:
                q = Query.create(name=query_name, **query)
                pack.queries.append(q)
                print("Adding new query %s to pack %s", q.name, pack.name)
                continue

            if q in pack.queries:
                continue

            if q.sql == query['query']:
                print("Adding existing query %s to pack %s", q.name, pack.name)
                pack.queries.append(q)
            else:
                q2 = Query.create(name=query_name, **query)
                print("Created another query named %s, but different sql: %r vs %r", query_name, q2.sql.encode('utf-8'),
                      q.sql.encode('utf-8'))
                pack.queries.append(q2)
        pack.save()
    except Exception as error:
        print("Failed to create pack {0} - {1}".format(packname, error))
        exit(1)
    else:
        print("Created pack {0}".format(pack.name))
        exit(0)


@manager.command
def add_default_options():
    existing_option = Options.query.filter(Options.name == PolyLogyxServerDefaults.plgx_config_all_options).first()

    for k, v in PolyLogyxConstants.DEFAULT_OPTIONS.items():
        option = Options.query.filter(Options.name == k).first()
        if option:
            option.option = v
            option.update(option)
        else:
            Options.create(name=k, option=v)

    if existing_option:
        existing_option.option = json.dumps(PolyLogyxConstants.DEFAULT_OPTIONS)
        existing_option.update(option)
    else:
        Options.create(name=PolyLogyxServerDefaults.plgx_config_all_options, option=json.dumps(PolyLogyxConstants.DEFAULT_OPTIONS))
    exit(0)


@manager.option('--filepath')
def add_rules(filepath):
    with open(filepath) as f:
        rules = json.load(f)

    for name, data in rules.items():
        rule = Rule.query.filter_by(name=data['name']).first()
        if rule:
            sys.stderr.write('Updating rule.. ' + rule.name)
            if 'technique_id' in data:
                if data['technique_id']:
                    rule.tactics = data['tactics']
                    rule.technique_id = data['technique_id']
                    rule.description = data['description']
                    rule.conditions = data['conditions'],
                    rule.conditions = rule.conditions[0]
                    if 'type' not in data:
                        rule.type = Rule.MITRE
                    else:
                        rule.type = data['type']
                    rule.save(rule)

        else:
            sys.stderr.write('Creating rule.. ' + data['name'])
            severity = Rule.WARNING
            try:
                if data['severity']:
                    severity = data['severity']
            except:
                pass
            if 'technique_id' in data:
                if data['technique_id']:
                    rule = Rule(name=data['name'],
                                alerters=data['alerters'],
                                description=data['description'],
                                conditions=data['conditions'],
                                status='ACTIVE',
                                technique_id=data['technique_id'],
                                tactics=data['tactics'],
                                severity=severity,
                                type=Rule.MITRE,
                                updated_at=dt.datetime.utcnow(), recon_queries=json.dumps(UtilQueries.ALERT_RECON_QUERIES_JSON))
            else:
                rule = Rule(name=data['name'],
                            alerters=data['alerters'],
                            description=data['description'],
                            conditions=data['conditions'],
                            status='ACTIVE',
                            severity=severity,
                            updated_at=dt.datetime.utcnow(), recon_queries=json.dumps(UtilQueries.ALERT_RECON_QUERIES_JSON))
            rule.save()



@manager.option('--purge_data_duration')
def delete_historical_data(purge_data_duration):
    existingSettingObj = Settings.query.filter(Settings.name == 'purge_data_duration').first()

    if existingSettingObj:
        current_app.logger.info("Delete duration already set")
    else:
        Settings.create(name='purge_data_duration', setting=purge_data_duration)

 
@manager.option('username')
@manager.option('--password', default=None)
@manager.option('--email', default=None)
def add_user(username, password, email):
    from polylogyx.models import User

    if User.query.filter_by(username=username).first():
        raise ValueError("Username already exists!")

    # password = getpass.getpass(stream=sys.stderr)

    try:
        user = User.create(
            username=username,
            email=email or username,
            password=password,
        )
    except Exception as error:
        print("Failed to create user {0} - {1}".format(username, error))
        exit(1)
    else:
        print("Created user {0}".format(user.username))
        exit(0)



@manager.option('--username')
@manager.option('--password', default=None)
@manager.option('--email', default=None)
def update_user(username, password, email):
    from polylogyx.models import User
    user=User.query.filter_by(username=username).first()
    if not user :
        raise ValueError("User with this username doesn't exists!")

    # password = getpass.getpass(stream=sys.stderr)

    try:

        user.update(
            password=bcrypt.generate_password_hash(password.encode("utf-8")).decode("utf-8"))
        print("Successfully updated password for user {0}".format(user.username))

    except Exception as error:
        print("Failed to create user {0} - {1}".format(username, error))
        exit(1)
    exit(0)


if __name__ == '__main__':
    manager.run()
