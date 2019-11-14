# -*- coding: utf-8 -*-
import datetime as dt
import string

from flask import render_template, current_app

from polylogyx.models import  AlertEmail
from .base import AbstractAlerterPlugin


class EmailAlerter(AbstractAlerterPlugin):
    def __init__(self, config):
        self.config = config

    def handle_alert(self, node, match, intel_match):
        params = {}
        params.update(node)
        params.update(node.get('node_info', {}))
        server_url = self.setServerName()

        message_template = self.config.setdefault(
            'message_template', 'email/alert.body.txt'
        )

        if match:
            params.update(match.result['columns'])
            alert_id=match.alert_id
        elif intel_match:
            message_template='email/intel_alert.body.txt'
            params.update(intel_match.result)

            alert_id=intel_match.alert_id

        server_url=server_url.replace("9000","5000")



        body = string.Template(
            render_template(
                message_template,
                match=match,
                intel_match=intel_match,
                timestamp=dt.datetime.utcnow(),
                node=node,server_url=server_url
            )
        ).safe_substitute(**params)

        email_alert = AlertEmail(node_id=node['id'], alert_id=alert_id,
                                     body=body)
        email_alert.save(email_alert)
        return

    def setServerName(self):
        try:
            with open("resources/osquery.flags", "r") as fi:
                for ln in fi:
                    if ln.startswith("--tls_hostname="):
                        SERVER_URL = (ln[len('--tls_hostname='):]).replace('\r', '').replace('\n', '')
                        return SERVER_URL
        except Exception as e:
            return "localhost:9000"

