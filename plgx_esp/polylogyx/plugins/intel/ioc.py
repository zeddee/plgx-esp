# -*- coding: utf-8 -*-
import logging

import sqlalchemy
from flask import current_app
from polylogyx.models import  ResultLogScan, PhishTank
from polylogyx.database import db
from .base import AbstractIntelPlugin


class IOCIntel(AbstractIntelPlugin):
    LEVEL_MAPPINGS = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warn': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL,
    }

    def __init__(self, config):
        self.name = 'ioc'

        levelname = config.get('level', 'debug')
        self.level = self.LEVEL_MAPPINGS.get(levelname, logging.DEBUG)

    def analyse_hash(self, value,type, node):
        # TODO(andrew-d): better message?
        current_app.logger.log(self.level, 'Triggered alert: ')

    def analyse_domain(self, value, type, node):
        # TODO(andrew-d): better message?
        current_app.logger.log(self.level, 'Triggered alert: ')

    def analyse_pending_hashes(self):
        scan_max = 4
        result_log_scans = ResultLogScan.query.filter(
            sqlalchemy.not_(ResultLogScan.reputations.has_key(self.name))).filter(
            ResultLogScan.scan_type.in_([ 'url'])).limit(scan_max).all()
        for result_log_scan_elem in result_log_scans:

            try:
                response = db.session.query(PhishTank).filter(PhishTank.url.ilike('%'+result_log_scan_elem.scan_value+'%')).first()
                newReputations = dict(result_log_scan_elem.reputations)
                if response:
                    newReputations[self.name + "_detected"] = True
                    newReputations[self.name ] = {}

                else:
                    newReputations[self.name + "_detected"] = False
                    newReputations[self.name ] = {}

                result_log_scan_elem.reputations = newReputations
                db.session.add(result_log_scan_elem)
            except Exception as e:
                current_app.logger.error(e)
        db.session.commit()


    def generate_alerts(self):
        try:
            source = self.name
            from polylogyx.models import ResultLogScan
            from polylogyx.database import db
            from polylogyx.utils import check_and_save_intel_alert

            result_log_scans = db.session.query(ResultLogScan).filter(
                ResultLogScan.reputations[source + "_detected"].astext.cast(sqlalchemy.Boolean).is_(True)).all()
            for result_log_scan in result_log_scans:
                check_and_save_intel_alert(scan_type=result_log_scan.scan_type, scan_value=result_log_scan.scan_value,
                                           data=result_log_scan.reputations[source],

                                           source=source,
                                           severity="LOW")
        except Exception as e:
            current_app.logger.error(e)

    def update_credentials(self):
        pass