# -*- coding: utf-8 -*-
import os

from flask import Flask, render_template
from flask_cors import CORS

from polylogyx.api import blueprint as api
from polylogyx.extensions import (
    csrf, db, log_tee,
    mail, make_celery, migrate, rule_manager, sentry,
    threat_intel)
from polylogyx.settings import ProdConfig
from polylogyx.tasks import celery
from flask_caching import Cache

def create_app(config=ProdConfig):
    app = Flask(__name__)
    CORS(app)
    cache=Cache(app=app, config={'CACHE_TYPE': 'simple'})

    app.config.from_object(config)
    app.config.from_envvar('POLYLOGYX_SETTINGS', silent=True)

    register_blueprints(app)
    register_loggers(app)
    register_extensions(app)
    # cache.init_app(app)

    return app


def register_blueprints(app):
    app.register_blueprint(api)
    csrf.exempt(api)

def register_extensions(app):
    csrf.init_app(app)
    db.init_app(app)

    migrate.init_app(app, db)


    log_tee.init_app(app)
    rule_manager.init_app(app)
    threat_intel.init_app(app)

    mail.init_app(app)
    make_celery(app, celery)
    sentry.init_app(app)

    mail.init_app(app)
    if app.config['ENFORCE_SSL']:
        # Due to architecture of flask-sslify,
        # its constructor expects to be launched within app context
        # unless app is passed.
        # As a result, we cannot create sslify object in `extensions` module
        # without getting an error.
        from flask_sslify import SSLify
        SSLify(app)


def register_loggers(app):
    from logging.handlers import RotatingFileHandler
    import logging
    import sys

    logfile = app.config['POLYLOGYX_LOGGING_FILENAME']

    if logfile == '-':
        handler = logging.StreamHandler(sys.stdout)
    else:
        handler = RotatingFileHandler(logfile, maxBytes=10*1024*1024, backupCount=10)

    levelname = app.config['POLYLOGYX_LOGGING_LEVEL']

    if levelname in ('DEBUG', 'INFO', 'WARN', 'WARNING', 'ERROR', 'CRITICAL'):
        handler.setLevel(getattr(logging, levelname))

    formatter = logging.Formatter(app.config['POLYLOGYX_LOGGING_FORMAT'])
    handler.setFormatter(formatter)

    app.logger.addHandler(handler)


def register_threat_intel(app):
    from logging.handlers import RotatingFileHandler
    import logging
    import sys

    logfile = app.config['POLYLOGYX_LOGGING_FILENAME']

    if logfile == '-':
        handler = logging.StreamHandler(sys.stdout)
    else:
        handler = RotatingFileHandler(logfile, maxBytes=10*1024*1024, backupCount=10)

    levelname = app.config['POLYLOGYX_LOGGING_LEVEL']

    if levelname in ('DEBUG', 'INFO', 'WARN', 'WARNING', 'ERROR', 'CRITICAL'):
        handler.setLevel(getattr(logging, levelname))

    formatter = logging.Formatter(app.config['POLYLOGYX_LOGGING_FORMAT'])
    handler.setFormatter(formatter)

    app.logger.addHandler(handler)

def register_error_handlers(app):
    """Register error handlers."""

    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, 'code', 500)
        if 'POLYLOGYX_NO_MANAGER' in os.environ:
            return '', 400
        return render_template('{0}.html'.format(error_code)), error_code

    for errcode in [401, 403, 404, 500]:
        app.errorhandler(errcode)(render_error)




