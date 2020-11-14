"""
All Test-Case required client, url_prefix and token,
and these all we need to just pass as parameters in the function.
"""

import json

from polylogyx.constants import PolyLogyxServerDefaults


class TestGetSchema:

    def test_get_schema(self, client, url_prefix, token):
        """
        Test-case of get schema of table,
        expected output:- status is success, and
        response data should be equal to default server data
        """
        resp = client.get(url_prefix + '/schema', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        data = PolyLogyxServerDefaults.POLYLOGYX_OSQUERY_SCHEMA_JSON
        assert response_dict['data'] == data

    def test_get_schema_with_invalid_method(self, client, url_prefix, token):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.post(url_prefix + '/schema', headers={'x-access-token': token})
        assert resp.status_code == 405


class TestGetTableSchema:

    def test_get_table_schema(self, client, url_prefix, token):
        """
        Test-Case with valid table name which is passing through url,
        expected output:- status is success, and
        response data should be schema of particular table which passing through url
        """
        resp = client.get(url_prefix + '/schema/carves', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        schema_json = PolyLogyxServerDefaults.POLYLOGYX_OSQUERY_SCHEMA_JSON
        if 'carves':
            table_schema = schema_json['carves']
        assert response_dict['data'] == table_schema

    def test_get_with_invalid_table_name_schema(self, client, url_prefix, token):
        """
        Test-Case with invalid table name which is passing through url,
        expected output:- status is failure
        """
        resp = client.get(url_prefix + '/schema/carve', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_table_schema_with_invalid_method(self, client, url_prefix, token):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.post(url_prefix + '/schema/carves', headers={'x-access-token': token})
        assert resp.status_code == 405

