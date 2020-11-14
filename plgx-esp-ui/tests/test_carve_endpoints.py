"""
All Test-Case required client, url_prefix and token,
and these all we need to just pass as parameters in the function.
"""

import json

from flask import send_file, current_app

from polylogyx import db
from polylogyx.dao import carves_dao
from .base import TestUtils
from .factories import DistributedQueryTaskFactory

test_utils_obj = TestUtils()


class TestNodeCarveList:
    """
   Test-case inside this block where these payloads are used,
   all are optional value and start and limit are of int type while
   host_identifier as of str type
   """

    payload = {'host_identifier': None, 'start': None, 'limit': None}

    def test_carves_without_existing_data_and_payload(self, client, url_prefix, token):
        """
        Test-case without payloads, and without exsiting carves_session and node data,
        expected output:- status is succes,
        count i.e., 0 and resultant data of carves i.e., empty list in this case
        """
        resp = client.post(url_prefix + '/carves', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 0
        assert response_dict['data']['results'] == []

    def test_carves_without_existing_data_and_empty_payload(self, client, url_prefix, token):
        """
        Test-case with payloads is empty dictionary,
        and without exsiting carves_session and node data,
        expected output:- status is succes,
        count i.e., 0 and resultant data of carves i.e., empty list in this case
        """
        resp = client.post(url_prefix + '/carves', headers={'x-access-token': token}, json={})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 0
        assert response_dict['data']['results'] == []

    def test_carves_without_existing_data_and_payload_val_none(self, client, url_prefix, token):
        """
        Test-case with payload values are none,
        and without exsiting carves_session and node data,
        expected output:- status is succes,
        count i.e., 0 and resultant data of carves i.e., empty list in this case
        """
        resp = client.post(url_prefix + '/carves', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 0
        assert response_dict['data']['results'] == []

    def test_carves_without_existing_data_and_with_invalid_host_identifier(self, client, url_prefix, token):
        """
        Test-case with invalid value of host_identifier of payloads,
        and without exsiting carves_session and node data,
        expected output:- status is failure,
        """
        self.payload['host_identifier'] = 'foo'
        resp = client.post(url_prefix + '/carves', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_carves_without_existing_data_and_with_valid_host_identifier(self, client, url_prefix, token):
        """
        Test-case with valid payloads value of host_identifier,
        and without exsiting carves_session and node data,
        expected output:- status is failure
        """
        self.payload['host_identifier'] = 'foobar'
        resp = client.post(url_prefix + '/carves', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_carves_invalid_method(self, client, url_prefix, token, carve_session):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.get(url_prefix + '/carves', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_carves_with_existing_data_and_without_payload(self, client, url_prefix, token, carve_session):
        """
        Test-case without payloads, and without exsiting carves_session and node data,
        expected output:- status is succes,
        count i.e., 1 and resultant data of carves in this case
        """
        resp = client.post(url_prefix + '/carves', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        carves = test_utils_obj.get_carve()
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['results'] == carves['results']

    def test_carves_with_existing_data_and_invalid_host_identifier(self, client, url_prefix, token, carve_session):
        """
        Test-case with invalid payloads value of host_identifier,
        and without exsiting carves_session and node data,
        expected output:- status is failure
        """
        self.payload['host_identifier']='foo'
        resp = client.post(url_prefix + '/carves', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_carves_with_existing_data_and_valid_payload(self, client, url_prefix, token, carve_session):
        """
        Test-case with valid payloads value of host_identifier,
        and without exsiting carves_session and node data,
        expected output:- status is succes,
        count i.e., 1 and resultant data of carves
        """
        self.payload['host_identifier']='foobar'
        resp = client.post(url_prefix + '/carves', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        carves = test_utils_obj.get_carves_with_host_identifier(self.payload['host_identifier'])
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['results'] == carves['results']

    def test_carves_with_existing_data_and_all_valid_payload(self, client, url_prefix, token, carve_session):
        """
        Test-case with all payloads value,
        and without exsiting carves_session and node data,
        expected output:- status is succes,
        count i.e., 1 and resultant data of carves
        """
        self.payload['host_identifier']='foobar'
        self.payload['start']=0
        self.payload['limit']=5
        resp = client.post(url_prefix + '/carves', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        carves = test_utils_obj.get_carves_with_host_identifier(self.payload['host_identifier'])
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['results'] == carves['results']


class TestDownloadCarves:

    def test_download_carves_with_valid_or_invalid_session_id(self, client, url_prefix, token):
        """
        Test-case without carve_session data,
        and session_id which is passing through url
        expected output:- status is failure
        """
        resp = client.get(url_prefix + '/carves/download/MQIAPXX285', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_download_carves_invalid_method(self, client, url_prefix, token):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.post(url_prefix + '/carves/download/MQIAPXX285', headers={'x-access-token': token})
        assert resp.status_code == 405

    def test_download_carves_with_with_valid_valid_session_id(self, client, url_prefix, token, carve_session):
        """
        Test-case with carve_session data, and
        valid session_id which is passing through url
        expected output:- status_code is 200, and
        a csv carves file data
        """
        resp = client.get(url_prefix + '/carves/download/foobar_session_id', headers={'x-access-token': token})
        assert resp.status_code == 200
        get_file = get_carves_file('foobar_session_id')
        assert resp.data == get_file.data

    def test_download_carves_with_with_valid_invalid_session_id(self, client, url_prefix, token, carve_session):
        """
        Test-case with carve_session data, and
        invalid session_id which is passing through url
        expected output:- status is failure
        """
        resp = client.get(url_prefix + '/carves/download/MQIAPXX567', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'


class TestDeleteCarve:

    """
    Test-case inside this block where this payload value is used,
    this value is compulsory value of str type,
    so if value is not passed or passed any other type than str,
    then it will return 400 i.e., bad request
    """

    payload = {'session_id': None}

    def test_delete_carves_without_payload(self, client, url_prefix, token):
        """
        Test-case without payload and without
        existing node and carve_session data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/carves/delete', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_delete_carves_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload is empty dictionary and without
        existing node and carve_session data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/carves/delete', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_delete_carves_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with payload value none and without
        existing node and carve_session data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/carves/delete', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_delete_carve_with_invalid_session_id(self, client, url_prefix, token):
        """
        Test-case with invalid session_id,
        and without exsisting carve_session and node data,
        expected output:- status is failure
        """
        self.payload['session_id'] = 'foobar'
        resp = client.post(url_prefix + '/carves/delete', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_delete_carve_with_valid_session_id(self, client, url_prefix, token):
        """
        Test-case with valid session-id,
        and without exsisting carve_session and node data,
        expected output:- status is failure
        """
        self.payload['session_id'] = 'foobar_session_id'
        resp = client.post(url_prefix + '/carves/delete', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_delete_carve_session_invalid_method(self, client, url_prefix, token, carve_session):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.get(url_prefix + '/carves/delete', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_delete_carves_with_invalid_session_id(self, client, url_prefix, token, carve_session):
        """
        Test-case with invalid session-id,
        and with existing carve_session data,
        expected output:- status is failure
        """
        self.payload['session_id'] = 'foobar'
        resp = client.post(url_prefix + '/carves/delete', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_delete_carves_with_valid_session_id(self, client, url_prefix, token, carve_session):
        """
        Test-case with valid session-id,
        and with existing carve_session and node data,
        expected output:- status is success
        """
        self.payload['session_id'] = 'foobar_session_id'
        resp = client.post(url_prefix + '/carves/delete', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'


class TestCarveSessionByPostQueryId:
    """
    Test-case inside this block where these payloads are used,
    all of the payloads values are compulsory value and query_id is of
    integer value and host_identifier is of str type,
    so if these values are none and other than specified type, then
    it will return 400 i.e., bad request
    """
    payload = {"query_id": None, "host_identifier": None}

    def test_carve_session_query_id_without_payload(self, client, url_prefix, token):
        """
        Test-case without payloads data and without existing carve_session data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/carves/query', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_carve_session_query_id_with_empty_payload(self, client, url_prefix, token):
        """
        Test-case empty payloads data and without existing carve_session data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/carves/query', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_carve_session_query_id_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case payloads value is None and without existing carve_session data,
        expected output:- status_code is 400
        """
        self.payload['query_id'] = None
        self.payload['host_identifier'] = None
        resp = client.post(url_prefix + '/carves/query', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_carve_session_with_only_payload_query_id(self, client, url_prefix, token):
        """
        Test-case only payloads value of query_id and without existing carve_session data,
        expected output:- status_code is 400
        """
        self.payload['query_id'] = 1
        self.payload['host_identifier'] = None
        resp = client.post(url_prefix + '/carves/query', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_carve_session_with_only_payload_host_identifier(self, client, url_prefix, token):
        """
        Test-case only payloads value of host_identifier and without existing carve_session data,
        expected output:- status_code is 400
        """
        self.payload['query_id'] = None
        self.payload['host_identifier'] = 'foobar'
        resp = client.post(url_prefix + '/carves/query', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_carve_session_query_id_with_empty_str_payload(self, client, url_prefix, token):
        """
        Test-case with empty str value of host_identifier and with valid
        query_id and without existing  carve_session data and if query-id value is any
        positive number and host-identifier value is any str value it
        gives same result if existing data is not present
        expected output:- status is failure
        """
        self.payload['query_id'] = 1
        self.payload['host_identifier'] = ''
        resp = client.post(url_prefix + '/carves/query', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_carve_session_query_id_invalid_method(self, client, url_prefix, token):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.get(url_prefix + '/carves/query', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_carve_session_query_id_with_valid_payload(self, client, url_prefix, token, carve_session, distributed_query_task):
        """
        Test-case with valid host_identifier and query_id,
        and with existing carve_session and distributed_query_task data,
        expected output:- status is failure
        """
        self.payload["host_identifier"] = "foobar"
        self.payload["query_id"] = 1
        resp = client.post(url_prefix + '/carves/query', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_carve_sessions_query_id_with_valid_payload(self, client, url_prefix, token, carve_session, distributed_query_task):
        """
        Test-case with valid host_identifier and query_id,
        and with existing carve_session and distributed_query_task data,
        expected output:- status is success, and
        resultant carves data
        """
        self.payload["host_identifier"] = "foobar"
        self.payload["query_id"] = 2
        DistributedQueryTaskFactory(
            save_results_in_db=True,
            distributed_query_id=2,
            guid='foobar_request_id',
            node_id=1
        )
        db.session.commit()

        resp = client.post(url_prefix + '/carves/query', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        carve_session = test_utils_obj.get_carve_session_by_query_id(2, 'foobar')
        assert response_dict['data'] == carve_session

    def test_carve_session_query_id_with_invalid_query_id(self, client, url_prefix, token, carve_session, distributed_query_task):
        """
        Test-case with valid host_identifier but invalid query_id
        and with existing carve_session and distributed_query_task data,
        expected output:- status is failure
        """
        self.payload["host_identifier"] = "foobar"
        self.payload["query_id"] = 20
        resp = client.post(url_prefix + '/carves/query', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_carve_session_query_id_with_invalid_host_identifier(self, client, url_prefix, token, carve_session, distributed_query_task):
        """
        Test-case with valid query_id but invalid host_identifier,
        nd with existing carve_session and distributed_query_task data,
        expected output:- status is failure
        """
        self.payload["host_identifier"] = "foo"
        self.payload["query_id"] = 1
        resp = client.post(url_prefix + '/carves/query', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'


def get_carves_file(session_id):
    carve_session = carves_dao.get_carves_by_session_id(session_id)
    if carve_session:
        data = send_file(
            current_app.config[
                'BASE_URL'] + '/carves/' + carve_session.node.host_identifier + '/' + carve_session.archive,
            as_attachment=True, mimetype='application/x-tar',
            attachment_filename='carve_session.tar'
        )
        data.direct_passthrough = False
        return data
