# -*- coding: utf-8 -*-
import base64
import os

from flask import Flask, render_template, current_app, url_for

from polylogyx.blueprints.external_api import blueprint as external_api
from polylogyx.assets import assets
from polylogyx.extensions import (
    bcrypt, csrf, db, ldap_manager, login_manager,
    mail, make_celery, migrate, sentry
)
from polylogyx.manage import blueprint as backend
from polylogyx.models import EmailRecipient, Settings
from polylogyx.settings import ProdConfig
from polylogyx.tasks import celery

from polylogyx.utils import get_node_health, pretty_field, pretty_operator, jinja2_escapejs_filter, render_column, \
    jinja2_to_json_filter, jinja2_array_to_string_filter, date_diff


def create_app(config=ProdConfig):
    app = Flask(__name__)
    app.config.from_object(config)
    app.config.from_envvar('POLYLOGYX_SETTINGS', silent=True)

    register_blueprints(app)
    register_errorhandlers(app)
    register_loggers(app)
    register_extensions(app)
    register_auth_method(app)
    register_filters(app)
    return app


def register_blueprints(app):
    # if the POLYLOGYX_NO_MANAGER environment variable isn't set,
    # register the backend blueprint. This is useful when you want
    # to only deploy the api as a standalone service.

    app.register_blueprint(external_api, url_prefix="/services/api/v0",name="external_api")

    csrf.exempt(external_api)

    app.register_blueprint(backend)



def register_extensions(app):
    bcrypt.init_app(app)
    csrf.init_app(app)
    db.init_app(app)

    migrate.init_app(app, db)
    try:
        set_email_sender(app)
    except:
        print('No email address configured')

    assets.init_app(app)
    mail.init_app(app)
    make_celery(app, celery)
    login_manager.init_app(app)
    sentry.init_app(app)
    try:
        set_email_value(app)
    except:
        print('cannot connect to database')

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
        handler = RotatingFileHandler(logfile, maxBytes=1024*1024, backupCount=10)

    levelname = app.config['POLYLOGYX_LOGGING_LEVEL']

    if levelname in ('DEBUG', 'INFO', 'WARN', 'WARNING', 'ERROR', 'CRITICAL'):
        handler.setLevel(getattr(logging, levelname))

    formatter = logging.Formatter(app.config['POLYLOGYX_LOGGING_FORMAT'])
    handler.setFormatter(formatter)

    app.logger.addHandler(handler)


def register_errorhandlers(app):
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


def register_filters(app):
    app.jinja_env.filters['health'] = get_node_health
    app.jinja_env.filters['pretty_field'] = pretty_field
    app.jinja_env.filters['pretty_operator'] = pretty_operator
    app.jinja_env.filters['escapejs'] = jinja2_escapejs_filter
    app.jinja_env.filters['to_json'] = jinja2_to_json_filter
    app.jinja_env.filters['date_diff'] = date_diff
    app.jinja_env.filters['render'] = render_column
    app.jinja_env.filters['array_to_string'] = jinja2_array_to_string_filter





def register_auth_method(app):
    from polylogyx.users import views
    app.register_blueprint(views.blueprint)

    if app.config['POLYLOGYX_AUTH_METHOD'] is None:
        from polylogyx.users.mixins import NoAuthUserMixin
        login_manager.anonymous_user = NoAuthUserMixin
        return

    login_manager.login_view = 'users.login'
    login_manager.login_message_category = 'warning'

    if app.config['POLYLOGYX_AUTH_METHOD'] == 'ldap':
        ldap_manager.init_app(app)
        return

    # no other authentication methods left, falling back to OAuth

    if app.config['POLYLOGYX_AUTH_METHOD'] != 'polylogyx':
        login_manager.login_message = None
        login_manager.needs_refresh_message = None

        from polylogyx.users.oauth import OAuthLogin
        provider = OAuthLogin.get_provider(app.config['POLYLOGYX_AUTH_METHOD'])
        provider.init_app(app)


def set_email_value(app):
    with app.app_context():
        from polylogyx.settings import Config as config
        emailRecipients = db.session.query(EmailRecipient).filter(EmailRecipient.status == 'active').all()
        emailRecipientList = []
        config.EMAIL_RECIPIENTS = None
        if emailRecipients and len(emailRecipients) > 0:
            for emailRecipient in emailRecipients:
                emailRecipientList.append(emailRecipient.recipient)
            config.EMAIL_RECIPIENTS = emailRecipientList


def set_email_sender(app):
    with app.app_context():
        emailSender = db.session.query(Settings).filter(Settings.name == 'email').first().setting
        emailPassword = base64.b64decode(
            db.session.query(Settings).filter(Settings.name == 'password').first().setting)
        smtpPort = db.session.query(Settings).filter(Settings.name == 'smtpPort').first().setting
        smtpAddress = db.session.query(Settings).filter(Settings.name == 'smtpAddress').first().setting
        current_app.config['MAIL_USERNAME'] = emailSender
        current_app.config['MAIL_PASSWORD'] = emailPassword
        current_app.config['MAIL_SERVER'] = smtpAddress
        current_app.config['MAIL_PORT'] = int(smtpPort)
