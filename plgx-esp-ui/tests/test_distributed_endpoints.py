"""
All Test-Case required client, url_prefix and token,
and these all we need to just pass as parameters in the function.
"""

import json
import datetime as dt
from .factories import NodeFactory


class TestDistributedQueryClass:
    """
        for all the test-case inside this block where payload are using,
        query value should be valid sql query,
        tags value may be single or multiple, if multiple tag value
        is passing then tag value should be separated by comma,
        nodes value are also single or multiple, if multiple node
        values are passing then node value should be comma separated,
        description value should be any string value, and
        query value is compulsory payload value of str type,
        so if compulsory value is not passed or passed any other value which
        is not matched with specified type then it will return 400 i.e., bad request
        """
    payload = {'query': None, 'tags': None, 'nodes': None, 'description': None}

    def test_distributed_query_without_payload(self, client, url_prefix, token):
        """
        Test-case without payload and without existing node data,
        expected output:- status code is 400
        """
        resp = client.post(url_prefix + '/distributed/add', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_distributed_query_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload is empry dictionary and without existing node data,
        expected output:- status code is 400
        """
        resp = client.post(url_prefix + '/distributed/add', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_distributed_query_with_none_payload_value(self, client, url_prefix, token):
        """
        Test-case with empty payloads and without existing node data,
        expected output:- status code is 400
        """
        self.payload['query'] = None
        resp = client.post(url_prefix + '/distributed/add', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_distributed_query_with_empty_value_payload(self, client, url_prefix, token):
        """
        Test-case with empty payloads and without existing node data,
        expected output:- status is failure
        """
        self.payload['query'] = ''
        self.payload['tags'] = ''
        self.payload['nodes'] = ''
        self.payload['description'] = ''
        resp = client.post(url_prefix + '/distributed/add', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_distributed_query_with_only_payload_value_query(self, client, url_prefix, token):
        """
        Test-case with payloads of only query value and without existing node data,
        expected output:- status is failure
        """
        payload = {'query': 'select * from system_info'}
        resp = client.post(url_prefix + '/distributed/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_distributed_query_with_all_payload_value(self, client, url_prefix, token):
        """
        Test-case with payloads of all values and without existing node data,
        expected output:- status is failure
        """
        self.payload['query'] = 'select * from system_info'
        self.payload['tags'] = 'demo'
        self.payload['nodes'] = '6357CE4F-5C62-4F4C-B2D6-CAC567BD6113,6357CE4F-5C62-4F4C-B2D6-CAGF12F17F23'
        self.payload['description'] = 'live query to get system_info'
        resp = client.post(url_prefix + '/distributed/add', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_distributed_query_with_multiple_tag(self, client, url_prefix, token):
        """
        Test-case with payloads of all values and without existing data,
        expected output:- status is failure
        """
        self.payload['query'] = 'select * from system_info'
        self.payload['tags'] = 'demo, test'
        self.payload['nodes'] = '6357CE4F-5C62-4F4C-B2D6-CAC567BD6113,6357CE4F-5C62-4F4C-B2D6-CAGF12F17F23'
        self.payload['description'] = 'live query to get system_info'
        resp = client.post(url_prefix + '/distributed/add', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_distributed_query_with_invalid_method(self, client, url_prefix, token, node):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.get(url_prefix + '/distributed/add', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_distributed_query_with_only_payloads_value_query(self, client, url_prefix, token, node):
        """
        Test-case of only payloads value of only query and with existing node data,
        expected output:- status is success
        query_id and count of online_nodes i.e, 3 in this case
        """
        payload = {'query': 'select * from system_info'}
        resp = client.post(url_prefix + '/distributed/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['query_id'] == 1
        assert response_dict['data']['onlineNodes'] == 1

    def test_distributed_query_with_all_payload(self, client, url_prefix, token, node):
        """"
        Test-case of payloads of all value and with existing node data,
        expected output:- status is success,
        query_id and count of online_nodes i.e, 1 in this case
        """
        self.payload['query'] = 'select * from system_info'
        self.payload['tags'] = 'demo'
        self.payload['nodes'] = '6357CE4F-5C62-4F4C-B2D6-CAC567BD6113,6357CE4F-5C62-4F4C-B2D6-CAGF12F17F23'
        self.payload['description'] = 'live query to get system_info'
        NodeFactory(
            host_identifier='6357CE4F-5C62-4F4C-B2D6-CAC567BD6113',
            last_checkin=dt.datetime.utcnow())
        resp = client.post(url_prefix + '/distributed/add', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['query_id'] == 1
        assert response_dict['data']['onlineNodes'] == 1

    def test_distributed_query_with_multiple_tag_value(self, client, url_prefix, token, node):
        """"
        Test-case of payloads of all value and with existing node data,
        expected output:- status is success,
        query_id and count of online_nodes i.e, 1 in this case
        """
        self.payload['query'] = 'select * from system_info'
        self.payload['tags'] = 'demo, test'
        self.payload['nodes'] = '6357CE4F-5C62-4F4C-B2D6-CAC567BD6113,6357CE4F-5C62-4F4C-B2D6-CAGF12F17F23'
        self.payload['description'] = 'live query to get system_info'
        NodeFactory(
            host_identifier='6357CE4F-5C62-4F4C-B2D6-CAC567BD6113',
            last_checkin=dt.datetime.utcnow())
        resp = client.post(url_prefix + '/distributed/add', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['query_id'] == 1
        assert response_dict['data']['onlineNodes'] == 1


class TestDistributedQueryTaskUpdate:

    """
    Test-case inside this block where this payload value is used,
    this is compulsory payload value of str type, so if value is not passsed
    or passed any other type than string then it will return 400 i.e., bad request
    """

    payload = {"guid": None}

    def test_distributed_query_task_without_payload(self, client, url_prefix, token):
        """
        Test-case without payloads and without
        existing DistributedQueryTask data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/distributed/querytaskupdate', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_distributed_query_task_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload is empty dictionary and without
        existing DistributedQueryTask data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/distributed/querytaskupdate', headers={'x-access-token': token},
                           json={})
        assert resp.status_code == 400

    def test_distributed_query_task_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with payload value is none and without
        existing DistributedQueryTask data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/distributed/querytaskupdate', headers={'x-access-token': token},
                           json=self.payload)
        assert resp.status_code == 400

    def test_distributed_query_task_with_payload_value_empty_str(self, client, url_prefix, token):
        """
        Test-case with payload value is str and without
        existing DistributedQueryTask data,
        expected output:- status is failure
        """
        self.payload['guid'] = ''
        resp = client.post(url_prefix + '/distributed/querytaskupdate', headers={'x-access-token': token},
                           json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_distributed_query_task_with_payload_value(self, client, url_prefix, token):
        """
        Test-case with payload value is str and without
        existing DistributedQueryTask data,
        expected output:- status is failure
        """
        self.payload['guid'] = '62d5510f-ae98-46c1-8bdc-f84abad3b4fa'
        resp = client.post(url_prefix + '/distributed/querytaskupdate', headers={'x-access-token': token},
                           json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_distributed_query_task_with_invalid_method(self, client, url_prefix, token, distributed_query_task):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        self.payload['guid'] = '62d5510f-ae98-46c1-8bdc-f84abad3b4fa'
        resp = client.get(url_prefix + '/distributed/querytaskupdate', headers={'x-access-token': token},
                           json=self.payload)
        assert resp.status_code == 405

    def test_distributed_query_task_with_invalid_guid_value(self, client, url_prefix, token, distributed_query_task):
        """
        Test-case with invalid guid value and with
        existing DistributedQuery, DistributedQueryTask and node data,
        expected output:- status is failure
        """
        self.payload['guid'] = 'foobar'
        resp = client.post(url_prefix + '/distributed/querytaskupdate', headers={'x-access-token': token},
                           json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'
        assert response_dict['message'] == 'Guid provided is invalid'

    def test_distributed_query_task_with_valid_guid_value(self, client, url_prefix, token, distributed_query_task):
        """
        Test-case with valid guid value and with
        existing DistributedQuery, DistributedQueryTask and node data,
        expected output:- status is success
        """
        self.payload['guid'] = 'foobar_guid'
        resp = client.post(url_prefix + '/distributed/querytaskupdate', headers={'x-access-token': token},
                           json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
