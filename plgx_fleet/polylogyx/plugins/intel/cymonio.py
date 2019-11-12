# -*- coding: utf-8 -*-
import logging

from flask import current_app

from .base import AbstractIntelPlugin

from cymon import Cymon

class CymonIOIntel(AbstractIntelPlugin):
    LEVEL_MAPPINGS = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warn': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL,
    }

    def __init__(self, config):
        self.api = Cymon('')
        levelname = config.get('level', 'debug')
        self.level = self.LEVEL_MAPPINGS.get(levelname, logging.DEBUG)

    def analyse_hash(self, value,type, node):
        # TODO(andrew-d): better message?
        current_app.logger.log(self.level, 'Triggered alert: ')
    def analyse_domain(self, value,type, node):
        self.api.ip_events('185.27.134.165')

        # TODO(andrew-d): better message?
        current_app.logger.log(self.level, 'Triggered alert: ')