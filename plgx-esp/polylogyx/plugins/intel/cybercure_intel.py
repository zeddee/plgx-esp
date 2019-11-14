# -*- coding: utf-8 -*-
import logging

from flask import current_app

from polylogyx.utils import check_and_save_intel_alert
from .base import AbstractIntelPlugin

import cybercure

class CyberCureIntel(AbstractIntelPlugin):
    LEVEL_MAPPINGS = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warn': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL,
    }

    def __init__(self, config):
        levelname = config.get('level', 'debug')
        self.level = self.LEVEL_MAPPINGS.get(levelname, logging.DEBUG)

    def analyse_hash(self, value,type, node):
        # TODO(andrew-d): better message?
        current_app.logger.log(self.level, 'Triggered alert: ')
    def analyse_domain(self, value,type, node):
        response=cybercure.search('url')
        if 'exists' in response and response['exists']==True:
            check_and_save_intel_alert(scan_type=type, scan_value=value, data={}, source="cybercure",
                                       severity="LOW")

        # TODO(andrew-d): better message?
        current_app.logger.log(self.level, 'Triggered alert: ')