
# -*- coding: utf-8 -*-

from polylogyx.application import create_app
from polylogyx.settings import CurrentConfig
from polylogyx.tasks import celery  # noqa


app = create_app(config=CurrentConfig)

