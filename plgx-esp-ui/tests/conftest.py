# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""

import json, os

import pytest
from webtest import TestApp

from polylogyx.application import create_app
from polylogyx.database import db as _db
from polylogyx.settings import TestConfig


from .factories import (
    NodeFactory, RuleFactory, UserFactory, DashboardDataFactory, AlertsFactory, ResultLogFactory,
    StatusLogFactory, CarveSessionFactory,
    DistributedQueryFactory, DistributedQueryTaskFactory, PackFactory, QueryFactory,
    OptionsFactory, DefaultFiltersFactory, DefaultQueryFactory, ConfigFactory, TagFactory,
    SettingsFactory, IocIntelFactory, ThreatIntelCredentialsFactory, HandlingTokenFactory,
    NodeQueryCountFactory
)


@pytest.yield_fixture(scope='function')
def app():
    """An application for the tests."""
    _app = create_app(config=TestConfig)
    ctx = _app.test_request_context()
    ctx.push()

    try:
        yield _app
    finally:
        ctx.pop()


@pytest.fixture(scope='function')
def client(app):
    return app.test_client()


@pytest.yield_fixture(scope='function')
def api():
    """An api instance for the tests, no manager"""
    import os
    # the mere presence of the env var should prevent the manage
    # blueprint from being registered
    os.environ['POLYLOGYX_NO_MANAGER'] = '1'

    _app = create_app(config=TestConfig)
    ctx = _app.test_request_context()
    ctx.push()

    try:
        yield _app
    finally:
        ctx.pop()


@pytest.fixture(scope='function')
def testapp(app):
    """A Webtest app."""
    return TestApp(app)


@pytest.fixture(scope='function')
def testapi(api):
    return TestApp(api)


@pytest.yield_fixture(scope='function')
def db(app):
    """A database for the tests."""
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    # Explicitly close DB connection
    _db.session.close()
    _db.drop_all()


@pytest.fixture
def url_prefix():
    return "/services/api/v1"


@pytest.fixture
def token(client, user, url_prefix):
    data = {'username': 'admin', 'password': 'admin'}
    res = client.post(url_prefix + '/login', data=json.dumps(data), headers={'Accept': None})
    return json.loads(res.data)['token']


@pytest.fixture
def node(db):
    """A node for the tests."""
    node = NodeFactory(host_identifier='foobar', enroll_secret='foobar',
                       platform='windows', node_info={}, os_info={}, network_info={},
                       host_details={})
    db.session.commit()
    return node


@pytest.fixture
def status_log(db, node):
    """A Status Log row for the tests."""
    log = StatusLogFactory(
        node_id=1,
        line=2,
        message="done, it's completed",
        severity=1,
        filename='foobar_file',
        version='4.0.2'
    )
    db.session.commit()
    return log



@pytest.fixture
def rule(db):
    """A rule for the tests."""
    rule = RuleFactory(
        name='testrule',
        description='kung = $kung',
        alerters=[],
        conditions={}
    )
    db.session.commit()
    return rule


@pytest.fixture
def user(db):
    user = UserFactory(
        username='admin',
        password='admin'
    )
    db.session.commit()
    return user


@pytest.fixture
def dashboard_data(db):
    fp = os.getcwd() + '/tests/TestUtilFiles/dashboard_data.json'
    with open(fp) as json_data:
        data = json.load(json_data)
    data = data['data']
    dashboard_data = DashboardDataFactory(
        name='dashboard',
        data=data
    )
    db.session.commit()
    return dashboard_data


@pytest.fixture
def alerts(db, node, rule):
    """An alert for the tests."""
    fp = os.getcwd() + '/tests/TestUtilFiles/sample_alerts_data.json'
    with open(fp) as json_data:
        data = json.load(json_data)
    message = data['message']
    source_data = data['source_data']
    alerts1_message = data['alerts1_message']
    recon_querries = data['recon_querries']

    alerts = AlertsFactory(
        query_name='win_file_events',
        message=message,
        node_id=1,
        rule_id=1,
        severity='LOW',
        type='Threat Intel',
        recon_queries={},
        result_log_uid='f41d1a87-557a-4bbf-9e60-ed1c03265634',
        source='virustotal',
        source_data=source_data
    )

    alerts1 = AlertsFactory(
        query_name='win_file_events',
        message=alerts1_message,
        node_id=1,
        rule_id=1,
        severity='INFO',
        type='rule',
        recon_queries=recon_querries,
        result_log_uid='ac11ae27-59a5-47c9-9a05-f17e335f04f9',
        source='rule',
        source_data={}
    )

    db.session.commit()
    # return alerts


@pytest.fixture
def result_log(db, node):
    fp = os.getcwd() + '/tests/TestUtilFiles/sample_result_log.json'
    with open(fp) as json_data:
        data = json.load(json_data)
    columns1 = data['columns1']
    columns2 = data['columns2']
    columns3 = data['columns3']
    result_log1 = ResultLogFactory(
        name='kernel_modules',
        action='added',
        columns=columns1,
        node_id=1,
        status=2
    )
    result_log2 = ResultLogFactory(
        name='kernel_modules',
        action='added',
        columns=columns2,
        node_id=1,
        status=2
    )
    result_log3 = ResultLogFactory(
        name='kernel_modules',
        action='added',
        columns=columns3,
        node_id=1,
        status=2
    )
    result_log4 = ResultLogFactory(
        name='win_process_events',
        action='added',
        columns=columns3,
        node_id=1,
        status=2
    )
    db.session.commit()
    # return result_log


@pytest.fixture
def carve_session(db, node):
    carve_session = CarveSessionFactory(
        node_id=1,
        session_id='foobar_session_id',
        carve_guid='foo_carve_guid',
        carve_size=4608,
        block_size=30000,
        block_count=1,
        completed_blocks=1,
        archive='foo_archieve.tar',
        request_id='foobar_request_id',
        status='COMPLETED'
    )
    db.session.commit()
    return carve_session


@pytest.fixture
def distributed_query(db):
    distributed_query1 = DistributedQueryFactory(
        description='foo',
        sql='select * from foo'
    )
    distributed_query2 = DistributedQueryFactory(
        description='foobar',
        sql='select * from foobar'
    )
    db.session.commit()
    # return distributed_query


@pytest.fixture
def distributed_query_task(db, distributed_query, node):
    distributed_query_task = DistributedQueryTaskFactory(
        save_results_in_db=True,
        distributed_query_id=1,
        guid='foobar_guid',
        node_id=1
    )
    db.session.commit()
    return distributed_query_task


@pytest.fixture
def packs(db):
    packs = PackFactory(
        name='pytest_pack',
        description='pytest_pack'
    )
    db.session.commit()
    return packs


@pytest.fixture
def queries(db):
    queries = QueryFactory(
        name='test_query',
        sql='select * from osquery_info;',
        interval=10,
        platform='all',
        version='2.9.0',
        description='Processes',
        value='Processes',
        shard=100,
        snapshot=True
    )
    db.session.commit()
    return queries


@pytest.fixture
def options(db):
    options = OptionsFactory(
        option='logger_plugin',
        name='tls,filesystem'
    )
    db.session.commit()
    return options


@pytest.fixture
def config(db):
    config1 = ConfigFactory(
        platform='windows',
        arch='x86',
        is_active=True
    )
    config2 = ConfigFactory(
        platform='windows',
        arch='x86_64',
        is_active=True
    )
    config3 = ConfigFactory(
        platform='linux',
        arch='x86_64',
        is_active=True
    )
    config4 = ConfigFactory(
        platform='darwin',
        arch='x86_64',
        is_active=True
    )
    db.session.commit()


@pytest.fixture
def default_query(config, db):
    default_query1 = DefaultQueryFactory(
        name='drivers',
        sql='select * from drivers;',
        interval=86400,
        platform='windows',
        arch='x86',
        description='Windows Drivers',
        removed=False,
        status=True,
        config_id=1
    )
    default_query2 = DefaultQueryFactory(
        name='win_socket_events',
        sql='select * from win_socket_events;',
        interval=240,
        platform='windows',
        arch='x86_64',
        description='Windows Socket Events',
        removed=False,
        status=True,
        config_id=2
    )
    default_query3 = DefaultQueryFactory(
        name='file_events',
        sql='SELECT * FROM file_events;',
        interval=10,
        platform='linux',
        arch='x86_64',
        removed=False,
        status=True,
        config_id=3
    )
    default_query4 = DefaultQueryFactory(
        name='platform_info',
        sql='SELECT * FROM platform_info;',
        interval=28800,
        platform='darwin',
        arch='x86_64',
        description='Information about EFI/UEFI/ROM and platform/boot.',
        removed=False,
        status=True,
        config_id=4
    )
    db.session.commit()
    # return default_query


@pytest.fixture
def default_filter(config, db):
    fp = os.getcwd() + '/tests/TestUtilFiles/sample_default_filters.json'
    with open(fp) as json_data:
        data = json.load(json_data)
    filter2 = data['filter2']
    filter3 = data['filter3']
    filter4 = data['filter4']
    default_filter1 = DefaultFiltersFactory(
        filters={},
        platform='windows',
        arch='x86',
        config_id=1
    )
    default_filter2 = DefaultFiltersFactory(
        filters=filter2,
        platform='darwin',
        arch='x86_64',
        config_id=4
    )
    default_filter3 = DefaultFiltersFactory(
        filters=filter3,
        platform='windows',
        arch='x86_64',
        config_id=2
    )
    default_filter4 = DefaultFiltersFactory(
        filters=filter4,
        platform='linux',
        arch='x86_64',
        config_id=3
    )
    db.session.commit()


@pytest.fixture
def tag(db):
    tag = TagFactory(
        value='test'
    )
    db.session.commit()
    return tag


@pytest.fixture
def settings(db):
    settings = SettingsFactory(
        name='',
        setting = ''
    )
    db.session.commit()
    return settings


@pytest.fixture
def ioc_intel(db):
    remote_address = IocIntelFactory(
        type='remote_address',
        intel_type='self',
        value='23.13.5.28,5.45.6.56',
        threat_name='test-intel_ipv4',
        severity='WARNING'
    )
    domain_name = IocIntelFactory(
        type='domain_name',
        intel_type='self',
        value='bigbasket.com,slackabc.com',
        threat_name='test-intel_domain_name',
        severity='WARNING'
    )
    md5 = IocIntelFactory(
        type='md5',
        intel_type='self',
        value='3h8dgfdjjkdgm0,9sd77jkdsgv80',
        threat_name='test-intel_md5',
        severity='INFO'
    )
    db.session.commit()


@pytest.fixture
def threat_intel_credentials(db):
    ibm_x_credentials = ThreatIntelCredentialsFactory(
        intel_name='ibmxforce',
        credentials={'key': 'ibm_x_key', 'pass':'ibm_x_pass'}
    )
    vt_credentials = ThreatIntelCredentialsFactory(
        intel_name='virustotal',
        credentials={'key':'virustotal'}
    )
    alienvault_credentials = ThreatIntelCredentialsFactory(
        intel_name='alienvault',
        credentials={'key': 'alienvault'}
    )
    db.session.commit()


@pytest.fixture
def handling_token(db):
    handling_token = HandlingTokenFactory(
        token='',
        user='foo'
    )
    db.session.commit()
    return handling_token


@pytest.fixture
def node_query_count(db, node):
    nodequerycount = NodeQueryCountFactory(
        total_results = 14,
        query_name = 'kernel_modules',
        node_id = 1
    )
    db.session.commit()
    return nodequerycount
