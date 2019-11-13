
# -*- coding: utf-8 -*-

from polylogyx.application import create_app
from polylogyx.settings import CurrentConfig
from polylogyx.tasks import celery  # noqa
from flask_caching import  Cache

app = create_app(config=CurrentConfig)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
app.app_context().push()