"""
All Test-Case required client, url_prefix and token,
and these all we need to just pass as parameters in the function.
"""

import os
from polylogyx.blueprints.v1.common import hunt_through_indicators
from polylogyx.blueprints.v1.utils import *
from polylogyx.constants import PolyLogyxServerDefaults
from polylogyx.dao.v1 import common_dao
from .factories import OptionsFactory

from .base import TestUtils

test_utils_obj = TestUtils()
search_rules = SearchParser()

conditions = {
  		"condition": "OR",
  		"rules": [
    			{
      			"id": "name",
      			"field": "name",
      			"type": "string",
      			"input": "text",
      			"operator": "contains",
      			"value": "foobar"
    			},
    			{
      			"id": "name",
      			"field": "name",
      			"type": "string",
      			"input": "text",
      			"operator": "equal",
      			"value": "foobar1"
    			}
  			],
  		"valid": True
}


class TestHuntFileUpload:
    """
    Test-case inside this block where these payloads are used,
    out of all payloads file and type are compulsory payloads value,
    and remaining all are optional, so if compulsory value not passed or
    passed any other values type, then it will return 400 i.e., bad request
    """
    fp = 'tests/eicar.com.txt'
    files = {'file': open(fp, 'rb')}
    payload = {
        'file': '', 'type': '', 'host_identifier': '', 'query_name': '', 'start': None, 'limit': None
    }

    def test_hunt_file_upload_without_payload(self, client, url_prefix, token):
        """
        Test-case without payload and without existing result_log and node data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/hunt-upload', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_with_empty_payload(self, client, url_prefix, token):
        """
        Test-case with empty dict of payload and without existing result_log and node data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/hunt-upload', headers={'x-access-token': token}, data={})
        assert resp.status_code == 400

    def test_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with none value of payload and without existing result_log and node data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/hunt-upload', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 400

    def test_with_payload_value_empty_str(self, client, url_prefix, token):
        """
        Test-case with file and type value is empty of payload
        and without existing result_log and node data,
        expected output:- status_code is 400
        """
        self.payload['file'] = ''
        self.payload['type'] = ''
        resp = client.post(url_prefix + '/hunt-upload', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 400

    def test_with_compulsory_value_of_payload(self, client, url_prefix, token):
        """
        Test-case with compulsory value of payloads of upload file and type,
        and without existing result_log and node data,
        expected output:- status is success,
        and resultant_data is empty list in this case
        """
        payload = {'file': self.files, 'type': 'md5'}
        resp = client.post(url_prefix + '/hunt-upload', headers={'x-access-token': token}, data=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == []

    def test_with_compulsory_payload_value_and_host_identifier(self, client, url_prefix, token):
        """
        Test-case with compulsory value of payload and host-identifier but no query-name,
        and without existing result_log and node data,
        expected output:- status is failure
        """
        payload = {}
        payload['host_identifier'] = 'foobar'
        payload['type'] = 'md5'
        payload['file'] = {'file': open(self.fp, 'rb')}
        resp = client.post(url_prefix + '/hunt-upload', headers={'x-access-token': token}, data=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_with_compulsory_payload_value_and_query_name(self, client, url_prefix, token):
        """
        Test-case with compulsory value of payload and query-name but no host-identifier ,
        and without existing result_log and node data,
        expected output:- status is success,
        and resultant_data is empty list in this case
        """
        payload = {}
        payload['query_name'] = 'kernel_modules'
        payload['type'] = 'md5'
        payload['file'] = {'file': open(self.fp, 'rb')}
        resp = client.post(url_prefix + '/hunt-upload', headers={'x-access-token': token}, data=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == []

    def test_with_all_value_of_payloads_except_pagination(self, client, url_prefix, token):
        """
        Test-case with paylods of upload file, type, host-identifier and query-name,
        and without existing result_log and node data,
        expected output:- status is success,
        and resultant_data is empty list in this case
        """
        payload = {}
        payload['query_name'] = 'kernel_modules'
        payload['type'] = 'md5'
        payload['host-identifier'] = 'foobar'
        payload['file'] = {'file': open(self.fp, 'rb')}
        resp = client.post(url_prefix + '/hunt-upload', headers={'x-access-token': token}, data=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == []

    def test_with_all_value_payloads_with_invalid_pagination(self, client, url_prefix, token):
        """
        Test-case with paylods of upload file, type, host-identifier, query-name, start and limit,
        and without existing result_log and node data,
        expected output:- status_code is 400
        """
        self.payload['query_name'] = 'kernel_modules'
        self.payload['host-identifier'] = 'foobar1'
        self.payload['type'] = 'md5'
        self.payload['start'] = -2
        self.payload['limit'] = 4.5
        self.payload['file'] = {'file': open(self.fp, 'rb')}
        resp = client.post(url_prefix + '/hunt-upload', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 400

    def test_with_all_value_payloads_with_valid_pagination(self, client, url_prefix, token):
        """
        Test-case with paylods of upload file, type, host-identifier, query-name, start and limit,
        and without existing result_log and node data,
        expected output:- status is success,
        and resultant_data is empty list in this case
        """
        self.payload['query_name'] = 'kernel_modules'
        self.payload['host-identifier'] = 'foobar1'
        self.payload['type'] = 'md5'
        self.payload['start'] = 0
        self.payload['limit'] = 3
        self.payload['file'] = {'file': open(self.fp, 'rb')}
        resp = client.post(url_prefix + '/hunt-upload', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == []

    def test_with_invalid_method(self, client, url_prefix, token):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        self.payload['file'] = {'file': open(self.fp, 'rb')}
        self.payload['type'] = 'md5'
        resp = client.get(url_prefix + '/hunt-upload', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 405

    def test_data_with_only_compulsory_payload_value(self, client, url_prefix, token, result_log):
        """
        Test-case with existing result_log and node data,
        and file-upload and type but no host-identifier,
        no query-name, no start and limit value,
        expected output:- status is success,
        count i.e., 2 in this case and resultant data
        """
        payload = {}
        payload['file'] = {'file': open(self.fp, 'rb')}
        payload['type'] = 'md5'
        resp = client.post(url_prefix + '/hunt-upload', headers={'x-access-token': token}, data=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        file = open(self.fp, 'rb')
        lines = [line.decode('utf-8').replace('\n', '') for line in file.readlines()]
        data = hunt_through_indicators(lines, 'md5', None, None, 0, 100)
        assert response_dict['data'][0]['queries'][0]['count'] == 2
        assert response_dict['data'][0]['queries'][0]['query_name'] == 'kernel_modules'
        assert response_dict['data'][0] == data[2][0]

    def test_data_with_compulsory_value_and_host_identifier(self, client, url_prefix, token, result_log):
        """
        Test-case with existing result_log and node data,
        and file-upload, type and host-identifier,
        but no query-name, start and limit value,
        expected output:- status is failure
        """
        payload = {}
        payload['host_identifier'] = 'foobar'
        payload['file'] = {'file': open(self.fp, 'rb')}
        payload['type'] = 'md5'
        resp = client.post(url_prefix + '/hunt-upload', headers={'x-access-token': token}, data=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_data_with_compulsory_value_and_query_name(self, client, url_prefix, token, result_log):
        """
        Test-case with existing result_log and node data,
        and file-upload, type and host-identifier,
        but no query-name, start and limit value,
        expected output:- status is success,
        count i.e., 2 in this case and resultant data
        """
        payload = {}
        payload['file'] = {'file': open(self.fp, 'rb')}
        payload['type'] = 'md5'
        payload['query_name'] = 'kernel_modules'
        resp = client.post(url_prefix + '/hunt-upload', headers={'x-access-token': token}, data=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == "success"
        file = open(self.fp, 'rb')
        lines = [line.decode('utf-8').replace('\n', '') for line in file.readlines()]
        data = hunt_through_indicators(lines, 'md5', None, 'kernel_modules', 0, 100)
        assert response_dict['data'][0]['queries'][0]['count'] == 2
        assert response_dict['data'][0]['queries'][0]['query_name'] == 'kernel_modules'
        assert response_dict['data'][0] == data[2][0]

    def test_data_with_all_compulsory_value_except_pagination(self, client, url_prefix, token, result_log):
        """
        Test-case with existing result_log and node data,
        and all payload value except start and limit value,
        expected output:- status is success,
        count i.e., 2 in this case and resultant data
        """
        self.payload['host_identifier'] = 'foobar'
        self.payload['file'] = {'file': open(self.fp, 'rb')}
        self.payload['type'] = 'md5'
        self.payload['query_name'] = 'kernel_modules'
        resp = client.post(url_prefix + '/hunt-upload', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == "success"
        file = open(self.fp, 'rb')
        lines = [line.decode('utf-8').replace('\n', '') for line in file.readlines()]
        data = hunt_through_indicators(lines, 'md5',  'foobar', 'kernel_modules', 0, 100)
        assert response_dict['data']['count']== 2
        assert response_dict['data']['results']== data[2]['results']

    def test_data_with_all_compulsory_value_with_pagination(self, client, url_prefix, token, result_log):
        """
        Test-case with existing result_log and node data and all payload value,
        expected output:- status is success,
        count i.e., 2 in this case and resultant data
        """
        self.payload['host_identifier'] = 'foobar'
        self.payload['type'] = 'md5'
        self.payload['file'] = {'file': open(self.fp, 'rb')}
        self.payload['query_name'] = 'kernel_modules'
        self.payload['start'] = 0
        self.payload['limit'] = 10
        resp = client.post(url_prefix + '/hunt-upload', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == "success"
        file = open(self.fp, 'rb')
        lines = [line.decode('utf-8').replace('\n', '') for line in file.readlines()]
        data = hunt_through_indicators(lines, 'md5',  'foobar', 'kernel_modules', 0, 10)
        assert response_dict['data']['count'] == 2
        assert response_dict['data']['results'] == data[2]['results']

    def test_data_with_all_compulsory_value_with_invalid_pagination(self, client, url_prefix, token, result_log):
        """
        Test-case with existing result_log and node data, and
        all payload value with invalid pagination,
        expected output:- status_code is 200,
        and status is failure
        """
        self.payload['host_identifier'] = 'foobar'
        self.payload['type'] = 'md5'
        self.payload['file'] = {'file': open(self.fp, 'rb')}
        self.payload['query_name'] = 'kernel_modules'
        self.payload['start'] = -2
        self.payload['limit'] = -1
        resp = client.post(url_prefix + '/hunt-upload', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'


class TestIndicatorHunt:

    """
    Test-case inside this block where these payloads are used,
    out of all payloads only indicators and type are compulsory value,
    remainings are optional so if compulsory values are not passed,
    passed any wrong value type then it will return 400 i.e., bad request
    """
    payload = {
        'indicators': '', 'type': '', 'host_identifier': '',
        'query_name': '', 'start': None, 'limit': None
    }

    def test_indicator_hunt_without_payload(self, client, url_prefix, token):
        """
        Test-case without payloads and without existing result_log and node data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/indicators/hunt', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_indicator_hunt_with_empty_payload(self, client, url_prefix, token):
        """
        Test-case with empty payload and without existing result_log and node data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/indicators/hunt', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_indicator_hunt_with_compulsory_payload_value(self, client, url_prefix, token):
        """
        Test-case with payload of indicators and type but no host_identifier
        and no query-name and without existing result_log and node data,
        expected output:- status is success,
        and resultant data is empty list in this case
        """
        payload = {}
        payload['indicators'] = 'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
        payload['type'] = 'md5'
        resp = client.post(url_prefix + '/indicators/hunt', headers={'x-access-token': token},
                           json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == []

    def test_indicator_hunt_with_compulsory_payload_and_host_identifier(self, client, url_prefix, token):
        """
        Test-case with payload of indicators, type and host-identifier
        but no query-name and without existing result_log and node data,
        expected output:- status is failure
        """
        payload = {}
        payload['indicators'] = 'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
        payload['type'] = 'md5'
        payload['host_identifier'] = 'foobar'
        resp = client.post(url_prefix + '/indicators/hunt', headers={'x-access-token': token},
                           data=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_indicator_hunt_with_compulsory_payload_value_and_query_name(self, client, url_prefix, token):
        """
        Test-case with payload of indicators and type but no host_identifier
        and no query-name and without existing result_log and node data,
        expected output:- status is success,
        and resultant data is empty list in this case
        """
        self.payload['indicators'] = 'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
        self.payload['type'] = 'md5'
        self.payload['host_identifier'] = ''
        self.payload['query_name'] = 'kernel_modules'
        resp = client.post(url_prefix + '/indicators/hunt', headers={'x-access-token': token},
                           data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == []

    def test_indicator_hunt_with_all_payload_value_except_pagination(self, client, url_prefix, token):
        """
        Test-case with payload of indicators, type, host_identifier
        and query-name and without existing result_log and node data,
        expected output:- status is failure

        """
        self.payload['indicators'] = 'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
        self.payload['type'] = 'md5'
        self.payload['host_identifier'] = 'foobar'
        self.payload['query_name'] = 'kernel_modules'
        resp = client.post(url_prefix + '/indicators/hunt', headers={'x-access-token': token},
                           data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_indicator_hunt_with_all_payload_value_with_pagination(self, client, url_prefix, token):
        """
        Test-case with payload of indicators, type, host_identifier
        and query-name and without existing result_log and node data,
        expected output:- status is failure
        """
        self.payload['indicators'] = 'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
        self.payload['type'] = 'md5'
        self.payload['host_identifier'] = 'foobar'
        self.payload['query_name'] = 'kernel_modules'
        self.payload['start'] = 0
        self.payload['limit'] = 10
        resp = client.post(url_prefix + '/indicators/hunt', headers={'x-access-token': token},
                           data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_indicator_hunt_with_all_payload_value_with_invalid_pagination(self, client, url_prefix, token):
        """
        Test-case with payload of indicators, type, host_identifier and
        query-name and without existing result_log and node data also with invalid pagination,
        expected output:- status is failure
        """
        self.payload['indicators'] = 'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
        self.payload['type'] = 'md5'
        self.payload['host_identifier'] = 'foobar'
        self.payload['query_name'] = 'kernel_modules'
        self.payload['start'] = -3
        self.payload['limit'] = -5
        resp = client.post(url_prefix + '/indicators/hunt', headers={'x-access-token': token},
                           data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_indicator_hunt_with_payload_value_empty_str(self, client, url_prefix, token):
        """
        Test-case with empty payload and without existing result_log and node data,
        expected output:- status_code is 400
        """
        self.payload['indicators'] = ''
        self.payload['type'] = ''
        self.payload['host_identifier'] = ''
        self.payload['query_name'] = ''
        self.payload['start'] = None
        self.payload['limit'] = None
        resp = client.post(url_prefix + '/indicators/hunt', headers={'x-access-token': token}, data={})
        assert resp.status_code == 400

    def test_indicator_hunt_with_invalid_method(self, client, url_prefix, token, result_log):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.get(url_prefix + '/indicators/hunt', headers={'x-access-token': token},
                           data=self.payload)
        assert resp.status_code == 405

    def test_indicator_hunt_with_only_compulsory_value(self, client, url_prefix, token, result_log):
        """
        Test-case only indicators and type but no host-identifier
        and no query-name and with existing result_log and node data,
        expected output:- status is success,
        and resultant data is like hostname, host_identifier, query_name and count
        """
        self.payload['indicators'] = 'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
        self.payload['type'] = 'md5'
        self.payload['host_identifier'] = ''
        self.payload['query_name'] = ''
        self.payload['start'] = None
        self.payload['limit'] = None
        resp = client.post(url_prefix + '/indicators/hunt', headers={'x-access-token': token},
                           data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'][0]['hostname'] == 'foobar'
        assert response_dict['data'][0]['host_identifier'] == 'foobar'
        assert response_dict['data'][0]['queries'][0]['query_name'] == 'kernel_modules'
        assert response_dict['data'][0]['queries'][0]['count'] == 2

    def test_indicator_hunt_with_compulsory_value_and_host_identifier(self, client, url_prefix, token, result_log):
        """
        Test-case with indicators, type and host-identifier
        but no query-name and with existing result_log and node data,
        expected output:- status is failure
        """
        self.payload['indicators'] = 'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
        self.payload['type'] = 'md5'
        self.payload['host_identifier'] = 'foobar'
        self.payload['query_name'] = ''
        self.payload['start'] = None
        self.payload['limit'] = None
        resp = client.post(url_prefix + '/indicators/hunt', headers={'x-access-token': token},
                           data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_indicator_hunt_compulsory_payload_value_and_query_name(self, client, url_prefix, token, result_log):
        """
        Test-case with payload of indicators, type and query-name
        but no host_identifier and without existing result_log and node data,
        expected output:- status is success,
        and resultant data is like hostname, host_identifier, query_name and count
        """
        self.payload['indicators'] = 'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
        self.payload['type'] = 'md5'
        self.payload['host_identifier'] = ''
        self.payload['query_name'] = 'kernel_modules'
        resp = client.post(url_prefix + '/indicators/hunt', headers={'x-access-token': token},
                           data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'][0]['hostname'] == 'foobar'
        assert response_dict['data'][0]['host_identifier'] == 'foobar'
        assert response_dict['data'][0]['queries'][0]['query_name'] == 'kernel_modules'
        assert response_dict['data'][0]['queries'][0]['count'] == 2

    def test_indicator_hunt_all_payload_value_except_pagination(self, client, url_prefix, token, result_log):
        """
        Test-case with indicators, type, host-identifier,
        query-name and without pagination and with existing result_log and node data,
        expected output:- status is success,
        and resultant data is like hostname, host_identifier, query_name and count
        """
        self.payload['indicators'] = 'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
        self.payload['type'] = 'md5'
        self.payload['host_identifier'] = 'foobar'
        self.payload['query_name'] = 'kernel_modules'
        self.payload['start'] = None
        self.payload['limit'] = None
        resp = client.post(url_prefix + '/indicators/hunt', headers={'x-access-token': token},
                           data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        data = hunt_through_indicators(self.payload['indicators'].split(','), 'md5', 'foobar', 'kernel_modules', 0, 100)
        assert response_dict['data']['count'] == 2
        assert response_dict['data']['results'] == data[2]['results']

    def test_indicator_hunt_all_payload_value_with_pagination(self, client, url_prefix, token, result_log):
        """
        Test-case with indicators, type, host-identifier,
        query-name and without pagination and with existing result_log and node data,
        expected output:- status is success,
        and resultant data is like hostname, host_identifier, query_name and count
        """
        self.payload['indicators'] = 'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
        self.payload['type'] = 'md5'
        self.payload['host_identifier'] = 'foobar'
        self.payload['query_name'] = 'kernel_modules'
        self.payload['start'] = 0
        self.payload['limit'] = 10
        resp = client.post(url_prefix + '/indicators/hunt', headers={'x-access-token': token},
                           data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        data = hunt_through_indicators(self.payload['indicators'].split(','), 'md5', 'foobar', 'kernel_modules', 0, 10)
        assert response_dict['data']['count'] == 2
        assert response_dict['data']['results'] == data[2]['results']

    def test_indicator_hunt_all_payload_value_with_invalid_pagination(self, client, url_prefix, token, result_log):
        """
        Test-case with payload of indicators, type, host_identifier and
        query-name and with existing result_log and node data, also with invalid pagination
        expected output:- status_code is 400
        """
        self.payload['host_identifier'] = 'foobar'
        self.payload['query_name'] = 'kernel_modules'
        self.payload['start'] = -3
        self.payload['limit'] = -5
        resp = client.post(url_prefix + '/indicators/hunt', headers={'x-access-token': token},
                           data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'


class TestExportHuntFileUpload:
    """
    Test-Case inside this block where these payload values are used,
    all payloads values are compulsory type, so if anyone value is not passed,
    it will return 400 i.e., bad request
    """
    fp = os.getcwd() + '/tests/eicar.com.txt'
    files = {'file': open(fp, 'rb')}
    payload = {'file': None, 'type': None, 'host_identifier': None, 'query_name': None}

    def test_with_no_payload(self, client, url_prefix, token):
        """
        Test-case without payload and without existing result_log and node data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/hunt-upload/export', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_with_empty_payload(self, client, url_prefix, token):
        """
        Test-case with empty dict of payload and without existing result_log and node data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/hunt-upload/export', headers={'x-access-token': token}, data={})
        assert resp.status_code == 400

    def test_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with none value of payload and without existing result_log and node data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/hunt-upload/export', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 400

    def test_with_payload_value_empty_str(self, client, url_prefix, token):
        """
        Test-case with none value of payload and without existing result_log and node data,
        expected output:- status_code is 400
        """

        self.payload['file'] = ''
        self.payload['type'] = ''
        self.payload['host_identifier'] = ''
        self.payload['query_name'] = ''
        resp = client.post(url_prefix + '/hunt-upload/export', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 400

    def test_with_all_payload_value_except_file_field(self, client, url_prefix, token):
        """
        Test-case with all payload value except file field
        without existing result_log and node data,
        expected output:- status_code is 400
        """
        self.payload['file'] = None
        self.payload['query_name'] = 'kernel_modules'
        self.payload['type'] = 'md5'
        self.payload['host_identifier'] = 'foobar'
        resp = client.post(url_prefix + '/hunt-upload/export', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 400

    def test_with_all_valid_payload_value(self, client, url_prefix, token):
        """
        Test-case with all payload values
        without existing result_log and node data,
        expected output:- status is failure
        """
        self.payload['file'] = self.files
        self.payload['type'] = 'md5'
        self.payload['host_identifier'] = 'foobar'
        self.payload['query_name'] = 'kernel_modules'
        resp = client.post(url_prefix + '/hunt-upload/export', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_with_only_valid_payload_value_of_file_field(self, client, url_prefix, token):
        """
        Test-case with only payload value of file field
        without existing result_log and node data,
        expected output:- status is failure
        """
        self.payload['file'] = {'file': open(self.fp, 'rb')}
        self.payload['type'] = None
        self.payload['host_identifier'] = None
        self.payload['query_name'] = None
        resp = client.post(url_prefix + '/hunt-upload/export', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_with_invalid_method(self, client, url_prefix, token, result_log):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        self.payload['file'] = {'file': open(self.fp, 'rb')}
        self.payload['type'] = 'md5'
        self.payload['host_identifier'] = 'foobar1'
        self.payload['query_name'] = 'kernel_modules'
        resp = client.get(url_prefix + '/hunt-upload/export', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 405

    def test_with_all_payload_except_file_field(self, client, url_prefix, token, result_log):
        """
        Test-Case with all payload value except file field, and
        without existing result_log and node data,
        expected output:- status_code is 400
        """
        self.payload['file'] = None
        self.payload['type'] = 'md5'
        self.payload['host_identifier'] = 'foobar1'
        self.payload['query_name'] = 'kernel_modules'
        resp = client.post(url_prefix + '/hunt-upload/export', headers={'x-access-token': token},
                           data=self.payload)
        assert resp.status_code == 400

    def test_with_all_valid_payload_except_host_identifier(self, client, url_prefix, token, result_log):
        """
        Test-Case with existing result_log and node data,
        and all valid payload value except host_identifier,
        expected output:- status is failure
        """

        self.payload['file'] = {'file': open(self.fp, 'rb')}
        self.payload['type'] = 'md5'
        self.payload['host_identifier'] = None
        self.payload['query_name'] = 'kernel_modules'
        resp = client.post(url_prefix + '/hunt-upload/export', headers={'x-access-token': token},
                           data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_with_any_valid_payload_except_query_name(self, client, url_prefix, token, result_log):
        """
        Test-Case with existing result_log and node data, and
        all valid payload value except host_identifier,
        expected output:- status_code is 200, and
        response_data of a csv file data of hunt_file data
        """

        self.payload['file'] = {'file': open(self.fp, 'rb')}
        self.payload['type'] = 'md5'
        self.payload['host_identifier'] = 'foobar'
        self.payload['query_name'] = None
        resp = client.post(url_prefix + '/hunt-upload/export', headers={'x-access-token': token},
                           data=self.payload)
        assert resp.status_code == 200
        assert resp.data == b'\r\n'

    def test_with_all_valid_payload(self, client, url_prefix, token, result_log):
        """
        Test-Case with existing result_log and node data, and
        all valid payload value,
        expected output:- status_code is 200, and
        response_data of a csv file data of hunt_file data
        """

        self.payload['file'] = {'file': open(self.fp, 'rb')}
        self.payload['type'] = 'md5'
        self.payload['host_identifier'] = 'foobar'
        self.payload['query_name'] = 'kernel_modules'
        resp = client.post(url_prefix + '/hunt-upload/export', headers={'x-access-token': token},
                           data=self.payload)
        assert resp.status_code == 200
        file_data = get_hunt_file_data('foobar', 'md5', 'kernel_modules')
        assert resp.data == file_data.data


class TestSearch:

    """
    Test-case inside this block where these payloads are used,
    out of all only conditions value is compulsory value and of dict type,
    and remaings are optional value and of str type and integer type,
    so if compulsory value is not passed or passed value type is other than
    specified type, then it will return 400 i.e., bad request
    """
    payload = {'conditions': None, 'host_identifier': None, 'query_name': None, 'start': None, 'limit': None}

    def test_search_without_payload_value(self, client, url_prefix, token):
        """
        Test-case without payloads without existing result_log and node data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/search', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_search_with_empty_payload(self, client, url_prefix, token):
        """
        Test-case with empty payloads without existing result_log and node data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/search', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_search_with_none_payload_value(self, client, url_prefix, token):
        """
        Test-case with None value of conditions in payloads
        without existing result_log and node data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/search', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_search_with_only_condition_payload_value(self, client, url_prefix, token):
        """
        Test-case with only compulsory payloads value,
        and without existing result_log and node data,
        expected output:- status is success
        """
        self.payload['conditions'] = conditions
        resp = client.post(url_prefix + '/search', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'

    def test_search_with_condition_payload_value_and_host_identifier(self, client, url_prefix, token):
        """
        Test-case with only compulsory payloads value,
        host-identifier and without existing result_log and node data,
        expected output:- status is failure
        """
        self.payload['conditions'] = conditions
        self.payload['host_identifier'] = 'foobar'
        resp = client.post(url_prefix + '/search', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_search_with_condition_payload_value_and_query_name(self, client, url_prefix, token):
        """
        Test-case with only compulsory payloads value,
        query_name and without existing result_log and node data,
        expected output:- status is success, and
        count i.e. 0 and resultant data should be empty list in this case
        """
        self.payload['conditions'] = conditions
        self.payload['host_identifier'] = ''
        self.payload['query_name'] = 'kernel_modules'
        resp = client.post(url_prefix + '/search', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'

    def test_search_with_all_payload_value_without_pagination(self, client, url_prefix, token):
        """
        Test-case with all payloads except start and limit but
        without existing result_log and node data,
        expected output:- status is success, and
        count i.e. 0 and resultant data should be empty list in this case
        """
        self.payload['conditions'] = conditions
        self.payload['host_identifier'] = 'foobar'
        self.payload['query_name'] = 'kernel_modules'
        resp = client.post(url_prefix + '/search', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == {'count': 0, 'results': []}

    def test_search_with_all_payload_value_with_pagination(self, client, url_prefix, token):
        """
        Test-case with all payloads with start and limit
        but without existing result_log and node data,
        expected output:- status is success, and
        count i.e. 0 and resultant data should be empty list in this case
        """
        self.payload['conditions'] = conditions
        self.payload['host_identifier'] = 'foobar1'
        self.payload['query_name'] = 'kernel_modules'
        self.payload['start'] = 0
        self.payload['limit'] = 10
        resp = client.post(url_prefix + '/search', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == {'count': 0, 'results': []}

    def test_search_with_all_payload_except_condition(self, client, url_prefix, token):
        """
        Test-case with all payloads value except
        condition, and without existing result_log and node data,
        expected output:- status_code is 400
        """
        self.payload['conditions'] = None
        self.payload['host_identifier'] = 'foobar'
        self.payload['query_name'] = 'kernel_modules'
        self.payload['start'] = 0
        self.payload['limit'] = 10
        resp = client.post(url_prefix + '/search', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_search_with_invalid_method(self, client, url_prefix, token, result_log):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        self.payload['conditions'] = conditions
        resp = client.get(url_prefix + '/search', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_search_with_all_none_payload_value(self, client, url_prefix, token, result_log):
        """
        Test-case with empty paylodas and conditions
        is None and with existing result_log and node data,
        expected output:- status_code is 400
        """
        self.payload['conditions'] = None
        self.payload['host_identifier'] = ''
        self.payload['query_name'] = ''
        self.payload['start'] = None
        self.payload['limit'] = None
        resp = client.post(url_prefix + '/search', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_search_with_only_condition_value_payload(self, client, url_prefix, token, result_log):
        """
        Test-case with paylodas value of only
        conditions and with existing result_log and node data,
        expected output:- status is success, and
        count i.e. 0 and resultant data should be empty list in this case
        """
        self.payload['conditions'] = conditions
        resp = client.post(url_prefix + '/search', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'

    def test_search_with_only_compulsory_value_and_host_identifier(self, client, url_prefix, token, result_log):
        """
        Test-case with paylodas value of only conditions
        and host_identifier and with existing result_log and node data,
        expected output:- status is failure
        """
        self.payload['conditions'] = conditions
        self.payload['host_identifier'] = 'foobar11'
        resp = client.post(url_prefix + '/search', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_search_with_only_compulsory_value_and_query_name(self, client, url_prefix, token, result_log):
        """
        Test-case with paylodas value of only conditions
        and host_identifier and with existing result_log and node data,
        expected output:- status is success, and
        count i.e. 0 and resultant data should be empty list in this case
        """
        self.payload['conditions'] = conditions
        self.payload['host_identifier'] = ''
        self.payload['query_name'] = 'kernel_modules'
        resp = client.post(url_prefix + '/search', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'

    def test_search_with_all_payload_except_pagination(self, client, url_prefix, token, result_log):
        """
        Test-case with all payload value except
        start and limit and with existing result_log and node data,
        expected output:- status is success,
        and resultant data
        """
        self.payload['conditions'] = conditions
        self.payload['host_identifier'] = 'foobar'
        self.payload['query_name'] = 'kernel_modules'
        resp = client.post(url_prefix + '/search', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        root = search_rules.parse_group(conditions)
        filter = root.run('', [], 'result_log')
        qs = common_dao.result_log_search_results(
            filter, [node.id for node in get_nodes_for_host_id('foobar')], 'kernel_modules', 0, 100)
        # data = [data_elem[0] for data_elem in data]
        assert response_dict['data'] == {'count':qs['count'], 'results':[data_elem[0] for data_elem in qs['results']]}

    def test_search_with_all_payload_with_pagination(self, client, url_prefix, token, result_log):
        """
        Test-case with all paylodas value including
        pagination and with existing result_log and node data,
        expected output:- status is success,
        and resultant data
        """
        self.payload['conditions'] = conditions
        self.payload['host_identifier'] = 'foobar'
        self.payload['query_name'] = 'kernel_modules'
        self.payload['start'] = 0
        self.payload['limit'] = 10
        resp = client.post(url_prefix + '/search', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        root = search_rules.parse_group(conditions)
        filter = root.run('', [], 'result_log')
        qs = common_dao.result_log_search_results(
            filter, [node.id for node in get_nodes_for_host_id('foobar')], 'kernel_modules', 0, 100)
        # data = [data_elem[0] for data_elem in data]
        assert response_dict['data'] == {'count':qs['count'], 'results':[data_elem[0] for data_elem in qs['results']]}

    def test_search_with_all_payloads_except_condition(self, client, url_prefix, token, result_log):
        """
        Test-case with all paylodas value including pagination
        except condition and with existing result_log and node data,
        expected output:- status_code is 400
        """
        self.payload['conditions'] = None
        self.payload['host_identifier'] = 'foobar1'
        self.payload['query_name'] = 'kernel_modules'
        self.payload['start'] = 0
        self.payload['limit'] = 6
        resp = client.post(url_prefix + '/search', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400


class TestDeleteQueryResult:
    """
    Test-case inside this block where this payload values are used,
    this is compulsory payload value of integer type, so if value not
    passed then it will return 400 i.e., bad request
    """
    payload = {'days_of_data': None}

    def test_delete_query_result_without_payload(self, client, url_prefix, token):
        """
        Test-case without payload and without existing result_log data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/queryresult/delete', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_delete_query_result_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload is empty dictionary and without existing result_log data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/queryresult/delete', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_delete_query_result_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with payload value none and without existing result_log data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/queryresult/delete', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_delete_query_result_with_valid_payload(self, client, url_prefix, token):
        """
        Test-case with valid payload value and without existing result_log data,
        expected output:- status is success
        """
        self.payload['days_of_data'] = 2
        resp = client.post(url_prefix + '/queryresult/delete', headers={'x-access-token': token},
                           json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'

    def test_query_result_with_invalid_method(self, client, url_prefix, token, result_log):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.get(url_prefix + '/queryresult/delete', headers={'x-access-token':token},
                          json=self.payload)
        assert resp.status_code == 405

    def test_delete_query_result_with_data(self, client, url_prefix, token, node, result_log):
        """
        Test-case with valid payload value and with existing result_log data
        expected output:- status is success,
        """
        self.payload['days_of_data'] = 2
        resp = client.post(url_prefix + '/queryresult/delete', headers={'x-access-token': token},
                           json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'


class TestExportScheduleQueryCSV:
    """
    Test-case inside this block where these payloads are used,
    both of the values are compulsory payload value, and of str type
    so if value is not passed or passed any other type than str,
    it will return 400 i.e. bad request
    """
    payload = {'query_name': None, 'host_identifier': None}

    def test_export_schedule_query_without_payload(self, client, url_prefix, token):
        """
        Test-case without payloads and without existing node and result_log data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/schedule_query/export', headers={'x-access-token':token})
        assert resp.status_code == 400

    def test_export_schedule_query_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload is empty dictionary and without existing node and result_log data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/schedule_query/export', headers={'x-access-token': token},
                           json=self.payload)
        assert resp.status_code == 400

    def test_export_schedule_query_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with payload value none and without existing node and result_log data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/schedule_query/export', headers={'x-access-token': token},
                           json=self.payload)
        assert resp.status_code == 400

    def test_export_schedule_query_with_only_host_identifier(self, client, url_prefix, token):
        """
        Test-case with only payload value of host_identifier
        and without existing node and result_log data,
        expected output:- status_code is 400
        """
        payload = {'host_identifier': 'foobar'}
        resp = client.post(url_prefix + '/schedule_query/export', headers={'x-access-token': token},
                           json=payload)
        assert resp.status_code == 400

    def test_export_schedule_query_with_only_query_name(self, client, url_prefix, token):
        """
        Test-case with only payload value of query_name
        and without existing node and result_log data,
        expected output:- status_code is 400
        """
        payload = {'query_name': 'kernel_modules'}
        resp = client.post(url_prefix + '/schedule_query/export', headers={'x-access-token': token},
                           json=payload)
        assert resp.status_code == 400

    def test_export_schedule_query_with_valid_payload_value(self, client, url_prefix, token):
        """
        Test-case with valid payload value and without existing node and result_log data,
        expected output:- status is failure
        """
        self.payload['host_identifier'] = 'foobar'
        self.payload['query_name'] = 'kernel_modules'
        resp = client.post(url_prefix + '/schedule_query/export', headers={'x-access-token': token},
                           json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_export_schedule_query_with_invalid_method(self, client, url_prefix, token, result_log):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.get(url_prefix + '/schedule_query/export', headers={'x-access-token':token},
                          json=self.payload)
        assert resp.status_code == 405

    def test_exports_schedule_query_with_only_host_identifier(self, client, url_prefix, token):
        """
        Test-case with only payload value of host_identifier
        and with existing node and result_log data,
        expected output:- status_code is 400
        """
        payload = {'host_identifier': 'foobar'}
        resp = client.post(url_prefix + '/schedule_query/export', headers={'x-access-token': token},
                           json=payload)
        assert resp.status_code == 400

    def test_exports_schedule_query_with_only_query_name(self, client, url_prefix, token, result_log):
        """
        Test-case with only payload value of query_name
        and with existing node and result_log data,
        expected output:- status_code is 400
        """
        payload = {'query_name': 'kernel_modules'}
        resp = client.post(url_prefix + '/schedule_query/export', headers={'x-access-token': token},
                           json=payload)
        assert resp.status_code == 400

    def test_exports_schedule_query_with_invalid_host_identifier(self, client, url_prefix, token, result_log):
        """
        Test-case with invalid payload value of host_identifier
        and with existing node and result_log data,
        expected output:- status is failure
        """
        payload = {'host_identifier': 'foo', 'query_name': 'kernel_modules'}
        resp = client.post(url_prefix + '/schedule_query/export', headers={'x-access-token': token},
                           json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_exports_schedule_query_with_invalid_query_name(self, client, url_prefix, token, result_log):
        """
        Test-case with invalid payload value of query_name
        and with existing node and result_log data,
        expected output:- status is failure
        """
        payload = {'host_identifier': 'foobar', 'query_name': 'test_query'}
        resp = client.post(url_prefix + '/schedule_query/export', headers={'x-access-token': token},
                           json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_exports_schedule_query_with_valid_payload_value(self, client, url_prefix, token, result_log):
        """
        Test-case with valid payload value and with existing node and result_log data,
        expected output:- status_code is 200, and
        a csv file data
        """
        self.payload['host_identifier'] = 'foobar'
        self.payload['query_name'] = 'kernel_modules'
        resp = client.post(url_prefix + '/schedule_query/export', headers={'x-access-token': token},
                           json=self.payload)
        assert resp.status_code == 200
        assert resp.data == get_export_query_schedule_csv_data('foobar', 'kernel_modules').data


class TestGetOption:

    def test_get_option_with_empty_data(self, client, url_prefix, token):
        """
        Test-Case without existing options data,
        expected output:- status is failure
        """
        resp = client.get(url_prefix + '/options', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_option_with_inavlid_method(self, client, url_prefix, token, options):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.post(url_prefix + '/options', headers={'x-access-token': token})
        assert resp.status_code == 405

    def test_get_option_with_existing_data(self, client, url_prefix, token, options):
        """
        Test-case without PolyLogyxServerDefaults data but with existing other options data,
        expected output:- status is failure
        """
        resp = client.get(url_prefix + '/options', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_option_with_polylogyxserverdefaults_data(self, client, url_prefix, token, options):
        """
        Test-case with PolyLogyxServerDefaults data along with other existing options data
        expected output:- status is success, and
        resultant options data
        """
        option = {
            "custom_plgx_EnableLogging": "true", "custom_plgx_EnableSSL": "true",
            "custom_plgx_LogFileName": "C:\\Program Files\\plgx_win_extension\\plgx-agent.log"
        }
        opt = OptionsFactory(name=PolyLogyxServerDefaults.plgx_config_all_options, option=json.dumps(option))
        db.session.commit()
        resp = client.get(url_prefix + '/options', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == option


class TestAddOrUpdateOption:
    """
    Test-case inside this block where theis payload value is used,
    this is compulsory payload value and of dict type,
    so if the value is not passed or value type is other than dict,
    then it will return 400 i.e., bad request
    """
    payload = {'option': None}

    def test_add_or_update_option_with_no_payload(self, client, url_prefix, token):
        """
        Test-case with no payloads and without existing options data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/options/add', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_add_or_update_option_with_empty_payload(self, client, url_prefix, token):
        """
        Test-case with Empty Payloads and without existing options data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/options/add', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_add_or_update_option_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with None value for options in payloads,
        and without existing options data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/options/add', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_add_or_update_option_with_valid_payload(self, client, url_prefix, token):
        """
        Test-case with a value of options in payloads,
        and without existing options data,
        expected output:- status is success,
        and resultant_data should be same as payload value of str type
        """
        self.payload['option'] = {'value': 'logger_plugin'}
        resp = client.post(url_prefix + '/options/add', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == '{"value": "logger_plugin"}'

    def test_add_or_update_option_with_invalid_method(self, client, url_prefix, token, options):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        self.payload['option'] = None
        resp = client.get(url_prefix + '/options/add', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_add_or_update_option_none_value_payload(self, client, url_prefix, token, options):
        """
        Test-case with None value for options in payloads,
        and with existing options data,
        expected output:- status_code is 400
        """
        self.payload['option'] = None
        resp = client.post(url_prefix + '/options/add', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_add_option_value_payload(self, client, url_prefix, token, options):
        """
        Test-case with a value of options in payloads,
        and with existing options data,
        expected output:- status is success,
        and resultant option value should be same as payload value of str type
        """
        self.payload['option'] = {'value': 'logger_plugin'}
        resp = client.post(url_prefix + '/options/add', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == '{"value": "logger_plugin"}'

    def test_add_or_update_option_value_payload_with_existing_value(self, client, url_prefix, token, options):
        """
        Test-case with a value of options in payloads
        as well as existing option is present,
        expected output:- status is success,
        and resultant option value should be same as payload value
        """
        from .factories import OptionsFactory

        self.payload['option'] = {'test_data': 'testing_existing_option_data'}
        new_option = OptionsFactory(name=PolyLogyxServerDefaults.plgx_config_all_options, option='logger_tls')
        resp = client.post(url_prefix + '/options/add', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == {"test_data": "testing_existing_option_data"}


def get_hunt_file_data(host_identifier, type, query_name):
    lines = None
    fp = os.getcwd() + '/tests/eicar.com.txt'

    file = open(fp, 'rb')
    nodes = get_nodes_for_host_id(host_identifier)

    try:
        lines = [line.decode('utf-8').replace('\n', '').replace('\r', '') for line in file.readlines()]
    except Exception as e:
        message = "We are unable to read this file with this format!"
    if lines is not None:
        if nodes:
            try:
                results = common_dao.result_log_query_for_export(lines, type, [node.id for node in nodes], query_name)
                results = [r for r, in results]
                headers = []
                if not len(results) == 0:
                    firstRecord = results[0]
                    for key in firstRecord.keys():
                        headers.append(key)

                bio = BytesIO()
                writer = csv.writer(bio)
                writer.writerow(headers)

                for data in results:
                    row = []
                    row.extend([data.get(column, '') for column in headers])
                    writer.writerow(row)

                bio.seek(0)

                file_data = send_file(
                    bio,
                    mimetype='text/csv',
                    as_attachment=True,
                    attachment_filename='hunt_query_results.csv'
                )
                file_data.direct_passthrough = False
                return file_data
            except:
                data = []
                return data


def get_export_query_schedule_csv_data(host_identifier, query_name):
    node_id = get_node_id_by_host_id(host_identifier)
    record_query = common_dao.record_query(node_id, query_name)
    results = [r for r, in record_query]
    headers = []
    if not len(results) == 0:
        firstRecord = results[0]
        for key in firstRecord.keys():
            headers.append(key)

    bio = BytesIO()
    writer = csv.writer(bio)
    writer.writerow(headers)

    for data in results:
        row = []
        row.extend([data.get(column, '') for column in headers])
        writer.writerow(row)

    bio.seek(0)

    file_data = send_file(
        bio,
        mimetype='text/csv',
        as_attachment=True,
        attachment_filename='query_results.csv'
    )
    file_data.direct_passthrough = False
    return file_data
