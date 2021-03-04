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
from polylogyx.models import Query, Rule, Options, Settings, DefaultFilters, DefaultQuery, Config,VirusTotalAvEngines
from polylogyx.settings import CurrentConfig
from polylogyx.constants import PolyLogyxServerDefaults, UtilQueries, PolyLogyxConstants, DefaultInfoQueries
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
def add_default_queries( filepath, platform, arch, type):
    try:
        sys.stderr.write('Adding queries for ' + platform)
        jsonStr = open(filepath, 'r').read()
        query = json.loads(jsonStr)
        queries = query['schedule']
        is_active = False
        if int(type) == 0 or int(type) == 1:
            is_active = True
        config = db.session.query(Config).filter(Config.type == type).filter(Config.arch == arch).filter(
            Config.platform == platform).first()
        if not config:
            config = Config.create(platform=platform, arch=arch, type=type, is_active=is_active)

        for query_key in queries.keys():
            if query_key not in DefaultInfoQueries.DEFAULT_VERSION_INFO_QUERIES.keys():
                query_filter = DefaultQuery.query.filter_by(platform=platform).filter_by(name=query_key).filter_by(config_id=config.id)
                config_id = config.id
            else:
                query_filter = DefaultQuery.query.filter_by(platform=platform).filter_by(name=query_key)
                config_id = None
            if arch == DefaultQuery.ARCH_x86:
                query_filter = query_filter.filter_by(arch=DefaultQuery.ARCH_x86)

            query = query_filter.first()
            try:
                if 'snapshot' in queries[query_key]:
                    snapshot = queries[query_key]['snapshot']
                else:
                    snapshot = False

                if query:
                    sys.stderr.write("Query name " + query_key + " already exists, updating..!")
                    query.sql = queries[query_key]['query']
                    query.interval = queries[query_key]['interval']
                    query.status = queries[query_key]['status']
                    query.snapshot = snapshot
                    query.update(query)
                else:
                    sys.stderr.write(query_key+" does not exist, adding new...")
                    status = True
                    if "status" in queries[query_key]:
                        status = queries[query_key]['status']

                    DefaultQuery.create(name=query_key, sql=queries[query_key]['query'],arch=arch,config_id=config_id,
                                            interval=queries[query_key]['interval'], status=status, platform=platform,
                                            description=queries[query_key].get('description'), snapshot=snapshot)
            except Exception as error:
                sys.stderr.write(str(error))
    except Exception as error:
        raise (str(error))


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
        existing_option.update(existing_option)
    else:
        Options.create(name=PolyLogyxServerDefaults.plgx_config_all_options, option=json.dumps(PolyLogyxConstants.DEFAULT_OPTIONS))
    exit(0)


@manager.option('--filepath')
def add_rules(filepath):
    with open(filepath) as f:
        rules = json.load(f)

    for name, data in rules.items():
        try:
            rule = Rule.query.filter_by(name=data['name']).first()
            severity = data.get('severity', Rule.WARNING)
            description = data.get('description', '')
            type = data.get('type', Rule.MITRE)
            tactics = data.get('tactics')
            alerters = data.get('alerters', ["debug"])
            technique_id = data.get('technique_id')
            if not technique_id:
                type=None

            if rule:
                sys.stderr.write('Updating rule.. ' + rule.name)
                rule.tactics = tactics
                rule.technique_id = technique_id
                rule.description = description
                rule.conditions = data['conditions'],
                rule.severity=severity
                rule.type = type
                rule.alerters=alerters
                rule.save(rule)
            else:
                sys.stderr.write('Creating rule.. ' + data['name'])
                rule = Rule(name=data['name'],
                            alerters=alerters,
                            description=description,
                            conditions=data['conditions'],
                            status='ACTIVE',
                            technique_id=technique_id,
                            tactics=tactics,
                            severity=severity,
                            type=type,
                            updated_at=dt.datetime.utcnow(),
                            recon_queries=json.dumps(UtilQueries.ALERT_RECON_QUERIES_JSON))

                rule.save()
        except Exception as e:
            print(e)


@manager.option('--filepath')
def add_default_vt_av_engines( filepath):
    try:
        sys.stderr.write('Adding Virus total Avengines ')
        jsonStr = open(filepath, 'r').read()
        av_engine = json.loads(jsonStr)
        av_engines = av_engine['av_engines']
        for key in av_engines.keys():
            av_engine_Obj = VirusTotalAvEngines.query.filter(VirusTotalAvEngines.name == key).first()
            if av_engine_Obj:
                av_engine_Obj.status=av_engines[key]['status']
            else:
                VirusTotalAvEngines.create(name=key, status=av_engines[key]['status'])
    except Exception as error:
        raise(str(error))


@manager.option('--vt_min_match_count')
def update_vt_match_count(vt_min_match_count):
    existingSettingObj = Settings.query.filter(Settings.name == 'virustotal_min_match_count').first()

    if existingSettingObj:
        current_app.logger.info("Match count already set")
    else:
        Settings.create(name='virustotal_min_match_count', setting=vt_min_match_count)


@manager.option('--purge_data_duration')
def delete_historical_data(purge_data_duration):
    existingSettingObj = Settings.query.filter(Settings.name == 'purge_data_duration').first()

    if existingSettingObj:
        current_app.logger.info("Delete duration already set")


@manager.option('--purge_data_duration', default=60)
@manager.option('--alert_aggregation_duration', default=60)
def update_settings(purge_data_duration, alert_aggregation_duration):
    purge_dur_setting = Settings.query.filter(Settings.name == 'purge_data_duration').first()
    alert_aggr_dur_setting = Settings.query.filter(Settings.name == 'alert_aggregation_duration').first()

    if purge_dur_setting:
        current_app.logger.info("Purge duration is already set")
    else:
        Settings.create(name='purge_data_duration', setting=purge_data_duration)

    if alert_aggr_dur_setting:
        current_app.logger.info("Alert aggregation duration is already set")
    else:
        Settings.create(name='alert_aggregation_duration', setting=alert_aggregation_duration)


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


@manager.option('--filepath')
def add_release_versions(filepath):
    from polylogyx.models import ReleasedAgentVersions

    jsonStr = open(filepath, 'r').read()
    data = json.loads(jsonStr)
    for release_version, dictionary in data.items():
        for platform, platform_dict in dictionary.items():
            agent_version_history = ReleasedAgentVersions.query.filter(ReleasedAgentVersions.platform == platform).filter(ReleasedAgentVersions.platform_release == release_version).first()
            if agent_version_history:
                agent_version_history.extension_version = platform_dict['extension_version']
                agent_version_history.extension_hash_md5 = platform_dict['extension_hash']
                agent_version_history.update(agent_version_history)
            else:
                ReleasedAgentVersions.create(platform=platform, platform_release=release_version, extension_version=platform_dict['extension_version'], extension_hash_md5=platform_dict['extension_hash'])


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


if __name__ == '__main__':
    manager.run()
