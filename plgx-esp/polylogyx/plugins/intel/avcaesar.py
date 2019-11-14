# -*- coding: utf-8 -*-
import logging

from flask import current_app

from .base import AbstractIntelPlugin

import avcaesar_api
class AVCaesarIntel(AbstractIntelPlugin):
    LEVEL_MAPPINGS = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warn': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL,
    }

    def __init__(self, config):
        api = avcaesar_api.Connector(key='', **avcaesar_api.config_malware_lu)

        levelname = config.get('level', 'debug')
        self.level = self.LEVEL_MAPPINGS.get(levelname, logging.DEBUG)

    def analyse_hash(self, value,type, node):
        # TODO(andrew-d): better message?
        current_app.logger.log(self.level, 'Triggered alert: ')
    def analyse_domain(self, value,type, node):
        # TODO(andrew-d): better message?
        current_app.logger.log(self.level, 'Triggered alert: ')