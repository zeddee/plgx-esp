"""
All Test-Case required client, url_prefix and token,
and these all we need to just pass as parameters in the function.
"""

import json, os

from polylogyx.dao import iocs_dao

data = {
                "test-intel_ipv4": {
                    "type": "remote_address",
                    "values": "3.30.1.15,3.30.1.16",
                    "severity": "WARNING"
                },
                "test-intel_domain_name": {
                    "type": "domain_name",
                    "values":"unknown.com,slackabc.com",
                    "severity": "WARNING"
                },
                "test-intel_md5": {
                    "type": "md5",
                    "values": "3h8dk0sksm0,9sd772ndd80",
                    "severity": "INFO"
                }
            }


class TestListIocs:

    def test_get_list_of_iocs_without_data(self, client, url_prefix, token):
        """
        Test-case without ioc_intel data,
        expected output:- status is success, and
        resultant ioc_data
        """
        resp = client.get(url_prefix + '/iocs', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == data

    def test_get_list_of_iocs_with_invalid_method(self, client, url_prefix, token):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.post(url_prefix + '/iocs', headers={'x-access-token': token})
        assert resp.status_code == 405

    def test_get_list_of_iocs_with_data(self, client, url_prefix, token, ioc_intel):
        """
       Test-case with ioc_intel data,
       expected output:- status is success, and
       resultant ioc_data
       """
        resp = client.get(url_prefix + '/iocs', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        ioc_data = {}
        for ioc in iocs_dao.get_intel_data('self'):
            ioc_data[ioc.threat_name] = {'type':ioc.type, 'severity':ioc.severity, 'intel_type':ioc.intel_type, 'values':ioc.value}
        assert response_dict['data'] == ioc_data


class TestAddIocs:

    """
    Test-case inside this block where this payload value is used,
    this is compulsory payload value of dict type, so if value is not passed
    or passed any other type than dict, then it will return 400 i.e., bad request
    """
    payload = {'data': data}

    def test_add_ioc_without_payload(self, client, url_prefix, token):
        """
        Test-Case without payload and without ioc_intel data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/iocs/add', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_add_ioc_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-Case with payload is empty dictionary and without ioc_intel data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/iocs/add', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_add_ioc_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-Case with payload value is none and without ioc_intel data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/iocs/add', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_add_ioc_with_empty_file_data(self, client, url_prefix, token):
        """
        Test-Case with payload value is empty dictionary and without ioc_intel data,
        expected output:- status is success
        """
        self.payload['data'] = {}
        resp = client.post(url_prefix + '/iocs/add', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'

    def test_add_ioc_with_invalid_type_file_data(self, client, url_prefix, token):
        """
        Test-Case with payload value is invalid type of file data and without ioc_intel data,
        expected output:- status_code is 400
        """
        self.payload['data'] = 'data'
        resp = client.post(url_prefix + '/iocs/add', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_add_ioc_with_invalid_method(self, client, url_prefix, token):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.get(url_prefix + '/iocs/add', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_add_iocs_with_empty_file_data(self, client, url_prefix, token, ioc_intel):
        """
        Test-Case with payload value is empty dictionary and with ioc_intel data,
        expected output:- status is success
        """
        self.payload['data'] = {}
        resp = client.post(url_prefix + '/iocs/add', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'

    def test_add_iocs_with_invalid_type_file_data(self, client, url_prefix, token, ioc_intel):
        """
        Test-Case with payload value is invalid type of file data and without ioc_intel data,
        expected output:- status_code is 400
        """
        self.payload['data'] = 'data'
        resp = client.post(url_prefix + '/iocs/add', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_add_ioc_with_file_data(self, client, url_prefix, token, ioc_intel):
        """
        Test-case with valid file data and with existing ioc_intel data,
        expeceted output:- status is success
        """
        self.payload['data'] = data
        resp = client.post(url_prefix + '/iocs/add', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
