# -*- coding: utf-8 -*-
import datetime as dt
import string
import uuid
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature

from flask import json, current_app
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property

from polylogyx.database import (
    Column,
    Table,
    ForeignKey,
    Index,
    Model,
    SurrogatePK,
    db,
    reference_col,
    relationship,
    ARRAY,
    JSONB,
    INET,
    declared_attr,
)
from polylogyx.extensions import bcrypt

querypacks = Table(
    'query_packs',
    Column('pack.id', db.Integer, ForeignKey('pack.id')),
    Column('query.id', db.Integer, ForeignKey('query.id'))
)

pack_tags = Table(
    'pack_tags',
    Column('tag.id', db.Integer, ForeignKey('tag.id')),
    Column('pack.id', db.Integer, ForeignKey('pack.id'), index=True)
)

node_tags = Table(
    'node_tags',
    Column('tag.id', db.Integer, ForeignKey('tag.id')),
    Column('node.id', db.Integer, ForeignKey('node.id'), index=True)
)

query_tags = Table(
    'query_tags',
    Column('tag.id', db.Integer, ForeignKey('tag.id')),
    Column('query.id', db.Integer, ForeignKey('query.id'), index=True)
)

file_path_tags = Table(
    'file_path_tags',
    Column('tag.id', db.Integer, ForeignKey('tag.id')),
    Column('file_path.id', db.Integer, ForeignKey('file_path.id'), index=True)
)

class Tag(SurrogatePK, Model):
    value = Column(db.String, nullable=False, unique=True)

    nodes = relationship(
        'Node',
        secondary=node_tags,
        back_populates='tags',
    )

    packs = relationship(
        'Pack',
        secondary=pack_tags,
        back_populates='tags',
    )

    queries = relationship(
        'Query',
        secondary=query_tags,
        back_populates='tags',
    )

    file_paths = relationship(
        'FilePath',
        secondary=file_path_tags,
        back_populates='tags',
    )

    def __init__(self, value, **kwargs):
        self.value = value

    def __repr__(self):
        return '<Tag: {0.value}>'.format(self)

    @property
    def packs_count(self):
        return db.session.object_session(self) \
            .query(Pack.id).with_parent(self, 'packs').count()

    @property
    def nodes_count(self):
        return db.session.object_session(self) \
            .query(Node.id).with_parent(self, 'nodes').count()

    @property
    def queries_count(self):
        return db.session.object_session(self) \
            .query(Query.id).with_parent(self, 'queries').count()

    @property
    def file_paths_count(self):
        return db.session.object_session(self) \
            .query(FilePath.id).with_parent(self, 'file_paths').count()

    def to_dict(self):
        return self.value


class Query(SurrogatePK, Model):
    name = Column(db.String, nullable=False)
    sql = Column(db.String, nullable=False)
    interval = Column(db.Integer, default=3600)
    platform = Column(db.String)
    version = Column(db.String)
    description = Column(db.String)
    value = Column(db.String)
    removed = Column(db.Boolean, nullable=False, default=True)
    snapshot = Column(db.Boolean, nullable=False, default=False)
    shard = Column(db.Integer)

    packs = relationship(
        'Pack',
        secondary=querypacks,
        back_populates='queries',
    )

    tags = relationship(
        'Tag',
        secondary=query_tags,
        back_populates='queries',
        lazy='joined',
    )

    def __init__(self, name, query=None, sql=None, interval=3600, platform=None,
                 version=None, description=None, value=None, removed=True,
                 shard=None, snapshot=False, **kwargs):
        self.name = name
        self.sql = query or sql
        self.interval = int(interval)
        self.platform = platform
        self.version = version
        self.description = description
        self.value = value
        self.removed = removed
        self.snapshot = snapshot
        self.shard = shard

    def __repr__(self):
        return '<Query: {0.name}>'.format(self)

    def to_dict(self):
        return {
            'id': self.id,
            'query': self.sql,
            'interval': self.interval,
            'platform': self.platform,
            'version': self.version,
            'description': self.description,
            'value': self.value,
            'removed': self.removed,
            'shard': self.shard,
            'snapshot': self.snapshot,
            'tags': [r.to_dict() for r in self.tags]
        }


class DefaultQuery(SurrogatePK, Model):
    ARCH_x86="x86"
    ARCH_x64="x86_64"

    name = Column(db.String, nullable=False)
    sql = Column(db.String, nullable=False)
    interval = Column(db.Integer, default=3600)
    platform = Column(db.String)
    arch = Column(db.String,nullable=False)
    version = Column(db.String)
    description = Column(db.String)
    value = Column(db.String)
    removed = Column(db.Boolean, nullable=False, default=True)
    snapshot = Column(db.Boolean, nullable=False, default=False)
    shard = Column(db.Integer)
    status = Column(db.Boolean, nullable=False, default=False)

    def __init__(self, name, query=None, sql=None, interval=3600, platform=None,
                 version=None, description=None, value=None, removed=False,
                 shard=None,status=None, snapshot=False,arch=ARCH_x64, **kwargs):
        self.name = name
        self.sql = query or sql
        self.interval = int(interval)
        self.platform = platform
        self.version = version
        self.description = description
        self.value = value
        self.removed = removed
        self.snapshot = snapshot
        self.shard = shard
        self.status = status
        self.arch=arch

    def __repr__(self):
        return '<Query: {0.name}>'.format(self)

    def to_dict(self):
        return {
            'id': self.id,
            'query': self.sql,
            'interval': self.interval,
            'platform': self.platform,
            'version': self.version,
            'description': self.description,
            'value': self.value,
            'removed': False,
            'shard': self.shard,
            'snapshot': self.snapshot,
            'status': self.status
        }


class DefaultFilters(SurrogatePK, Model):
    ARCH_x86 = "x86"
    ARCH_x64 = "x86_64"

    filters = Column(JSONB)
    platform = Column(db.String, nullable=False)
    arch = Column(db.String,nullable=False)
    apply_by_default = Column(db.Boolean, nullable=False, default=False)
    created_at = Column(db.DateTime, nullable=False)
    updated_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, filters, platform,created_at, apply_by_default=False, arch=ARCH_x64, **kwargs):
        self.filters = filters
        self.platform = platform
        self.apply_by_default = apply_by_default
        self.created_at=created_at
        self.updated_at = dt.datetime.utcnow()
        self.arch = arch

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'filters': json.loads(self.filters),
            'platform': self.platform,
            'arch': self.arch,
            'created_at': dump_datetime(self.created_at),
            'updated_at': dump_datetime(self.updated_at)

        }



class Pack(SurrogatePK, Model):
    INTRUSION_DETECTION = "Intrusion Detection"
    MONITORING = "Monitoring"

    COMPLIANCE_MANAGEMENT = "Compliance and Management"
    FORENSICS_IR = "Forensics and Incident Response"
    GENERAL = "General"
    OTHERS = "Others"

    name = Column(db.String, nullable=False, unique=True)
    platform = Column(db.String)
    version = Column(db.String)
    description = Column(db.String)
    shard = Column(db.Integer)
    category = Column(db.String, default=GENERAL)

    queries = relationship(
        'Query',
        secondary=querypacks,
        back_populates='packs',
    )

    tags = relationship(
        'Tag',
        secondary=pack_tags,
        back_populates='packs',
    )

    def __init__(self, name, platform=None, version=None,
                 description=None, shard=None, **kwargs):
        self.name = name
        self.platform = platform
        self.version = version
        self.description = description
        self.shard = shard

    def __repr__(self):
        return '<Pack: {0.name}>'.format(self)

    def to_dict(self):
        queries = {}
        discovery = []

        for query in self.queries:
            if 'discovery' in (t.value for t in query.tags):
                discovery.append(query.sql)
            else:
                queries[query.name] = query.to_dict()

        return {
            'id': self.id,
            'platform': self.platform,
            'version': self.version,
            'shard': self.shard,
            'discovery': discovery,
            'queries': queries,
            'name': self.name,
            'tags': [r.to_dict() for r in self.tags]
        }

class Node(SurrogatePK, Model):
    NA = 0
    DISABLE = 1
    ENABLE = 2
    node_key = Column(db.String, nullable=False, unique=True)
    platform = Column(db.String)
    enroll_secret = Column(db.String)
    enrolled_on = Column(db.DateTime)
    host_identifier = Column(db.String)
    last_checkin = Column(db.DateTime)
    node_info = Column(JSONB, default={}, nullable=False)
    os_info = Column(JSONB, default={}, nullable=False)
    network_info = Column(JSONB, default={}, nullable=False)
    host_details = Column(JSONB, default={}, nullable=False)

    last_status = Column(db.DateTime)
    last_result = Column(db.DateTime)
    last_config = Column(db.DateTime)
    last_query_read = Column(db.DateTime)
    last_query_write = Column(db.DateTime)

    is_active = Column(db.Boolean, default=True, nullable=False)
    last_ip = Column(INET, nullable=True)


    tags = relationship(
        'Tag',
        secondary=node_tags,
        back_populates='nodes',
        lazy='joined',
    )

    def __init__(self, host_identifier, node_key=None,
                 enroll_secret=None, enrolled_on=None, last_checkin=None,
                 is_active=True, last_ip=None, last_status=None, network_info=None, os_info=None,
                 node_info=None, last_result=None,last_config=None,last_query_read=None,last_query_write=None,
                 **kwargs):
        self.network_info = network_info
        self.node_info = node_info
        self.os_info = os_info
        self.node_key = node_key or str(uuid.uuid4())
        self.host_identifier = host_identifier
        self.enroll_secret = enroll_secret
        self.enrolled_on = enrolled_on
        self.last_checkin = last_checkin
        self.is_active = is_active
        self.last_ip = last_ip
        self.last_status = last_status
        self.last_result = last_result
        self.last_config = last_config
        self.last_query_read = last_query_read
        self.last_query_write = last_query_write



    def __repr__(self):
        return '<Node-{0.id}: node_key={0.node_key}, host_identifier={0.host_identifier}>'.format(self)

    def get_config(self, **kwargs):
        from polylogyx.utils import assemble_configuration
        return assemble_configuration(self)

    def get_new_queries(self, **kwargs):
        from polylogyx.utils import assemble_distributed_queries
        return assemble_distributed_queries(self)

    def node_is_active(self):
        checkin_interval = current_app.config['POLYLOGYX_CHECKIN_INTERVAL']
        if isinstance(checkin_interval, (int, float)):
            checkin_interval = dt.timedelta(seconds=checkin_interval)
        if (dt.datetime.utcnow() - self.last_checkin) < checkin_interval:
            return True
        return False

    @property
    def display_name(self):
        if 'display_name' in self.node_info and self.node_info['display_name']:
            return self.node_info['display_name']
        elif 'hostname' in self.node_info and self.node_info['hostname']:
            return self.node_info['hostname']
        elif 'computer_name' in self.node_info and self.node_info['computer_name']:
            return self.node_info['computer_name']
        else:
            return self.host_identifier

    @property
    def packs(self):
        return db.session.object_session(self) \
            .query(Pack) \
            .join(pack_tags, pack_tags.c['pack.id'] == Pack.id) \
            .join(node_tags, node_tags.c['tag.id'] == pack_tags.c['tag.id']) \
            .filter(node_tags.c['node.id'] == self.id) \
            .options(db.lazyload('*'))

    @property
    def queries(self):
        return db.session.object_session(self) \
            .query(Query) \
            .join(query_tags, query_tags.c['query.id'] == Query.id) \
            .join(node_tags, node_tags.c['tag.id'] == query_tags.c['tag.id']) \
            .filter(node_tags.c['node.id'] == self.id) \
            .options(db.lazyload('*'))

    @hybrid_property
    def child_count(self):
        return db.session.query(db.func.count(DistributedQueryTask.id)).filter(DistributedQueryTask.node_id == self.id
                                                                               , DistributedQueryTask.viewed_at == None,
                                                                               DistributedQueryTask.status == DistributedQueryTask.COMPLETE
                                                                               ).scalar()

    @property
    def file_paths(self):
        return db.session.object_session(self) \
            .query(FilePath) \
            .join(file_path_tags, file_path_tags.c['file_path.id'] == FilePath.id) \
            .join(node_tags, node_tags.c['tag.id'] == file_path_tags.c['tag.id']) \
            .filter(node_tags.c['node.id'] == self.id) \
            .options(db.lazyload('*'))

    def to_dict(self):
        # NOTE: deliberately not including any secret values in here, for now.
        if self.network_info is None:
            self.network_info = {}
        if self.os_info is None:
            self.os_info = {}
        if self.node_info is None:
            self.node_info = {}
        return {
            'id': self.id,
            'display_name': self.display_name,
            'enrolled_on': self.enrolled_on,
            'host_identifier': self.host_identifier,
            'last_checkin': self.last_checkin,
            'platform': self.platform,
            'os_info': self.os_info.copy(),
            'node_info': self.node_info.copy(),
            'network_info': self.network_info.copy(),
            'last_ip': self.last_ip,
            'is_active': self.is_active
        }

    def as_dict(self):
        dictionary = {}
        for c in self.__table__.columns:
            if not (c.name == "enrolled_on" or c.name == "last_checkin"):
                dictionary[c.name] = getattr(self, c.name)
            else:
                if not getattr(self, c.name) == None:
                    dictionary[c.name] = getattr(self, c.name).strftime('%m/%d/%Y %H/%M/%S')
                # else:
                #     dictionary[c.name] = '%0/%0/%0 %0/%0/%0'
        return dictionary


class FilePath(SurrogatePK, Model):
    category = Column(db.String, nullable=False, unique=True)
    target_paths = Column(db.String)

    tags = relationship(
        'Tag',
        secondary=file_path_tags,
        back_populates='file_paths',
        lazy='joined',
    )

    def __init__(self, category=None, target_paths=None, *args, **kwargs):
        self.category = category

        if target_paths is not None:
            self.set_paths(*target_paths)
        elif args:
            self.set_paths(*args)
        else:
            self.target_paths = ''

    def to_dict(self):
        return {
            self.category: self.get_paths()
        }

    def get_paths(self):
        return self.target_paths.split('!!')

    def set_paths(self, *target_paths):
        self.target_paths = '!!'.join(target_paths)




class ResultLog(SurrogatePK, Model):
    NEW = 0
    PENDING = 1
    COMPLETE = 2
    name = Column(db.String, nullable=False)
    timestamp = Column(db.DateTime, default=dt.datetime.utcnow)
    action = Column(db.String)
    columns = Column(JSONB)
    node_id = reference_col('node', nullable=False)
    node = relationship(
        'Node',
        backref=db.backref('result_logs', lazy='dynamic')
    )
    uuid = Column(db.String, nullable=True)
    status = Column(db.Integer, default=NEW, nullable=False)
    task_id= Column(db.String, nullable=True)

    def __init__(self, name=None, action=None, columns=None, timestamp=None,
                 node=None, node_id=None, uuid=None, **kwargs):
        self.name = name
        self.action = action
        self.columns = columns or {}
        self.timestamp = timestamp
        self.uuid = uuid
        if node:
            self.node = node
        elif node_id:
            self.node_id = node_id

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def to_dict(self):
        dictionary = {}
        for c in self.__table__.columns:
            if not c.name == "timestamp":
                dictionary[c.name] = getattr(self, c.name);
            else:
                dictionary[c.name] = getattr(self, c.name).strftime('%m/%d/%Y %H/%M/%S');
        return dictionary

    @declared_attr
    def __table_args__(cls):
        return (
            Index('idx_%s_node_id_timestamp_desc' % cls.__tablename__,
                  'node_id', cls.timestamp.desc()),
        )


class StatusLog(SurrogatePK, Model):
    line = Column(db.Integer)
    message = Column(db.String)
    severity = Column(db.Integer)
    filename = Column(db.String)
    created = Column(db.DateTime, default=dt.datetime.utcnow)
    version = Column(db.String)

    node_id = reference_col('node', nullable=False)
    node = relationship(
        'Node',
        backref=db.backref('status_logs', lazy='dynamic')
    )

    def __init__(self, line=None, message=None, severity=None,
                 filename=None, created=None, node=None, node_id=None,
                 version=None, **kwargs):
        self.line = int(line)
        self.message = message
        self.severity = int(severity)
        self.filename = filename
        self.created = created
        self.version = version
        if node:
            self.node = node
        elif node_id:
            self.node_id = node_id

    @declared_attr
    def __table_args__(cls):
        return (
            Index('idx_%s_node_id_created_desc' % cls.__tablename__,
                  'node_id', cls.created.desc()),
        )


class DistributedQuery(SurrogatePK, Model):
    description = Column(db.String, nullable=True)
    sql = Column(db.String, nullable=False)
    timestamp = Column(db.DateTime, default=dt.datetime.utcnow)
    not_before = Column(db.DateTime, default=dt.datetime.utcnow)
    alert_id = reference_col('alerts', nullable=True)
    alert = relationship(
        'Alerts',
        backref=db.backref('distributed_query'),

    )

    # tasks = relationship(
    #     'DistributedQueryTask',
    #     backref=db.backref('distributed_query_task'),
    #
    # )

    def __init___(self, sql, description=None, not_before=None, alert_id=None):
        self.sql = sql
        self.alert_id = alert_id
        self.description = description
        self.not_before = not_before

    def to_dict(self):
        dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # dict['tasks'] = self.tasks
        return dict


class DistributedQueryTask(SurrogatePK, Model):
    NEW = 0
    PENDING = 1
    COMPLETE = 2
    FAILED = 3
    NOT_SENT = 4
    HIGH = 0

    LOW = 1

    save_results_in_db = Column(db.Boolean, nullable=False, default=False)
    guid = Column(db.String, nullable=False, unique=True)
    status = Column(db.Integer, default=0, nullable=False)
    timestamp = Column(db.DateTime)
    data = Column(JSONB)
    updated_at = Column(db.DateTime, nullable=True, default=None)
    viewed_at = Column(db.DateTime, nullable=True, default=None)
    priority = Column(db.Integer, default=0, nullable=False)
    sql = Column(db.String, nullable=True)

    distributed_query_id = reference_col('distributed_query', nullable=False)
    distributed_query = relationship(
        'DistributedQuery',
        backref=db.backref('tasks',
                           cascade='all, delete-orphan',
                           lazy='dynamic'),
    )

    node_id = reference_col('node', nullable=False)
    node = relationship(
        'Node',
        backref=db.backref('distributed_queries', lazy='dynamic'),
    )

    def __init__(self, node=None, node_id=None,
                 distributed_query=None, save_results_in_db=False, distributed_query_id=None, updated_at=None,
                 priority=0,
                 viewed_at=None, data=None):
        self.guid = str(uuid.uuid4())
        self.updated_at = updated_at
        self.viewed_at = viewed_at
        self.save_results_in_db = save_results_in_db
        self.data = data
        self.priority = priority
        if node:
            self.node = node
        elif node_id:
            self.node_id = node_id
        if distributed_query:
            self.distributed_query = distributed_query
        elif distributed_query_id:
            self.distributed_query_id = distributed_query_id

    @declared_attr
    def __table_args__(cls):
        return (
            Index('idx_%s_node_id_status' % cls.__tablename__, 'node_id', 'status'),
        )

    def to_dict_obj(self):
        return {
            'id': self.id,
            'distributed_query': {
                'description': self.distributed_query.description,
                'sql': self.distributed_query.sql
            },
            'results': self.data,
        }


class DistributedQueryResult(SurrogatePK, Model):
    columns = Column(JSONB)
    timestamp = Column(db.DateTime, default=dt.datetime.utcnow)

    distributed_query_task_id = reference_col('distributed_query_task', nullable=False)
    distributed_query_task = relationship(
        'DistributedQueryTask',
        backref=db.backref('results',
                           cascade='all, delete-orphan',
                           lazy='joined'),
    )

    distributed_query_id = reference_col('distributed_query', nullable=False)
    distributed_query = relationship(
        'DistributedQuery',
        backref=db.backref('results',
                           cascade='all, delete-orphan',
                           lazy='joined'),
    )

    def __init__(self, columns, distributed_query=None, distributed_query_task=None):
        self.columns = columns
        self.distributed_query = distributed_query
        self.distributed_query_task = distributed_query_task

    def to_dict(self):
        dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # dict['tasks'] = self.tasks
        return dict

    def to_dict_obj(self):
        dict = {'columns': self.columns}
        # dict['tasks'] = self.tasks
        return dict


class Rule(SurrogatePK, Model):
    WARNING = "WARNING"
    INFO = "INFO"
    CRITICAL = "CRITICAL"

    MITRE = "MITRE"
    DEFAULT = "DEFAULT"

    name = Column(db.String, nullable=False)
    alerters = Column(ARRAY(db.String), nullable=False)
    description = Column(db.String, nullable=True)
    severity = Column(db.String, nullable=True)

    conditions = Column(JSONB)
    updated_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    status = Column(db.String, nullable=True)
    recon_queries = Column(JSONB)
    type = Column(db.String, nullable=True, default=DEFAULT)
    technique_id=Column(db.String, nullable=True)
    tactics=Column(ARRAY(db.String), nullable=True)

    def __init__(self, name, alerters, description=None, conditions=None, status='ACTIVE', updated_at=None,
                 recon_queries=None, severity=None, type=None,technique_id=None,tactics=[]):
        self.name = name
        self.description = description
        self.alerters = alerters
        self.conditions = conditions
        self.status = status
        self.recon_queries = recon_queries
        self.updated_at = updated_at
        self.severity = severity
        self.type = type
        self.technique_id=technique_id
        self.tactics=tactics

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def as_dict(self):
        dictionary = {}
        for c in self.__table__.columns:
            if not c.name == "updated_at":
                dictionary[c.name] = getattr(self, c.name)
            else:
                dictionary[c.name] = getattr(self, c.name).strftime('%m/%d/%Y %H/%M/%S')
        return dictionary

    @property
    def template(self):
        return string.Template("{name}\r\n\r\n{description}".format(
            name=self.name, description=self.description or '')
        )


class User(UserMixin, SurrogatePK, Model):
    username = Column(db.String(80), unique=True, nullable=False)
    email = Column(db.String)

    password = db.Column(db.String, nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    # oauth related stuff
    social_id = Column(db.String)
    first_name = Column(db.String)
    last_name = Column(db.String)

    def __init__(self, username, password=None, email=None, social_id=None,
                 first_name=None, last_name=None):
        self.username = username
        self.email = email
        if password:
            self.set_password(password)
        else:
            self.password = None

        self.social_id = social_id
        self.first_name = first_name
        self.last_name = last_name

    def set_password(self, password):
        self.update(password=bcrypt.generate_password_hash(password).decode('utf-8'))
        return

    def check_password(self, value):
        if not self.password:
            # still do the computation
            return bcrypt.generate_password_hash(value) and False
        return bcrypt.check_password_hash(self.password, value)

    def generate_auth_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        if not token:
            return None
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user


class Alerts(SurrogatePK, Model):

    RULE="rule"
    THREAT_INTEL="Threat Intel"

    SOURCE_IOC="IOC"

    RESOLVED="RESOLVED"
    OPEN="OPEN"

    CRITICAL="CRITICAL"
    WARNING="WARNING"
    LOW="LOW"
    INFO="INFO"

    query_name = Column(db.String, nullable=False)
    message = Column(JSONB)

    node_id = reference_col('node', nullable=False)
    rule_id = reference_col('rule', nullable=True)
    rule = relationship(
        'Rule',
        backref=db.backref('alerts', lazy='dynamic'),
    )
    severity = Column(db.String, nullable=True)
    type = Column(db.String, nullable=True)

    node = relationship(
        'Node',
        backref=db.backref('alerts', lazy='dynamic'),
    )

    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    severity = Column(db.String)
    recon_queries = Column(JSONB)
    result_log_uid = Column(db.String)
    type = Column(db.String)
    source = Column(db.String)
    source_data = Column(JSONB)
    status = Column(db.String, default=OPEN)



    def __init__(self, message, query_name, node_id, rule_id, recon_queries, result_log_uid, type, source, source_data,
                 severity):
        self.message = message
        self.query_name = query_name
        self.recon_queries = recon_queries
        self.node_id = node_id
        self.rule_id = rule_id

        self.type = type
        self.source = source
        self.source_data = source_data
        self.result_log_uid = result_log_uid
        self.severity = severity
        # self.node=node

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def as_dict(self):
        dictionary = {}
        for c in self.__table__.columns:
            if not c.name == "created_at":
                dictionary[c.name] = getattr(self, c.name);
            else:
                dictionary[c.name] = getattr(self, c.name).strftime('%m/%d/%Y %H/%M/%S');
        return dictionary


class EmailRecipient(SurrogatePK, Model):
    recipient = Column(db.String, nullable=False)
    status = Column(db.String, nullable=False)
    created_at = Column(db.DateTime, nullable=False)
    updated_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)


class Options(SurrogatePK, Model):
    # config = Column(JSONB)
    option = Column(db.String, nullable=False)
    name = Column(db.String, nullable=False)
    created_at = Column(db.DateTime, nullable=False)
    updated_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, name, option, **kwargs):
        self.name = name
        self.option = option


class Settings(SurrogatePK, Model):
    # config = Column(JSONB)
    setting = Column(db.String, nullable=False)
    name = Column(db.String, nullable=False)
    created_at = Column(db.DateTime, nullable=False)
    updated_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, name, setting, **kwargs):
        self.name = name
        self.setting = setting


class NodeData(SurrogatePK, Model):
    # config = Column(JSONB)
    data = Column(JSONB, default={}, nullable=False)
    name = Column(db.String, nullable=False)
    node_id = reference_col('node', nullable=False)
    node = relationship(
        'Node',
        backref=db.backref('node_data', lazy='dynamic'),
    )

    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    updated_at = Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            'name': self.name,
            'data': json.dumps(self.data),
            'updated_at': dump_datetime(self.updated_at)

        }

    def to_dict_obj(self):
        return {
            'name': self.name,
            'data': self.data,
            'updated_at': dump_datetime(self.updated_at)

        }

    def __init__(self, node=None, node_id=None,
                 data=None, name=False, updated_at=None):

        if node:
            self.node = node
        elif node_id:
            self.node_id = node_id
        self.data = data
        self.name = name
        self.updated_at = updated_at


class NodeReconData(SurrogatePK, Model):
    columns = Column(JSONB, default={}, nullable=False)
    node_data_id = reference_col('node_data', nullable=False)
    node_data = relationship(
        'NodeData',
        backref=db.backref('node_recon_data', lazy='dynamic'),
    )

    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    updated_at = Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {

            'columns': json.dumps(self.columns),
            'updated_at': dump_datetime(self.updated_at)

        }

    def to_dict_obj(self):
        return {

            'columns': self.columns,
            'updated_at': dump_datetime(self.updated_at)

        }

    def __init__(self, node_data=None, node_data_id=None,
                 columns=None, updated_at=None):

        if node_data:
            self.node_data = node_data
        elif node_data_id:
            self.node_data_id = node_data_id
        self.columns = columns
        self.updated_at = updated_at


def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return value.strftime("%Y-%m-%d") + ' ' + value.strftime("%H:%M:%S")


class CarveSession(SurrogatePK, Model):
    # StatusQueried for queried carves that did not hit nodes yet
    StatusQueried = "QUERIED"
    # StatusInitialized for initialized carves
    StatusInitialized = "INITIALIZED"
    # StatusInProgress for carves that are on-going
    StatusInProgress = "IN PROGRESS"
    #  StatusCompleted for carves that finalized
    StatusBuilding = "BUILDING"
    #  StatusCompleted for carves that finalized
    StatusCompleted = "COMPLETED"

    node_id = reference_col('node', nullable=False)
    session_id = Column(db.String, nullable=False)
    carve_guid = Column(db.String, nullable=False)

    carve_size = Column(db.Integer)
    block_size = Column(db.Integer)
    block_count = Column(db.Integer)
    completed_blocks=Column(db.Integer,default=0)
    archive = Column(db.String())

    request_id = Column(db.String, nullable=False)
    status = Column(db.String, nullable=False)

    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    updated_at = Column(db.DateTime, nullable=False)
    node = relationship(
        'Node',
        backref=db.backref('carve_session', lazy='dynamic')
    )

    def __init___(self, node_id, session_id=None, carve_guid=None, carve_size=0, block_size=0, block_count=0,
                  archive=None,request_id=None):
        self.node_id = node_id
        self.session_id = session_id
        self.carve_guid = carve_guid
        self.carve_size = carve_size
        self.block_size = block_size
        self.block_count = block_count
        self.archive = archive
        self.request_id=request_id

    def to_dict(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'node_id': self.node_id,
            'session_id': self.session_id,
            'carve_guid': self.carve_guid,
            'carve_size': self.carve_size,
            'block_count': self.block_count,
            'archive': self.archive,
            'created_at': dump_datetime(self.created_at),

        }


class CarvedBlock(SurrogatePK, Model):
    request_id = Column(db.String, nullable=False)
    session_id = Column(db.String, nullable=False)
    block_id = Column(db.Integer, nullable=False)
    data = Column(db.String, nullable=False)
    size = Column(db.Integer, nullable=False)

    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    updated_at = Column(db.DateTime, nullable=False,default=dt.datetime.utcnow)

    def __init___(self, request_id=None, session_id=None, block_id=None, data=None, size=None):
        self.request_id = request_id
        self.session_id = session_id
        self.block_id = block_id
        self.data = data
        self.size = size



class AlertEmail(SurrogatePK, Model):
    alert_id = reference_col('alerts', nullable=False)
    alert = relationship(
        'Alerts',
        backref=db.backref('alert_email', lazy='dynamic'),
    )
    node = Column(db.String, nullable=False)
    status = Column(db.String, nullable=True)
    node_id = reference_col('node', nullable=False)

    node = relationship(
        'Node',
        backref=db.backref('alert_email', lazy='dynamic'),
    )
    body = Column(db.String, nullable=False)

    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    updated_at = Column(db.DateTime, nullable=False)

    def __init__(self, node=None, node_id=None, alert=None, alert_id=None, body=None,
                 status=None, updated_at=dt.datetime.utcnow()):

        if node:
            self.node = node
        elif node_id:
            self.node_id = node_id
        if alert:
            self.alert = alert
        elif alert_id:
            self.alert_id = alert_id
        self.updated_at = updated_at
        self.body = body
        self.status = status


class DashboardData(SurrogatePK, Model):
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    updated_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    name = Column(db.String)
    data = Column(JSONB, default={})

    def __init__(self, name='', data={}, updated_at=dt.datetime.utcnow()):
        self.name = name
        self.data = data
        self.updated_at = updated_at


class PhishTank(SurrogatePK, Model):
    phish_id = Column(db.String, nullable=False)
    verified = Column(db.String)
    url = Column(db.String, nullable=False)
    online = Column(db.String)
    target = Column(db.String)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    updated_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, id, phish_id, verified, url, online, target, updated_at, **kwargs):
        self.verified = verified
        self.phish_id = phish_id
        self.id = id
        self.url = url
        self.online = online
        self.target = target
        self.updated_at = updated_at


class ResultLogScan(SurrogatePK, Model):
    scan_type = Column(db.String, nullable=False)
    scan_value = Column(db.String, nullable=False)
    reputations = Column(JSONB, default={}, nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, scan_type, scan_value, reputations, **kwargs):
        self.scan_type = scan_type
        self.scan_value = scan_value
        self.reputations = reputations


class IOCIntel(SurrogatePK, Model):
    type = Column(db.String, nullable=True)
    intel_type = Column(db.String, nullable=False)
    value = Column(db.String, nullable=False)
    threat_name = Column(db.String, nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    severity = Column(db.String, nullable=False, default='')

    def __init__(self, type, value, threat_name, intel_type, severity, **kwargs):
        self.type = type
        self.value = value
        self.intel_type = intel_type
        self.threat_name = threat_name
        self.severity = severity


class ThreatIntelCredentials(SurrogatePK, Model):
    intel_name = Column(db.String, nullable=True)
    credentials = Column(JSONB, default={}, nullable=False)

    def __init__(self, intel_name, credentials, **kwargs):
        self.intel_name = intel_name
        self.credentials = credentials

# Table to invalidate the token
class HandlingToken(SurrogatePK, Model):
    token = Column(db.String, nullable=False)
    logged_in_at = Column(db.DateTime, default=dt.datetime.utcnow, nullable=False)
    token_expired = Column(db.Boolean, nullable=False, default=False)
    logged_out_at = Column(db.DateTime, nullable=True)
    user = Column(db.String, nullable=False)
