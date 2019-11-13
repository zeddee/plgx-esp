# # -*- coding: utf-8 -*-
# import logging
#
# from flask import current_app
#
# from .base import AbstractIntelPlugin
#
# from shadow_server_api import ShadowServerApi
# import json
#
# class ShadowServer(AbstractIntelPlugin):
#     LEVEL_MAPPINGS = {
#         'debug': logging.DEBUG,
#         'info': logging.INFO,
#         'warn': logging.WARNING,
#         'error': logging.ERROR,
#         'critical': logging.CRITICAL,
#     }
#
#     def __init__(self, config):
#         levelname = config.get('level', 'debug')
#
#
#         self.ss = ShadowServerApi()
#
#         self.level = self.LEVEL_MAPPINGS.get(levelname, logging.DEBUG)
#
#     def analyse_hash(self, value,type, node):
#         # TODO(andrew-d): better message?
#         response = self.ss.get_av('039ea049f6d0f36f55ec064b3b371c46')
#
#         current_app.logger.log(self.level, 'Triggered alert: ')
#     def analyse_domain(self, value,type, node):
#         # TODO(andrew-d): better message?
#         current_app.logger.log(self.level, 'Triggered alert: ')