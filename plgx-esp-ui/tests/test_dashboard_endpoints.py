"""
All Test-Case required client, url_prefix and token,
and these all we need to just pass as parameters in the function.
"""

import json

from polylogyx import db
from polylogyx.blueprints.v1.utils import fetch_alert_node_query_status, fetch_dashboard_data
from polylogyx.models import Settings
from tests.factories import SettingsFactory


class TestDashboardData:

    def test_get_dashboard_empty_data(self, client, url_prefix, token):
        """
        Test-case without existing dashboard data,
        expected output:- status is success, and
        resultant data of alert_data and distribution_and_status
        """
        resp = client.get(url_prefix + '/dashboard', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        alert_data = fetch_alert_node_query_status()
        distribution_and_status = fetch_dashboard_data()
        chart_data = {'alert_data': alert_data,"purge_duration":None, 'distribution_and_status': distribution_and_status}
        assert response_dict['data'] == chart_data

    def test_get_invalid_method(self, client, url_prefix, token):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.post(url_prefix + '/dashboard', headers={'x-access-token': token})
        assert resp.status_code == 405

    def test_get_dashboard_data(self, client, url_prefix, token, dashboard_data, alerts):
        """
        Test-case with existing dashboard data,
        expected output:- status is success, and
        resultant data of alert_data and distribution_and_status
        """
        SettingsFactory(
            name='purge_data_duration',
            setting='7'
        )
        db.session.commit()
        resp = client.get(url_prefix + '/dashboard', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        alert_data = fetch_alert_node_query_status()
        distribution_and_status = fetch_dashboard_data()
        chart_data={}
        chart_data['alert_data'] = alert_data
        chart_data['distribution_and_status'] = distribution_and_status
        chart_data['purge_duration'] = db.session.query(Settings).filter(Settings.name == 'purge_data_duration').first().setting
        assert response_dict['data'] == chart_data
        assert response_dict['data']['purge_duration'] == '7'
