"""
All Test-Case required client, url_prefix and token,
and these all we need to just pass as parameters in the function.
"""


from polylogyx.dao.v1 import alerts_dao as dao
from polylogyx.wrappers.v1 import alert_wrappers as alert_wrapper
from polylogyx.blueprints.v1.utils import *

ALERT_RECON_QUERIES_JSON = {
    "scheduled_queries": [
        {
            "name": "win_file_events",
            "before_event_interval": 30,
            "after_event_interval": 60
        },
        {
            "name": "win_process_events",
            "before_event_interval": 30,
            "after_event_interval": 60
        }, {
            "name": "win_registry_events",
            "before_event_interval": 30,
            "after_event_interval": 60
        }, {
            "name": "win_socket_events",
            "before_event_interval": 30,
            "after_event_interval": 60
        }, {
            "name": "win_http_events",
            "before_event_interval": 30,
            "after_event_interval": 60
        }
    ],
    "live_queries": [
        {
            "name": "win_epp_table",
            "query": "select * from win_epp_table;"
        }
    ]
}


class TestAlertSourceCount:

    def test_alert_source_count_without_alerts_data(self,client, url_prefix, token):
        """
        test-case without existing alerts data,
        expected output:- status is success, and
        resultant data of alert_source with source_name and count
        """
        resp = client.get(url_prefix + '/alerts/count_by_source', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['alert_source'][0] == {'name': 'virustotal', 'count': 0}
        assert response_dict['data']['alert_source'][1] == {'name': 'rule', 'count': 0}
        assert response_dict['data']['alert_source'][2] == {'name': 'ibmxforce', 'count': 0}
        assert response_dict['data']['alert_source'][3] == {'name': 'alienvault', 'count': 0}
        assert response_dict['data']['alert_source'][4] == {'name': 'ioc', 'count': 0}

    def test_post_view_alerts_invalid_method(self, client, url_prefix, token):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.get(url_prefix + '/alerts', headers={'x-access-token': token})
        assert resp.status_code == 405

    def test_alert_source_count_with_alerts_data(self,client, url_prefix, token, alerts):
        """
        test-case with existing alerts data,
        expected output:- status is success, and
        resultant data of alert_source with source_name and count
        """
        resp = client.get(url_prefix + '/alerts/count_by_source', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['alert_source'][0] == {'name': 'virustotal', 'count': 1}
        assert response_dict['data']['alert_source'][1] == {'name': 'rule', 'count': 1}
        assert response_dict['data']['alert_source'][2] == {'name': 'ibmxforce', 'count': 0}
        assert response_dict['data']['alert_source'][3] == {'name': 'alienvault', 'count': 0}
        assert response_dict['data']['alert_source'][4] == {'name': 'ioc', 'count': 0}


class TestAlertsData:
    """
    Test-case inside this block where these payloads values are used
    these values are optional values and source and searchterm are of str type,
    start and limits are integer type, resolved value is
    of boolean type, and event_ids is of list type, start is 0,
    limit is 10 and searchterm is empty str, so if value type is
    not same as specified type then it will return 400 i.e., bad request
    """
    payload = {
        "start": None, "limit": None, "source": None,
        'resolved': None, 'event_ids': None, 'searchterm': ''
    }

    def test_alerts_data_without_payload(self, client, url_prefix, token):
        """
        Test-case without payload value and without existing alerts data,
        expected output:- status is failure, and resultant alert data is empty list in this case
        """
        resp = client.post(url_prefix + '/alerts', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'
        assert response_dict['data'] == []

    def test_alerts_data_with_payload_value_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload value is empty dictionary,
        and without existing alerts data,
        expected output:- status is failure, and
        resultant alert data is empty list in this case
        """
        resp = client.post(url_prefix + '/alerts', headers={'x-access-token': token}, json={})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'
        assert response_dict['data'] == []

    def test_alerts_data_with_payload_value_None(self, client, url_prefix, token):
        """
        Test-case with payload value None,
        and without existing alerts data,
        expected output:- status is failure, and
        resultant alert data is empty list in this case
        """
        resp = client.post(url_prefix + '/alerts', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'
        assert response_dict['data'] == []

    def test_alerts_data_with_only_source(self, client, url_prefix, token):
        """
        Test-case with only payload value of source,
        and without existing alerts data,
        expected output:- status is failure, and
        resultant alert data is empty list in this case
        """
        payload = {'source': 'rule'}
        resp = client.post(url_prefix + '/alerts', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'
        assert response_dict['data'] == []

    def test_alerts_data_with_only_resolved(self, client, url_prefix, token):
        """
        Test-case with only payload value of resolved,
        and without existing alerts data,
        expected output:- status is failure, and
        resultant alert data is empty list in this case
        """
        payload = {'resolved': True}
        resp = client.post(url_prefix + '/alerts', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'
        assert response_dict['data'] == []

    def test_alerts_data_with_only_event_ids(self, client, url_prefix, token):
        """
        Test-case with only payload value of event_ids,
        and without existing alerts data,
        expected output:- status is failure, and
        resultant alert data is empty list in this case
        """
        payload = {'event_ids': [1]}
        resp = client.post(url_prefix + '/alerts', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'
        assert response_dict['data'] == []

    def test_alerts_data_with_only_searchterm(self, client, url_prefix, token):
        """
        Test-case with only payload value of searchterm,
        and without existing alerts data,
        expected output:- status is failure, and
        resultant alert data is empty list in this case
        """
        payload = {'searchterm': 'testrule'}
        resp = client.post(url_prefix + '/alerts', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'
        assert response_dict['data'] == []

    def test_alerts_data_with_all_payload_value(self, client, url_prefix, token):
        """
        Test-case with all payload value,
        and without existing alerts data,
        expected output:- status is failure, and
        resultant alert data is empty list in this case
        Note:- results may vary based on date value
        """
        payload = {
            'start':0, 'limit': 3, 'source': 'rule', 'resolved': False,
            'event_ids': [1], 'searchterm': 'testrule'
        }
        resp = client.post(url_prefix + '/alerts', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'
        assert response_dict['data'] == []

    def test_alerts_data_with_all_payload_value_with_invalid_pagination(self, client, url_prefix, token):
        """
        Test-case with all payload value with invalid pagination,
        and without existing alerts data,
        expected output:- status_code is 400
        """
        payload = {
            'start':'str', 'limit': 'foo', 'source': 'rule', 'resolved': False,
            'event_ids': [1], 'searchterm': 'testrule'
        }
        resp = client.post(url_prefix + '/alerts', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 400

    def test_alerts_data_with_all_payload_value_with_start_value_none(self, client, url_prefix, token):
        """
        Test-case with all payload value with start value none,
        and without existing alerts data,
        expected output:- status_code is 400
        """
        payload = {
            'start':None, 'limit': 'foo', 'source': 'rule', 'resolved': False,
            'event_ids': [1], 'searchterm': 'testrule'
        }
        resp = client.post(url_prefix + '/alerts', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 400

    def test_alerts_data_with_all_payload_value_with_limit_value_none(self, client, url_prefix, token):
        """
        Test-case with all payload value with limit value none,
        and without existing alerts data,
        expected output:- status is failure, and response_data should be empty list
        """
        payload = {
            'start':1, 'limit': None, 'source': 'rule', 'resolved': False,
            'event_ids': [1], 'searchterm': 'testrule'
        }
        resp = client.post(url_prefix + '/alerts', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'
        assert response_dict['data'] == []

    def test_alerts_data_invalid_method(self, client, url_prefix, token, alerts):
        """
         Test-case with invalid request method,
         expected output:- status code is 405
        """
        resp = client.get(url_prefix + '/alerts', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 405

    def test_alert_data_without_payload(self, client, url_prefix, token, alerts):
        """
        Test-case without payload value and with existing alerts data,
        expected output:- status is failure, and resultant alert data is empty list in this case
        """
        resp = client.post(url_prefix + '/alerts', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'
        assert response_dict['data'] == []

    def test_alert_data_with_payload_value_empty_dict(self, client, url_prefix, token, alerts):
        """
        Test-case with payload value is empty dictionary,
        and with existing alerts data,
        expected output:- status is failure, and
        resultant alert data is empty list in this case
        """
        resp = client.post(url_prefix + '/alerts', headers={'x-access-token': token}, json={})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'
        assert response_dict['data'] == []

    def test_alert_data_with_payload_value_None(self, client, url_prefix, token, alerts):
        """
        Test-case with payload value None,
        and with existing alerts data,
        expected output:- status is failure, and
        resultant alert data is empty list in this case
        """
        resp = client.post(url_prefix + '/alerts', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'
        assert response_dict['data'] == []

    def test_alert_data_with_only_source(self, client, url_prefix, token, alerts):
        """
        Test-case with only payload value of source,
        and with existing alerts data,
        expected output:- status is success, and
        resultant alert data like count, total_count, hostname etc.
        """
        payload = {'source': 'rule'}
        resp = client.post(url_prefix + '/alerts', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        data = get_results_by_alert_source(0, 10, 'rule')
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        assert response_dict['data']['results'] == data['results']

    def test_alert_data_with_only_resolved(self, client, url_prefix, token, alerts):
        """
        Test-case with only payload value of resolved,
        and with existing alerts data,
        expected output:- status is failure, and
        resultant alert data is empty list in this case
        """
        payload = {'resolved': True}
        resp = client.post(url_prefix + '/alerts', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'
        assert response_dict['data'] == []

    def test_alert_data_with_only_event_ids(self, client, url_prefix, token, alerts):
        """
        Test-case with only payload value of event_ids,
        and with existing alerts data,
        expected output:- status is failure, and
        resultant alert data is empty list in this case
        """
        payload = {'event_ids': [1]}
        resp = client.post(url_prefix + '/alerts', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'
        assert response_dict['data'] == []

    def test_alert_data_with_only_searchterm(self, client, url_prefix, token, alerts):
        """
        Test-case with only payload value of searchterm,
        and with existing alerts data,
        expected output:- status is failure, and
        resultant alert data is empty list in this case
        """
        payload = {'searchterm': 'testrule'}
        resp = client.post(url_prefix + '/alerts', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'
        assert response_dict['data'] == []

    def test_alert_data_with_all_payload_value(self, client, url_prefix, token, alerts):
        """
        Test-case with all payload value,
        and with existing alerts data,
        expected output:- status is success, and
        resultant alert data like count, total_count, hostname etc.
        Note:- results may vary based on date value
        """
        payload = {
            'start':0, 'limit': 3, 'source': 'rule', 'resolved': False,
            'event_ids': [1, 2], 'searchter': 'testrule'
        }
        resp = client.post(url_prefix + '/alerts', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        data = get_results_by_alert_source(0, 10, 'rule')
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        assert response_dict['data']['results'] == data['results']

    def test_alert_data_with_all_payload_value_with_invalid_source(self, client, url_prefix, token, alerts):
        """
        Test-case with all payload value with invalid source,
        and with existing alerts data,
        expected output:- status is failure, and
        resultant alert is empty list in this case
        """
        payload = {
            'start':0, 'limit': 3, 'source': 'test', 'resolved': False,
            'event_ids': [1, 2], 'searchter': 'testrule'
        }
        resp = client.post(url_prefix + '/alerts', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_alert_data_with_all_payload_value_with_invalid_pagination(self, client, url_prefix, token, alerts):
        """
        Test-case with all payload value with invalid pagination,
        and with existing alerts data,
        expected output:- status_code is 400
        """
        payload = {
            'start':'str', 'limit': 'foo', 'source': 'rule', 'resolved': False,
            'event_ids': [1], 'searchterm': 'testrule'
        }
        resp = client.post(url_prefix + '/alerts', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 400

    def test_alert_data_with_all_payload_value_with_start_value_none(self, client, url_prefix, token, alerts):
        """
        Test-case with all payload value with start value none,
        and with existing alerts data,
        expected output:- status_code is 400
        """
        payload = {
            'start':None, 'limit': 'foo', 'source': 'rule', 'resolved': False,
            'event_ids': [1], 'searchterm': 'testrule'
        }
        resp = client.post(url_prefix + '/alerts', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 400

    def test_alert_data_with_all_payload_value_with_limit_value_none(self, client, url_prefix, token, alerts):
        """
        Test-case with all payload value with limit value none,
        and with existing alerts data,
        expected output:- status is failure, and response_data should be empty list
        """
        payload = {
            'start':0, 'limit': None, 'source': 'rule', 'resolved': False,
            'event_ids': [1], 'searchterm': 'testrule'
        }
        resp = client.post(url_prefix + '/alerts', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'
        assert response_dict['data'] == []


class TestGetAlertInvestigateData:

    def test_get_alert_investigate_data_without_existing_alerts(self, client, url_prefix, token):
        """
        Test-case without alerts data,
        alert_id which is passing through url
        expected output:- status is failure
        """
        resp = client.get(url_prefix + '/alerts/1', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_invalid_method(self, client, url_prefix, token):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.post(url_prefix + '/alerts/1', headers={'x-access-token': token})
        assert resp.status_code == 405

    def test_get_alert_investigate_data_with_invalid_alert_id(self, client, url_prefix, token, alerts):
        """
        Test-case with alerts data and invalid
        alert_id which is passing through url,
        expected output:- status is failure
        """
        resp = client.get(url_prefix + '/alerts/5', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_alert_investigate_data_with_existing_alerts(self, client, url_prefix, token, alerts):
        """
        Test-case with alerts data and valid
        alert_id which is passing through url,
        expected output:- status is success, and
        resultant alerts data
        """
        resp = client.get(url_prefix + '/alerts/1', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        alert = dao.get_alert_by_id(1)
        assert response_dict['data'] == alerts_details(alert)


class TestUpdateAlertInvestigateData:

    """
    Test-case inside this block where this payload value is used,
    this is optional value of payload and of boolean type,
    so if value type is other than boolean then it will return
    400 error, i.e., bad request
    """
    payload = {'resolve': None}

    def test_update_alert_investigate_data_without_payload(self, client, url_prefix, token):
        """
        Test-case without payload value and without alerts data,
        alert_id which is passing through url
        expected output:- status is failure
        """
        resp = client.put(url_prefix + '/alerts/1', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_update_alert_investigate_data_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload value is empty dictionary, and without alerts data,
        alert_id which is passing through url
        expected output:- status is failure
        """
        resp = client.put(url_prefix + '/alerts/1', headers={'x-access-token': token}, json={})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_update_alert_investigate_data_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with payload value is none, and without alerts data,
        alert_id which is passing through url
        expected output:- status is failure
        """
        resp = client.put(url_prefix + '/alerts/1', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_update_alert_investigate_data_with_resolve_value_of_payload(self, client, url_prefix, token):
        """
        Test-case with payload value is True/False, and without alerts data,
        alert_id which is passing through url
        expected output:- status is failure
        """
        self.payload['resolve'] = True
        resp = client.put(url_prefix + '/alerts/1', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_update_alert_investigate_invalid_method(self, client, url_prefix, token):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.post(url_prefix + '/alerts/1', headers={'x-access-token': token})
        assert resp.status_code == 405

    def test_get_alert_investigate_data_with_invalid_alert_id(self, client, url_prefix, token, alerts):
        """
        Test-case with alerts data and invalid
        alert_id which is passing through url, with payload value of true/false
        expected output:- status is failure
        """
        self.payload['resolve'] = False
        resp = client.put(url_prefix + '/alerts/5', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_alert_investigate_data_with_valid_id_resolve_false(self, client, url_prefix, token, alerts):
        """
        Test-case with alerts data and valid
        alert_id which is passing through url, and with payload value is False
        expected output:- status is success
        """
        self.payload['resolve'] = False
        resp = client.get(url_prefix + '/alerts/1', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        alert = alerts_dao.get_alerts_by_alert_id(1)
        assert alert.status == 'OPEN'

    def test_get_alert_investigate_data_with_valid_id_resolve_true(self, client, url_prefix, token, alerts):
        """
        Test-case with alerts data and valid
        alert_id which is passing through url, and with payload value is True
        expected output:- status is success
        """
        self.payload['resolve'] = True
        resp = client.put(url_prefix + '/alerts/1', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        alert = alerts_dao.get_alerts_by_alert_id(1)
        assert alert.status == 'RESOLVED'


class TestExportCsvAlerts:

    """
    Test-case inside this block where this payload value is used,
    this is compulsory payload value of str type, so if value is not passed
    or type of value other than str then it will return 400 i.e., bad request
    """

    payload = {'source': None}

    def test_export_csv_alerts_without_payload(self, client, url_prefix, token):
        """
        Test-case without payloads and without existing alerts data
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/alerts/alert_source/export', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_export_csv_alerts_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload value is empty dict and without existing alerts data
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/alerts/alert_source/export', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_export_csv_alerts_with_payload_val_none(self, client, url_prefix, token):
        """
        Test-case with payload value none and without existing alerts data
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/alerts/alert_source/export', headers={'x-access-token': token},
                           json=self.payload)
        assert resp.status_code == 400

    def test_export_csv_alerts_with_valid_payload_value(self, client, url_prefix, token):
        """
        Test-case with valid payload value and without existing alerts data
        expected output:- status is failure
        """
        self.payload['source'] = 'rule'
        resp = client.post(url_prefix + '/alerts/alert_source/export', headers={'x-access-token': token},
                           json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == "failure"

    def test_export_csv_invalid_method(self, client, url_prefix, token):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.get(url_prefix + '/alerts/alert_source/export', headers={'x-access-token': token},
                           data={'source': 'rule'})
        assert resp.status_code == 405

    def test_export_csv_alerts_with_invalid_source(self, client, url_prefix, token, alerts):
        """
        Test-case with invalid source name of payload value,
        and with existing alerts data,
        expected output:- status is failure
        """
        self.payload['source'] = 'test'
        resp = client.post(url_prefix + '/alerts/alert_source/export', headers={'x-access-token': token},
                           json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_export_csv_alerts_with_valid_source(self, client, url_prefix, token, alerts):
        """
        Test-case with valid source name of payload value,
        and with existing alerts data,
        expected output:- status_code is 200, and
        a csv file data
        """
        self.payload['source'] = 'rule'
        resp = client.post(url_prefix + '/alerts/alert_source/export', headers={'x-access-token': token},
                           json=self.payload)
        assert resp.status_code == 200
        assert resp.data == get_response(alerts_dao.get_alert_source('rule')).data
