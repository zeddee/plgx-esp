"""
All Test-Case required client, url_prefix and token,
and these all we need to just pass as parameters in the function.
"""

import json
import datetime as dt
import unicodecsv as csv
from io import BytesIO
from flask import send_file
from flask_restplus import marshal
from sqlalchemy import and_

from polylogyx.blueprints.utils import SearchParser
from polylogyx.dao import hosts_dao, packs_dao, tags_dao, queries_dao
from polylogyx.models import Tag, Node, db
from polylogyx.utils import assemble_additional_configuration, assemble_options, assemble_configuration
from polylogyx.wrappers import host_wrappers

search_rules = SearchParser()


class TestHostsList:
    """
    for all the test-cases under this block, where we used payload value,
    status value is True/False, Platform value is windows/linux/darwin/posix/freebsd,
    searchterm is any string value related to node like platform, or name etc,
    start and limit should be integer number and enbled is a boolean value.
    and all payload values are optional, so if value passed that
    is not matched with the specified type, then it will return 400 i.e., bad request
    """
    payload = {
        'status': True, 'platform': 'windows',  'searchterm': '',
        'start':0, 'limit': 25 , 'enabled': True
    }

    def test_hosts_list_without_payload(self, client, url_prefix, token):
        """
        Test-case without payloads and without existing node data
        expected output:- status is success, and
        node count by platform and total_node count as well as node details,
        e.g.,
        results is empty list, count and total_count is 0 in this case
        """
        resp = client.post(url_prefix + '/hosts', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == {'results': [], 'count':0, 'total_count': 0}

    def test_hosts_list_with_empty_payload(self, client, url_prefix, token):
        """
        Test-case with empty dictionary as payloads and without existing node data
        expected output:- status is success, and
        node count by platform and total_node count as well as node details
        e.g.,
        results is empty list, count and total_count is 0 in this case
        """
        resp = client.post(url_prefix + '/hosts', headers={'x-access-token': token},  json={})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 0
        assert response_dict['data']['total_count'] == 0
        assert response_dict['data']['results'] == []

    def test_hosts_list_with_empty_and_none_val_payload(self, client, url_prefix, token):
        """
        Test-case with all payloads values are none and without existing node data
        expected output:- status_code is 400
        """
        payload = {
            'status': None, 'platform': None, 'searchterm': None,
            'start': None, 'limit': None, 'enabled': None
        }
        resp = client.post(url_prefix + '/hosts', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 400

    def test_hosts_list_with_all_payload(self, client, url_prefix, token):
        """
        Test-case with all payloads and without existing node data
        this is valid for all type of platform as well as status
        True or False,
        expected output:- status is success, and
        node count by platform and total_node count as well as node details
         e.g.,
        results is empty list, count and total_count is 0 in this case
        """
        resp = client.post(url_prefix + '/hosts', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 0
        assert response_dict['data']['total_count'] == 0
        assert response_dict['data']['results'] == []

    def test_hosts_list_with_all_payload_except_searchterm(self, client, url_prefix, token):
        """
        Test-case with all payloads except searchterm and without
        existing node data this is valid for all type of platform
        as well as status True or False
        expected output:- status is success, and
        node count by platform and total_node count as well as node details
         e.g.,
        results is empty list, count and total_count is 0 in this case
        """
        payload = {
            'status': True, 'platform': 'windows',
            'start': 0, 'limit': 10, 'enabled': True
        }
        resp = client.post(url_prefix + '/hosts', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 0
        assert response_dict['data']['total_count'] == 0
        assert response_dict['data']['results'] == []

    def test_hosts_list_with_only_payload_platform(self, client, url_prefix, token):
        """
        Test-case with payloads of only platforms value and without existing node data
        and it's valid for any platform(windows/linux/darwin/posix/freebsd)
        expected output:- status is success, and
        node count by platform and total_node count as well as node details
         e.g.,
        results is empty list, count and total_count is 0 in this case
        """
        payload = {'platform': 'windows'}
        resp = client.post(url_prefix + '/hosts', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 0
        assert response_dict['data']['total_count'] == 0
        assert response_dict['data']['results'] == []

    def test_hosts_list_with_only_payload_darwin_platform(self, client, url_prefix, token):
        """
        Test-case with payloads of only platforms value is darwin and without existing data
        expected output:- status is success,
        node count by platform and total_node count as well as node details
         e.g.,
        results is empty list, count and total_count is 0 in this case
        """
        payload = {'platform': 'windows'}
        resp = client.post(url_prefix + '/hosts', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 0
        assert response_dict['data']['total_count'] == 0
        assert response_dict['data']['results'] == []

    def test_hosts_list_with_invalid_method(self, client, url_prefix, token, node):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.get(url_prefix + '/hosts', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_host_list_without_payload(self, client, url_prefix, token, node):
        """
        Test-case without payloads and without existing node data
        expected output:- status is success, and
        node count by platform and total_node count as well as node details,
        e.g.,
        results is details of node(like display_name, host_identifier,
        os_info, tags, last_ip, and is_active),
        count and total_count is 1 in this case
        """
        resp = client.post(url_prefix + '/hosts', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        data = get_host_list_data()
        assert response_dict['data']['results'] == data['results']

    def test_hosts_list_with_payload_value_is_empty(self, client, url_prefix, token, node):
        """
        Test-case with empty payloads and with existing node data,
        expected output:- status is success, and
        node count by platform and total_node count as well as node details
         e.g.,
        results is details of node(like display_name, host_identifier,
        os_info, tags, last_ip, and is_active),
        count and total_count is 1 in this case
        """
        resp = client.post(url_prefix + '/hosts', headers={'x-access-token': token},  json={})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        data = get_host_list_data()
        assert response_dict['data']['results'] == data['results']

    def test_hosts_list_with_none_value_payload(self, client, url_prefix, token, node):
        """
        Test-case with payloads value is empty str and  None but with existing node data,
        expected output:- status code is 400
        """
        payload = {
            'status': None, 'platform': None, 'searchterm': None,
            'start':'None', 'limit': None, 'enabled': None
        }
        resp = client.post(url_prefix + '/hosts', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 400

    def test_hosts_list_with_pltf_and_status_true(self, client, url_prefix, token, node):
        """
        Test-case with all payloads and status is True and with existing node data
        and will get type of result for any platform type if status is true
        expected output:- status is success, and
        node count by platform and total_node count as well as node details
        e.g.,
        results is empty list in this case,
        os_info, tags, last_ip, and is_active),
        count and total_count is 0 in this case
        """
        payload = {'platform': 'windows', 'status': True}
        resp = client.post(url_prefix + '/hosts', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        data = get_host_list_data(True, 'windows')
        assert response_dict['data']['results'] == data['results']

    def test_hosts_list_with_pltf_darwin_and_status_false(self, client, url_prefix, token, node):
        """
        Test-case with all payloads and status is False and with existing node data
        and will get same type of result for any platform(windows/linux/darwin/posix/freebsd)
        type if status is false,
        expected output:- status is success, and
        node count by platform and total_node count as well as node details
        e.g.,
        results is empty list, count and total_count is 0 in this case
        """
        payload = {'platform': 'darwin', 'status': False}
        resp = client.post(url_prefix + '/hosts', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 0
        assert response_dict['data']['total_count'] == 0
        assert response_dict['data']['results'] == []

    def test_hosts_list_with_only_pltf(self, client, url_prefix, token, node):
        """
        Test-case with payloads of only platforms value and with existing
        node data and will get same result with any type of platform,
        expected output:- status is success, and
        node count by platform and total_node count as well as node details
        e.g.,
        results is details of node(like display_name, host_identifier,
        os_info, tags, last_ip, and is_active),
        count and total_count is 1 in this case
        """
        payload = {'platform': 'windows'}
        resp = client.post(url_prefix + '/hosts', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        data = get_host_list_data('windows')
        assert response_dict['data']['results'] == data['results']

    def test_hosts_list_with_all_payload_except_serchterm(self, client, url_prefix, token, node):
        """
        Test-case with all payloads except searchtermand with existing node data
        and will get same result for any platform type if status is true,
        expected output:- status is success, and
        node count by platform and total_node count as well as node details
        e.g.,
        results is details of node(like display_name, host_identifier,
        os_info, tags, last_ip, and is_active),
        count and total_count is 1 in this case
        """
        payload = {
            'status': True, 'platform': 'windows',
            'start': 0, 'limit': 25, 'enabled': True
        }
        resp = client.post(url_prefix + '/hosts', headers={'x-access-token': token}, data=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        data = get_host_list_data(True, 'windows', None, True, 0 ,5)
        assert response_dict['data']['results'] == data['results']

    def test_host_list_with_all_payload(self, client, url_prefix, token, node):
        """
        Test-case with all payloads and with existing node data
        this is valid for all type of platform as well as status
        True or False,
        expected output:- status is success, and
        node count by platform and total_node count as well as node details
         e.g.,
        results is empty list, count and total_count is 1 in this case
        """
        payload = {
            'status': True, 'platform': 'windows', 'searchterm': '',
            'start': 0, 'limit': 25, 'enabled': True
        }
        resp = client.post(url_prefix + '/hosts', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        data = get_host_list_data(True, 'windows', '', True, 0, 5)
        assert response_dict['data']['results'] == data['results']


class TestNodesCSV:

    def test_get_nodes_csv_when_node_unavailable(self, client, url_prefix, token):
        """
        Test-case without existing node data,
        expected output:- status_code is 200, and
        response_data of a csv file, here it's in form of binary object
        """
        resp = client.get(url_prefix + '/hosts/export', headers={'x-access-token': token})
        assert resp.status_code == 200
        assert resp.data == b'\r\n'

    def test_get_nodes_csv_with_invalid_method(self, client, url_prefix, token, node):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.post(url_prefix + '/hosts/export', headers={'x-access-token': token})
        assert resp.status_code == 405

    def test_get_nodes_csv_with_data(self, client, url_prefix, token, node):
        """
        Test-case with existing node data,
        expected output:- status_code is 200, and
        response_data of a csv file, here it's in form of binary object
        """
        resp = client.get(url_prefix + '/hosts/export', headers={'x-access-token': token})
        assert resp.status_code == 200
        assert resp.data == b'Host_Identifier,os,last_ip,tags,id,health,platform\r\nfoobar,windows,,[],1,True,windows\r\n'


class TestNodeDetailsList:

    def test_get_details_with_host_identifier(self, client, url_prefix, token):
        """
        Test-case with valid/invalid host-identifier/node_id which are
        passing through url and without existing node data,
        expected output:- status is failure
        """
        resp = client.get(url_prefix + '/hosts/foobar', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_details_with_invalid_method(self, client, url_prefix, token):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.post(url_prefix + '/hosts/1', headers={'x-access-token': token})
        assert resp.status_code == 405

    def test_get_details_with_invalid_node_id(self, client, node, url_prefix, token):
        """
        Test-case with invalid host-identifier/node-id which are
        passing through url and with existing node data
        expected output:- status is failure
        """
        resp = client.get(url_prefix + '/hosts/5', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_details_with_valid_host_identifier(self, client, node, url_prefix, token):
        """
        Test-case with valid host-identifier which is
        passing through url and with existing node data,
        expected output:- status is success, and
        and all node data(like, nodeinfo, platform etc.)
        """
        resp = client.get(url_prefix + '/hosts/foobar', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        data = hosts_dao.get_node_by_host_identifier('foobar')
        assert response_dict['data'] == marshal(data, host_wrappers.nodewrapper)

    def test_get_details_with_valid_node_id(self, client, node, url_prefix, token):
        """
        Test-case with valid node-id which is passing
        through url and with existing node data,
        expected output:- status is success, and
        and all node data(like, nodeinfo, platform etc.)
        """
        resp = client.get(url_prefix + '/hosts/1', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        data = hosts_dao.getNodeById(1)
        assert response_dict['data'] == marshal(data, host_wrappers.nodewrapper)


class TestNodeCountList:

    def test_get_hosts_count_without_node_data(self, client, url_prefix, token):
        """
        Test-case without payload and without existing node data,
        expected output:- status is success, and
        and online and offline node count based on platform name
        e.g.,
        online node count of windows is 0, and
        offline of node count of windows is 0.
        """
        resp = client.get(url_prefix + '/hosts/count', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['windows']['online'] == 0
        assert response_dict['data']['windows']['offline'] == 0
        assert response_dict['data']['linux']['online'] == 0
        assert response_dict['data']['linux']['offline'] == 0
        assert response_dict['data']['darwin']['online'] == 0
        assert response_dict['data']['darwin']['offline'] == 0

    def test_get_hosts_count_with_invalid_method(self, client, url_prefix, token):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.post(url_prefix + '/hosts/count', headers={'x-access-token': token})
        assert resp.status_code == 405

    def test_get_host_count_with_node_data(self, client, node, url_prefix, token):
        """
        Test-case without payload and without existing node data,
        expected output:- status is success, and
        and online and offline node count based on platform name
        e.g.,
        online node count of windows is 1, and
        offline of node count of windows is 0.
        """
        resp = client.get(url_prefix + '/hosts/count', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['windows']['online'] == 1
        assert response_dict['data']['windows']['offline'] == 0
        assert response_dict['data']['linux']['online'] == 0
        assert response_dict['data']['linux']['offline'] == 0
        assert response_dict['data']['darwin']['online'] == 0
        assert response_dict['data']['darwin']['offline'] == 0


class TestHostStatusLogs:
    """
    Test-case where we used any of this payload,
    start,limit and node_id value should be integer value, and
    host_identifier and searchterm should be a string value like name,
    and all are optional value, so if payload value is not as the specified type,
    then it will return 400 i.e., bad request
    """
    payload = {
        'host_identifier': None, 'node_id': None, 'start': None, 'limit': None, 'searchterm': None
    }

    def test_get_host_status_log_without_payload(self, client, url_prefix, token):
        """
        Test-Case without payload along with host_identifier/node_id
        and without existing node data,
        expected output:- status is failure
        """
        resp = client.post(url_prefix + '/hosts/status_logs', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_host_status_log_with_empty_payload(self, client, url_prefix, token):
        """
        Test-Case with empty dictionary payload value and host_identifier/node_id
        and without existing node data
        expected output:- status is failure
        """
        resp = client.post(url_prefix + '/hosts/status_logs', headers={'x-access-token': token}, json={})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_host_status_log_with_none_val_payload(self, client, url_prefix, token):
        """
        Test-Case with none value of payload value along with host_identifier/node_id
        which is passing through url and without existing node data,
        expected output:- status is failure
        """
        resp = client.post(url_prefix + '/hosts/status_logs', headers={'x-access-token': token},
                          json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_host_status_log_without_pagination(self, client, url_prefix, token):
        """
        Test-Case without pagination and with host_identifier/node_id
        and without existing node data,
        expected output:- status is failure
        """
        payload = {'host_identifier': 'foobar', 'node_id': 1, 'searchterm': 'foobar2'}
        resp = client.post(url_prefix + '/hosts/status_logs', headers={'x-access-token': token},
                          json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_host_status_log_with_pagination(self, client, url_prefix, token):
        """
        Test-Case with pagination along and with host_identifier/node_id
        and without existing node data,
        expected output:- status is failure
        """
        self.payload['node_id'] = 1
        self.payload['host_identifier'] = 'foobar'
        self.payload['start'] = 0
        self.payload['limit'] = 5
        self.payload['searchterm'] = 'foobar'
        resp = client.post(url_prefix + '/hosts/status_logs', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_host_status_log_with_invalid_method(self, client, url_prefix, token, status_log):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.put(url_prefix + '/hosts/status_logs', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_get_hosts_status_log_without_payload(self, client, url_prefix, token, status_log):
        """
        Test-case without payloads but with host_identifier/node_id
        along with existing status_log and node data,
        expected output:- status is failure
        """
        resp = client.post(url_prefix + '/hosts/status_logs', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_hosts_status_log_with_empty_payload(self, client, url_prefix, token, status_log):
        """
        Test-case with Empty Payloads but with host_identifier/node_id
        along with existing status_log and node data,
        expected output:- status is failure
        """
        resp = client.post(url_prefix + '/hosts/status_logs', headers={'x-access-token': token}, json={})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_host_status_log_with_payload_value_none(self, client, url_prefix, token, status_log):
        """
        Test-Case with none value of payload value along with host_identifier/node_id
        and with existing status_log and node data,
        expected output:- status is failure
        """
        payload = {
            'host_identifier': None, 'node_id': None, 'start': None, 'limit': None, 'searchterm': None
        }
        resp = client.post(url_prefix + '/hosts/status_logs', headers={'x-access-token': token},
                          json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_host_status_log_with_invalid_host_identifier(self, client, url_prefix, token, status_log):
        """
        Test-Case with payload value invalid host_identifier
        and with existing status_log and node data,
        expected output:- status is failure
        """
        payload = {
            'host_identifier': 'foo', 'start': 0, 'limit': 5, 'searchterm': 'foobar_file'
        }
        resp = client.post(url_prefix + '/hosts/status_logs', headers={'x-access-token': token},
                          json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_host_status_log_with_invalid_node_id(self, client, url_prefix, token, status_log):
        """
        Test-Case with payload value invalid node_id
        and with existing status_log and node data,
        expected output:- status is failure
        """
        payload = {
            'node_id': 5, 'start': 0, 'limit': 5, 'searchterm': 'foobar_file'
        }
        resp = client.post(url_prefix + '/hosts/status_logs', headers={'x-access-token': token},
                          json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_host_status_log_with_all_valid_payload_except_node_id(self, client, url_prefix, token, status_log):
        """
        Test-Case with all payload value except node_id along with node_id
        and with existing status_log and node data,
        expected output:- status is success, and
        count and total_count of status log i.e., 1 and status log data
        """
        payload = {
            'host_identifier': 'foobar', 'start': 0, 'limit': 4, 'searchterm': 'foobar_file'
        }
        resp = client.post(url_prefix + '/hosts/status_logs', headers={'x-access-token': token},
                          json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        qs = hosts_dao.get_node_by_host_identifier('foobar')
        assert response_dict['data']['results'] == marshal(hosts_dao.get_status_logs_of_a_node(qs, '').offset(
            0).limit(5).all(), host_wrappers.node_status_log_wrapper)

    def test_get_host_status_log_with_all_valid_payload_except_host_identifier(self, client, url_prefix, token, status_log):
        """
        Test-Case with all payload value except host_identifier along with host_identifier
        and with existing status_log and node data,
        expected output:- status is success, and
        count and total_count of status log i.e., 1 and status log data
        """
        payload = {
            'node_id': 1, 'start': 0, 'limit': 4, 'searchterm': 'foobar_file'
        }
        resp = client.post(url_prefix + '/hosts/status_logs', headers={'x-access-token': token},
                          json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        qs = hosts_dao.getNodeById(1)
        assert response_dict['data']['results'] == marshal(hosts_dao.get_status_logs_of_a_node(qs, '').offset(
            0).limit(5).all(), host_wrappers.node_status_log_wrapper)

    def test_get_hosts_status_log_with_all_valid_payload_except_start(self, client, url_prefix, token, status_log):
        """
        Test-case with all valid payload except start value
        along with existing status_log and node data,
        expected output:- status is success, and
        count and total_count of status log i.e., 1 and status log data
        """
        payload = {'host_identifier': 'foobar', 'node_id': 1, 'searchterm': 'foobar_file', 'limit':5}
        resp = client.post(url_prefix + '/hosts/status_logs', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        qs = hosts_dao.get_node_by_host_identifier('foobar')
        assert response_dict['data']['results'] == marshal(hosts_dao.get_status_logs_of_a_node(qs, '').offset(
            None).limit(5).all(), host_wrappers.node_status_log_wrapper)

    def test_get_hosts_status_log_with_all_valid_payload_except_limit(self, client, url_prefix, token, status_log):
        """
        Test-case with all valid payload except limit value
        along with existing status_log and node data,
        expected output:- status is success, and
        count and total_count of status log i.e., 1 and status log data
        """
        payload = {'host_identifier': 'foobar', 'node_id': 1, 'searchterm': 'foobar_file', 'start': 0}
        resp = client.post(url_prefix + '/hosts/status_logs', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        qs = hosts_dao.get_node_by_host_identifier('foobar')
        assert response_dict['data']['results'] == marshal(hosts_dao.get_status_logs_of_a_node(qs, '').offset(
            0).limit(None).all(), host_wrappers.node_status_log_wrapper)

    def test_get_hosts_status_log_without_pagination(self, client, url_prefix, token, status_log):
        """
        Test-case without pagination but with host_identifier/node_id
        along with existing status_log and node data,
        expected output:- status is success, and
        count and total_count of status log i.e., 1 and status log data
        """
        payload = {'host_identifier': 'foobar', 'node_id': 1, 'searchterm': 'foobar_file'}
        resp = client.post(url_prefix + '/hosts/status_logs', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        qs = hosts_dao.get_node_by_host_identifier('foobar')
        assert response_dict['data']['results'] == marshal(hosts_dao.get_status_logs_of_a_node(qs, '').offset(
            None).limit(None).all(), host_wrappers.node_status_log_wrapper)

    def test_get_hosts_status_log_with_pagination(self, client, url_prefix, token, status_log):
        """
        Test-case with pagination but with host_identifier/node_id
        along with existing node data,
        expected output:- status is success, and
        count and total_count of status log i.e., 1 and status log data
        """
        self.payload['node_id'] = 1
        self.payload['host_identifier'] = 'foobar'
        self.payload['start'] = 0
        self.payload['limit'] = 5
        self.payload['searchterm'] = 'foobar_file'
        resp = client.post(url_prefix + '/hosts/status_logs', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        qs = hosts_dao.get_node_by_host_identifier('foobar')
        assert response_dict['data']['results'] == marshal(hosts_dao.get_status_logs_of_a_node(qs, '').offset(
            0).limit(5).all(), host_wrappers.node_status_log_wrapper)


class TestHostAdditionalConfig:
    """
    Test-case inside this block where both of the payloads values are used,
    both payloads values are the optional payload values, and
    host_identifier is of str type and node_id is of int type
    so if the payload value of host_identiifer is passed other than str,
    and payload value of node_id is passed other than int
    then it will return 400 i.e., bad request
    """
    payload = {'host_identifier': None, 'node_id': None}

    def test_host_config_without_payload(self, client, url_prefix, token):
        """
        Test-case without payload
        and without existing node, queries, packs and tags data,
        expected output:- status is failure
        """
        resp = client.post(url_prefix + '/hosts/additional_config', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_host_config_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload is empty dictionary,
        and without existing node, queries, packs and tags data,
        expected output:- status is failure
        """
        resp = client.post(url_prefix + '/hosts/additional_config', headers={'x-access-token': token}, json={})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_host_config_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with payload values are none,
        and without existing node, queries, packs and tags data,
        expected output:- status is failure
        """
        resp = client.post(url_prefix + '/hosts/additional_config', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_host_config_with_payload_value_empty_str(self, client, url_prefix, token):
        """
        Test-case with payload values are empty string,
        and without existing node, queries, packs and tags data,
        expected output:- status_code is 400
        """
        self.payload['host_identifier'] = ''
        self.payload['node_id'] = ''
        resp = client.post(url_prefix + '/hosts/additional_config', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_host_config_with_invalid_type_of_payload_value(self, client, url_prefix, token):
        """
        Test-case with invalid type of payload values,
        and without existing node, queries, packs and tags data,
        expected output:- status_code is 400
        """
        self.payload['host_identifier'] = [234]
        self.payload['node_id'] = ['foo']
        resp = client.post(url_prefix + '/hosts/additional_config', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_host_config_with_invalid_method(self, client, url_prefix, token, node):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.put(url_prefix + '/hosts/additional_config', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_host_config_with_invalid_host_identifier_and_node_id(self, client, url_prefix, token, node):
        """
        Test-case with existing only node data and invalid host_identifier
        which is passing through url,
        expected output:- status is failure
        """
        self.payload['host_identifier'] = 'foo'
        self.payload['node_id'] = 5
        resp = client.post(url_prefix + '/hosts/additional_config', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_host_config_with_invalid_node_id(self, client, url_prefix, token, node):
        """
        Test-case with existing only node data and invalid payload value of node_id,
        expected output:- status is failure
        """
        self.payload['node_id'] = 5
        resp = client.post(url_prefix + '/hosts/additional_config', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_host_config_with_valid_host_identifier(self, client, url_prefix, token, node):
        """
        Test-case with existing only node data and with valid host_identifier,
        expected output:- status is success, and
        response_data in the form of dictionary(with key_values are packs, queries, and tags)
        """
        payload = {'host_identifier': 'foobar'}
        resp = client.post(url_prefix + '/hosts/additional_config', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['queries'] == []
        assert response_dict['data']['packs'] == []
        assert response_dict['data']['tags'] == []

    def test_host_config_with_valid_node_id(self, client, url_prefix, token, node):
        """
        Test-case without existing only node data and with valid node_id,
        expected output:- status is success, and
        response_data in the form of dictionary(with key_values are packs, queries, and tags)
        """
        payload = {'node_id': 1}
        resp = client.post(url_prefix + '/hosts/additional_config', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['queries'] == []
        assert response_dict['data']['packs'] == []
        assert response_dict['data']['tags'] == []

    def test_host_config_with_all_valid_payload(self, client, url_prefix, token, node):
        """
        Test-case without existing only node data and with all valid payload,
        expected output:- status is success, and
        response_data in the form of dictionary(with key_values are packs, queries, and tags)
        """
        self.payload['node_id'] = 1
        self.payload['host_identifier'] = 'foobar'
        resp = client.post(url_prefix + '/hosts/additional_config', headers={'x-access-token': token},
                           json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['queries'] == []
        assert response_dict['data']['packs'] == []
        assert response_dict['data']['tags'] == []

    def test_hosts_config_with_valid_host_identifier(self, client, url_prefix, token, node, queries, packs, tag):
        """
        Test-case with existing node, queries, packs and tag data and with valid host_identifier,
        expected output:- status is success, and
        response_data in the form of dictionary(with key_values are packs, queries, and tags)
        """
        payload = {'host_identifier': 'foobar'}
        n = hosts_dao.get_node_by_host_identifier('foobar')
        p = packs_dao.get_pack_by_name('pytest_pack')
        q = queries_dao.get_query_by_name('test_query')
        t = tags_dao.get_tag_by_value('test')
        p.queries.append(q)
        p.tags.append(t)
        q.tags.append(t)
        n.tags.append(t)
        resp = client.post(url_prefix + '/hosts/additional_config', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        nod = hosts_dao.get_node_by_host_identifier('foobar')
        data = assemble_additional_configuration(nod)
        assert response_dict['data']['queries'] == data['queries']
        assert response_dict['data']['packs'] == data['packs']
        assert response_dict['data']['tags'] == data['tags']

    def test_hosts_config_with_valid_node_id(self, client, url_prefix, token, node, queries, packs, tag):
        """
        Test-case without existing node, queries, packs and tag data and with valid node_id,
        expected output:- status is success, and
        response_data in the form of dictionary(with key_values are packs, queries, and tags)
        """
        payload = {'node_id': 1}
        n = hosts_dao.getNodeById(1)
        p = packs_dao.get_pack_by_name('pytest_pack')
        q = queries_dao.get_query_by_name('test_query')
        t = tags_dao.get_tag_by_value('test')
        p.queries.append(q)
        p.tags.append(t)
        q.tags.append(t)
        n.tags.append(t)
        resp = client.post(url_prefix + '/hosts/additional_config', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        nod = hosts_dao.getNodeById(1)
        data = assemble_additional_configuration(nod)
        assert response_dict['data']['queries'] == data['queries']
        assert response_dict['data']['packs'] == data['packs']
        assert response_dict['data']['tags'] == data['tags']

    def test_hosts_config_with_all_valid_payload(self, client, url_prefix, token, node, queries, packs, tag):
        """
        Test-case without existing node, queries, packs and tag data and with all valid payload,
        expected output:- status is success, and
        response_data in the form of dictionary(with key_values are packs, queries, and tags)
        """
        self.payload['node_id'] = 1
        self.payload['host_identifier'] = 'foobar'
        n = hosts_dao.getNodeById(1)
        p = packs_dao.get_pack_by_name('pytest_pack')
        q = queries_dao.get_query_by_name('test_query')
        t = tags_dao.get_tag_by_value('test')
        p.queries.append(q)
        p.tags.append(t)
        q.tags.append(t)
        n.tags.append(t)
        resp = client.post(url_prefix + '/hosts/additional_config', headers={'x-access-token': token},
                           json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        nod = hosts_dao.getNodeById(1)
        data = assemble_additional_configuration(nod)
        assert response_dict['data']['queries'] == data['queries']
        assert response_dict['data']['packs'] == data['packs']
        assert response_dict['data']['tags'] == data['tags']


class TestHostFullConfig:
    """
    Test-case inside this block where both of the payloads values are used,
    both payloads values are the optional payload values, and
    host_identifier is of str type and node_id is of int type
    so if the payload value of host_identiifer is passed other than str,
    and payload value of node_id is passed other than int
    then it will return 400 i.e., bad request
    """
    payload = {'host_identifier': None, 'node_id': None}

    def test_host_config_without_payload(self, client, url_prefix, token):
        """
        Test-case without payload
        and without existing node, queries, packs and tags data,
        expected output:- status is failure
        """
        resp = client.post(url_prefix + '/hosts/config', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_host_config_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload is empty dictionary,
        and without existing node, queries, packs and tags data,
        expected output:- status is failure
        """
        resp = client.post(url_prefix + '/hosts/config', headers={'x-access-token': token}, json={})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_host_config_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with payload values are none,
        and without existing node, queries, packs and tags data,
        expected output:- status is failure
        """
        resp = client.post(url_prefix + '/hosts/config', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_host_config_with_payload_value_empty_str(self, client, url_prefix, token):
        """
        Test-case with payload values are empty string,
        and without existing node, queries, packs and tags data,
        expected output:- status_code is 400
        """
        self.payload['host_identifier'] = ''
        self.payload['node_id'] = ''
        resp = client.post(url_prefix + '/hosts/config', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_host_config_with_invalid_type_of_payload_value(self, client, url_prefix, token):
        """
        Test-case with invalid type of payload values,
        and without existing node, queries, packs and tags data,
        expected output:- status_code is 400
        """
        self.payload['host_identifier'] = [234]
        self.payload['node_id'] = ['foo']
        resp = client.post(url_prefix + '/hosts/config', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_host_config_with_invalid_method(self, client, url_prefix, token, node):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.put(url_prefix + '/hosts/config', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_host_config_with_invalid_host_identifier_and_node_id(self, client, url_prefix, token, node):
        """
        Test-case with existing only node data and invalid host_identifier
        which is passing through url,
        expected output:- status is failure
        """
        self.payload['host_identifier'] = 'foo'
        self.payload['node_id'] = 5
        resp = client.post(url_prefix + '/hosts/config', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_host_config_with_invalid_node_id(self, client, url_prefix, token, node):
        """
        Test-case with existing only node data and invalid payload value of node_id,
        expected output:- status is failure
        """
        self.payload['node_id'] = 5
        resp = client.post(url_prefix + '/hosts/config', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_host_config_with_valid_host_identifier(self, client, url_prefix, token, node):
        """
        Test-case with existing only node data and with valid host_identifier,
        expected output:- status is success, and
        response_data in the form of dictionary(with key_values
        are packs, queries, options, file_paths and filters)
        """
        payload = {'host_identifier': 'foobar'}
        resp = client.post(url_prefix + '/hosts/config', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['queries'] == {}
        assert response_dict['data']['packs'] == []
        assert response_dict['data']['file_paths'] == {}
        assert response_dict['data']['filters'] is None
        nod = hosts_dao.get_node_by_host_identifier('foobar')
        assert response_dict['data']['options'] == assemble_options(nod)

    def test_host_config_with_valid_node_id(self, client, url_prefix, token, node):
        """
        Test-case without existing only node data and with valid node_id,
        expected output:- status is success, and
        response_data in the form of dictionary(with key_values
        are packs, queries, options, file_paths and filters)
        """
        payload = {'node_id': 1}
        resp = client.post(url_prefix + '/hosts/config', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['queries'] == {}
        assert response_dict['data']['packs'] == []
        assert response_dict['data']['file_paths'] == {}
        assert response_dict['data']['filters'] is None
        nod = hosts_dao.get_node_by_host_identifier('foobar')
        assert response_dict['data']['options'] == assemble_options(nod)

    def test_host_config_with_all_valid_payload(self, client, url_prefix, token, node):
        """
        Test-case without existing only node data and with all valid payload,
        expected output:- status is success, and
        response_data in the form of dictionary(with key_values
        are packs, queries, options, file_paths and filters)
        """
        self.payload['node_id'] = 1
        self.payload['host_identifier'] = 'foobar'
        resp = client.post(url_prefix + '/hosts/config', headers={'x-access-token': token},
                           json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['queries'] == {}
        assert response_dict['data']['packs'] == []
        assert response_dict['data']['file_paths'] == {}
        assert response_dict['data']['filters'] is None
        nod = hosts_dao.get_node_by_host_identifier('foobar')
        assert response_dict['data']['options'] == assemble_options(nod)

    def test_hosts_config_with_valid_host_identifier(self, client, url_prefix, token, node, queries, packs, tag, default_filter):
        """
        Test-case with existing node, queries, packs and tag data and with valid host_identifier,
        expected output:- status is success, and
        response_data in the form of dictionary(with key_values
        are packs, queries, options, file_paths and filters)
        """
        payload = {'host_identifier': 'foobar'}
        n = hosts_dao.get_node_by_host_identifier('foobar')
        p = packs_dao.get_pack_by_name('pytest_pack')
        q = queries_dao.get_query_by_name('test_query')
        t = tags_dao.get_tag_by_value('test')
        p.queries.append(q)
        p.tags.append(t)
        q.tags.append(t)
        n.tags.append(t)
        resp = client.post(url_prefix + '/hosts/config', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        nod = hosts_dao.get_node_by_host_identifier('foobar')
        data = assemble_configuration(nod)
        assert response_dict['data']['queries'] == data['queries']
        assert response_dict['data']['packs'] == data['packs']
        assert response_dict['data']['options'] == data['options']
        assert response_dict['data']['file_paths'] == data['file_paths']
        assert response_dict['data']['filters'] == data['filters']

    def test_hosts_config_with_valid_node_id(self, client, url_prefix, token, node, queries, packs, tag, default_filter):
        """
        Test-case without existing node, queries, packs and tag data and with valid node_id,
        expected output:- status is success, and
        response_data in the form of dictionary(with key_values
        are packs, queries, options, file_paths and filters)
        """
        payload = {'node_id': 1}
        n = hosts_dao.getNodeById(1)
        p = packs_dao.get_pack_by_name('pytest_pack')
        q = queries_dao.get_query_by_name('test_query')
        t = tags_dao.get_tag_by_value('test')
        p.queries.append(q)
        p.tags.append(t)
        q.tags.append(t)
        n.tags.append(t)
        resp = client.post(url_prefix + '/hosts/config', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        nod = hosts_dao.getNodeById(1)
        data = assemble_configuration(nod)
        assert response_dict['data']['queries'] == data['queries']
        assert response_dict['data']['packs'] == data['packs']
        assert response_dict['data']['options'] == data['options']
        assert response_dict['data']['file_paths'] == data['file_paths']
        assert response_dict['data']['filters'] == data['filters']

    def test_hosts_config_with_all_valid_payload(self, client, url_prefix, token, node, default_filter, queries, packs, tag):
        """
        Test-case without existing node, queries, packs and tag data and with all valid payload,
        expected output:- status is success, and
        response_data in the form of dictionary(with key_values
        are packs, queries, options, file_paths and filters)
        """
        self.payload['node_id'] = 1
        self.payload['host_identifier'] = 'foobar'
        n = hosts_dao.getNodeById(1)
        p = packs_dao.get_pack_by_name('pytest_pack')
        q = queries_dao.get_query_by_name('test_query')
        t = tags_dao.get_tag_by_value('test')
        p.queries.append(q)
        p.tags.append(t)
        q.tags.append(t)
        n.tags.append(t)
        resp = client.post(url_prefix + '/hosts/config', headers={'x-access-token': token},
                           json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        nod = hosts_dao.getNodeById(1)
        data = assemble_configuration(nod)
        assert response_dict['data']['queries'] == data['queries']
        assert response_dict['data']['packs'] == data['packs']
        assert response_dict['data']['options'] == data['options']
        assert response_dict['data']['file_paths'] == data['file_paths']
        assert response_dict['data']['filters'] == data['filters']


class TestRecentActivityCount:
    """
       Test-case inside this block where both of the payloads values are used,
       both payloads values are the optional payload values, and
       host_identifier is of str type and node_id is of int type
       so if the payload value of host_identiifer is passed other than str,
       and payload value of node_id is passed other than int
       then it will return 400 i.e., bad request
       """
    payload = {'host_identifier': None, 'node_id': None}

    def test_recent_activity_without_payload(self, client, url_prefix, token):
        """
        Test-case without payload
        and without existing node and node_query_count data,
        expected output:- status is failure
        """
        resp = client.post(url_prefix + '/hosts/recent_activity/count', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_recent_activity_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload is empty dictionary,
        and without existing node and node_query_count data,
        expected output:- status is failure
        """
        resp = client.post(url_prefix + '/hosts/recent_activity/count', headers={'x-access-token': token}, json={})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_recent_activity_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with payload values are none,
        and without existing node and node_query_count data,
        expected output:- status is failure
        """
        resp = client.post(url_prefix + '/hosts/recent_activity/count', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_recent_activity_with_payload_value_empty_str(self, client, url_prefix, token):
        """
        Test-case with payload values are empty string,
        and without existing node and node_query_count data,
        expected output:- status_code is 400
        """
        self.payload['host_identifier'] = ''
        self.payload['node_id'] = ''
        resp = client.post(url_prefix + '/hosts/recent_activity/count', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_recent_activity_with_invalid_type_of_payload_value(self, client, url_prefix, token):
        """
        Test-case with invalid type of payload values,
        and without existing node and node_query_count data,
        expected output:- status_code is 400
        """
        self.payload['host_identifier'] = [234]
        self.payload['node_id'] = ['foo']
        resp = client.post(url_prefix + '/hosts/recent_activity/count', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_recent_activity_with_invalid_method(self, client, url_prefix, token, node):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.put(url_prefix + '/hosts/recent_activity/count', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_recent_activity_with_invalid_host_identifier_and_node_id(self, client, url_prefix, token, node):
        """
        Test-case with existing only node data and invalid host_identifier
        which is passing through url,
        expected output:- status is failure
        """
        self.payload['host_identifier'] = 'foo'
        self.payload['node_id'] = 5
        resp = client.post(url_prefix + '/hosts/recent_activity/count', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_recent_activity_with_invalid_node_id(self, client, url_prefix, token, node):
        """
        Test-case with existing only node data and invalid payload value of node_id,
        expected output:- status is failure
        """
        self.payload['node_id'] = 5
        resp = client.post(url_prefix + '/hosts/recent_activity/count', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_recent_activity_with_valid_host_identifier(self, client, url_prefix, token, node):
        """
        Test-case with existing only node data and with valid host_identifier,
        expected output:- status is success, and
        response_data is empty_list in this case
        """
        payload = {'host_identifier': 'foobar'}
        resp = client.post(url_prefix + '/hosts/recent_activity/count', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == []

    def test_recent_activity_with_valid_node_id(self, client, url_prefix, token, node):
        """
        Test-case without existing only node data and with valid node_id,
        expected output:- status is success, and
        response_data is empty_list in this case
        """
        payload = {'node_id': 1}
        resp = client.post(url_prefix + '/hosts/recent_activity/count', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == []

    def test_recent_activity_with_all_valid_payload(self, client, url_prefix, token, node):
        """
        Test-case without existing only node data and with all valid payload,
        expected output:- status is success, and
        response_data is empty_list in this case
        """
        self.payload['node_id'] = 1
        self.payload['host_identifier'] = 'foobar'
        resp = client.post(url_prefix + '/hosts/recent_activity/count', headers={'x-access-token': token},
                           json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == []

    def test_recents_activity_with_valid_host_identifier(self, client, url_prefix, token, node_query_count):
        """
        Test-case with existing node and node_query_count data and with valid host_identifier,
        expected output:- status is success, and
        response_data is name and count i.e., kernel_modules and 14
        respectively in this case
        """
        payload = {'host_identifier': 'foobar'}
        resp = client.post(url_prefix + '/hosts/recent_activity/count', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'][0]['name'] == 'kernel_modules'
        assert response_dict['data'][0]['count'] == 14

    def test_recents_activity_with_valid_node_id(self, client, url_prefix, token, node_query_count):
        """
        Test-case without existing node and node_query_count data and with valid node_id,
        expected output:- status is success, and
        response_data is name and count i.e., kernel_modules and 14
        respectively in this case
        """
        payload = {'node_id': 1}
        resp = client.post(url_prefix + '/hosts/recent_activity/count', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'][0]['name'] == 'kernel_modules'
        assert response_dict['data'][0]['count'] == 14

    def test_recents_activity_with_all_valid_payload(self, client, url_prefix, token, node_query_count):
        """
        Test-case without existing node and node_query_count data and with all valid payload,
        expected output:- status is success, and
        response_data is name and count i.e., kernel_modules and 14
        respectively in this case
        """
        self.payload['node_id'] = 1
        self.payload['host_identifier'] = 'foobar'
        resp = client.post(url_prefix + '/hosts/recent_activity/count', headers={'x-access-token': token},
                           json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'][0]['name'] == 'kernel_modules'
        assert response_dict['data'][0]['count'] == 14


class TestRecentActivityResults:
    """
    wherever we are using any of these payloads,
    query_name should be a string that is name of the query like, process_events,
    node_id, start and limit should be integer and searchterm should be a string value,
    and out of these six value of payloads only query_name is compulsory payload value
    and remaining all values are optional payload values, so if we not compulsory
     payload values or if the value is none or value type other than the specified type,
    then it will give bad request i.e., 400
    """
    payload = {
        'host_identifier': None, 'node_id': None, 'query_name': None,
        'start': None, 'limit': None, 'searchterm': None
    }

    def test_recent_activity_results_without_payload(self, client, url_prefix, token):
        """
        Test-Case without payload and without existing node and result_log data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/hosts/recent_activity', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_recent_activity_results_with_empty_dict_payload(self, client, url_prefix, token):
        """
        Test-Case with empty dictionary payloads,
        and without existing node and result_log data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/hosts/recent_activity', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_recent_activity_results_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-Case with payloads values are None,
        and without existing node and result_log data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/hosts/recent_activity', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_recent_activity_results_with_only_payload_compulsory_value(self, client, url_prefix, token):
        """
        Test-Case with only compulsory payloads value,
        and without existing node and result_log data,
        expected output:- status is failure
        """
        self.payload['query_name'] = 'win_file_events'
        self.payload['start'] = 0
        self.payload['limit'] = 5
        resp = client.post(url_prefix + '/hosts/recent_activity', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_recent_activity_results_with_all_payload_value_except_node_id(self, client, url_prefix, token):
        """
        Test-Case with all payloads value except node_id,
        and without existing node and result_log data,
        expected output:- status is failure
        """
        payload = {
            'query_name': 'win_file_events', 'host_identifier': 'foobar',
            'start': 0, 'limit': 5, 'searchterm': 'foobar'
        }
        resp = client.post(url_prefix + '/hosts/recent_activity', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_recent_activity_results_with_all_payload_value_except_host_identifier(self, client, url_prefix, token):
        """
        Test-Case with all payloads value except host_identifier,
        and without existing node and result_log data,
        expected output:- status is success, and
        resultant_data is dict of key_values are count, total_count and results
        """
        payload = {
            'query_name': 'win_file_events', 'node_id': 1,
            'start': 0, 'limit': 5, 'searchterm': 'foobar'
        }
        resp = client.post(url_prefix + '/hosts/recent_activity', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == {'count': 0, 'total_count': 0, 'results': []}

    def test_recent_activity_results_with_all_payload_value(self, client, url_prefix, token):
        """
        Test-Case with all payloads value,
        and without existing node and result_log data,
        expected output:- status is failure
        """
        self.payload['query_name'] = 'win_file_events'
        self.payload['host_identifier'] = 'foobar'
        self.payload['node_id'] = 1
        self.payload['start'] = 0
        self.payload['limit'] = 5
        self.payload['searchterm'] = 'foobar'
        resp = client.post(url_prefix + '/hosts/recent_activity', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_recent_activity_results_with_invalid_method(self, client, url_prefix, token, result_log):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.put(url_prefix + '/hosts/recent_activity', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_recent_activity_results_with_compulsory_payload(self, client, url_prefix, token, result_log):
        """
        Test-Case with only payloads of compulsory value,
        and with existing node and result_log data,
        expected output:- status is failure
        """
        payload = {}
        payload['query_name'] = 'win_file_events'
        payload['start'] = 0
        payload['limit'] = 5
        resp = client.post(url_prefix + '/hosts/recent_activity', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_recents_activity_results_with_all_payload_value_except_node_id(self, client, url_prefix, token, result_log):
        """
        Test-Case with all payloads value except node_id,
        and with existing node and result_log data,
        expected output:- status is success, and
        count and total_count of recent_activity data as well as
        recent_activity data
        """
        payload = {
            'query_name': 'win_file_events', 'host_identifier': 'foobar',
            'start': 0, 'limit': 5, 'searchterm': 'foobar'
        }
        resp = client.post(url_prefix + '/hosts/recent_activity', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        node = hosts_dao.get_node_by_host_identifier('foobar')
        data = recent_activity_data(node.id, 'win_file_events', 0, 5)
        assert response_dict['data']['count'] == data['count']
        assert response_dict['data']['total_count'] == data['total_count']
        assert response_dict['data']['results'] == data['results']

    def test_recents_activity_results_with_all_payload_value_except_host_identifier(self, client, url_prefix, token, result_log):
        """
        Test-Case with all payloads value except host_identifier,
        and without existing node and result_log data,
        expected output:- status is success, and
        count and total_count of recent_activity data as well as
        recent_activity data
        """
        payload = {
            'query_name': 'win_file_events', 'node_id': 1,
            'start': 0, 'limit': 5, 'searchterm': 'foobar'
        }
        resp = client.post(url_prefix + '/hosts/recent_activity', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        data = recent_activity_data(1, 'win_file_events', 0, 5)
        assert response_dict['data']['count'] == data['count']
        assert response_dict['data']['total_count'] == data['total_count']
        assert response_dict['data']['results'] == data['results']

    def test_recent_activity_results_with_all_payload(self, client, url_prefix, token, result_log):
        """
        Test-Case with all payloads value and with existing result_log data,
        and host_identifier/node_id which is passing through url
        expected output:- status is success, and
        count and total_count of recent_activity data as well as
        recent_activity data
        """
        payload = {}
        payload['query_name'] = 'win_file_events'
        payload['start'] = 0
        payload['limit'] = 5
        payload['searchterm'] = 'foobar'
        payload['host_identifier'] = 'foobar'
        payload['node_id'] = 1
        resp = client.post(url_prefix + '/hosts/recent_activity', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        node = hosts_dao.get_node_by_host_identifier('foobar')
        data = recent_activity_data(node.id, 'win_file_events', 0, 5)
        assert response_dict['data']['count'] == data['count']
        assert response_dict['data']['total_count'] == data['total_count']
        assert response_dict['data']['results'] == data['results']


class TestPostTagsOfNode:
    """
    all the test-case inside this block where we used this payload value,
    this is compulsory payload value of str type, so if value is not passes,
    or passed value type is other than str then it will return 400, i.e., bad request
    """
    payload = {'tag': None}

    def test_post_tags_of_node_without_payload(self, client, url_prefix, token):
        """
        Test-case without payloads and without existing node and tag data,
        host_identifier/node_id is passing through url,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/hosts/foobar/tags', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_post_tags_of_node_with_empty_dict_of_payload(self, client, url_prefix, token):
        """
        Test-case with empty dictionary of payloads and without existing node and tag data,
        host_identifier/node_id is passing through url,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/hosts/1/tags', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_post_tags_of_node_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with none value of payloads and without existing node and tag data,
        host_identifier/node_id is passing through url,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/hosts/foobar/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_post_tags_of_node_with_payload_value(self, client, url_prefix, token):
        """
        Test-case with value of payloads and without existing node and tag data,
        host_identifier/node_id is passing through url,
        expected output:- status is failure
        """
        self.payload['tag'] = 'test'
        resp = client.post(url_prefix + '/hosts/foobar/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_post_tags_of_node_with_invalid_method(self, client, url_prefix, token, node, tag):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.put(url_prefix + '/hosts/foobar/tags', headers={'x-access-token': token},
                           data=self.payload)
        assert resp.status_code == 405

    def test_post_tags_of_node_with_tag_value_empty_str(self, client, url_prefix, token, node, tag):
        """
        Test-case with existing node and tag data and empty str of tag value with
        host_identifier/node_id which is passing through url,
        expected output:- status is failure
        """
        self.payload['tag'] = ''
        resp = client.post(url_prefix + '/hosts/foobar/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_post_tags_of_node_with_tag_invalid_value(self, client, url_prefix, token, node, tag):
        """
        Test-case with existing node and tag data and invalid value of tag value with
        host_identifier/node_id which is passing through url,
        expected output:- status is failure
        """
        self.payload['tag'] = ''
        resp = client.post(url_prefix + '/hosts/foobar/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_post_tags_of_node_with_existing_tag(self, client, url_prefix, token, node, tag):
        """
        Test-case with existing node and tag data with
        host_identifier/node_id which is passing through url,
        expected output:- status is success
        """
        self.payload['tag'] = 'test'
        resp = client.post(url_prefix + '/hosts/foobar/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'

    def test_post_tags_of_node_without_existing_tag(self, client, url_prefix, token, node, tag):
        """
        Test-case with existing node and tag data with
        host_identifier/node_id which is passing through url,
        expected output:- status is success
        """
        self.payload['tag'] = 'test123'
        resp = client.post(url_prefix + '/hosts/foobar/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'


class TestGETListTagsOfNode:

    def test_get_list_of_tags_with_host_identifier_and_without_data(self, client, url_prefix, token):
        """
        Test-case with host_identifier/node_id passing through url
        without existing node and tag data,
        expected output:- status is failure
        """
        resp = client.get(url_prefix + '/hosts/foobar/tags', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_list_of_tags_with_invalid_method(self, client, url_prefix, token):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.put(url_prefix + '/hosts/foobar/tags', headers={'x-access-token': token})
        assert resp.status_code == 405

    def test_get_list_of_tags_with_invalid_node_id_or_host_identifier(self, client, url_prefix, token, node, tag):
        """
        Test-case with invalid host_identifier/node_id passing through url
        with existing node and tag data,
        expected output:- status is failure
        """
        resp = client.get(url_prefix + '/hosts/foobar1/tags', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_list_of_tags_with_valid_node_id_or_host_identifier(self, client, url_prefix, token, node, tag):
        """
        Test-case with invalid host_identifier/node_id passing through url
        with existing node and tag data,
        expected output:- status is success
        """
        resp = client.get(url_prefix + '/hosts/foobar/tags', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        node = hosts_dao.get_node_by_host_identifier('foobar')
        data=[tag.value for tag in node.tags]
        assert response_dict['data'] == data


class TestDeleteListTagsOfNode:
    """
    all the test-case inside this block where we used this payload,
    payload value should be string type and it's compulsory to give payloads,
    otherwise it will return input payload validation failes i.e., status_code 400
    """
    payload = {'tag': None}

    def test_delete_tag_of_node_without_payload(self, client, url_prefix, token):
        """
        Test-case without payload, existing node and tag data and
        host_identifier/node_id is passing through url,
        expected output:- status code is 400
        """
        resp = client.delete(url_prefix + '/hosts/foobar/tags', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_delete_tags_of_node_with_empty_dict_of_payload(self, client, url_prefix, token):
        """
        Test-case with empty dictionary of payloads and without existing node data,
        host_identifier/node_id is passing through url,
        expected output:- status_code is 400
        """
        resp = client.delete(url_prefix + '/hosts/1/tags', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_delete_tags_of_node_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with none value of payloads and without existing node data,
        host_identifier/node_id is passing through url,
        expected output:- status_code is 400
        """
        resp = client.delete(url_prefix + '/hosts/foobar/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_delete_tags_of_node_with_payload_value(self, client, url_prefix, token):
        """
        Test-case with value of payloads and without existing node data,
        host_identifier/node_id is passing through url,
        expected output:- status is failure
        """
        self.payload['tag'] = 'test'
        resp = client.delete(url_prefix + '/hosts/1/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_post_tags_of_node_with_invalid_method(self, client, url_prefix, token):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.put(url_prefix + '/hosts/foobar/tags', headers={'x-access-token': token},
                           data=self.payload)
        assert resp.status_code == 405

    def test_delete_tag_of_node_with_invalid_node_id_or_host_identifier(self, client, url_prefix, token, tag, node):
        """
       Test-case with existing node and tag data and tag value with
       host_identifier/node_id which is passing through url,
       expected output:- status is failure
       """
        self.payload['tag'] = 'test'
        resp = client.delete(url_prefix + '/hosts/1/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_delete_tag_of_node_with_invalid_tag_value(self, client, url_prefix, token, tag, node):
        """
       Test-case with existing node and tag data and invalid tag value with
       host_identifier/node_id which is passing through url,
       expected output:- status is failure
       """
        self.payload['tag'] = 'foo'
        resp = client.delete(url_prefix + '/hosts/1/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_delete_tag_of_node_with_valid_tag_value(self, client, url_prefix, token, tag, node):
        """
       Test-case with existing node and tag data and valid tag value with
       host_identifier/node_id which is passing through url,
       expected output:- status is success
       """
        self.payload['tag'] = 'test'
        existing_tag = Tag.query.filter(Tag.value == 'test').first()
        existing_node = hosts_dao.getNodeById(1)
        existing_node.tags.append(existing_tag)
        resp = client.delete(url_prefix + '/hosts/1/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert [tag.value for tag in node.tags] == []


class TestExportNodeSearchQueryCSV:
    """
    Test-case inside this block where these payloads are used,
    only query_name is compulsory payload value of string type
    remainings all values are optional payload values, conditions
    is of dict type, host_identifier is of str type, and node_id is of int type
    so if compulsory value like query_name is not passed or other payload value type other
    than specified type of values of payload, so it will return 400 i.e., bad request
    """
    payload = {'conditions': None, 'host_identifier': None, 'query_name': None, 'node_id': None}

    def test_export_node_search_query_csv_without_payloads(self, client, url_prefix, token):
        """
        Test-case without payloads value and without existing result_log and node data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/hosts/search/export', headers={'x-access-token': token},
                               json=self.payload)
        assert resp.status_code == 400

    def test_export_node_search_query_csv_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload is empty dictionary value and without
        existing result_log and node data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/hosts/search/export', headers={'x-access-token': token},
                               json=self.payload)
        assert resp.status_code == 400

    def test_export_node_search_query_csv_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with payload values are none and without existing result_log and node data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/hosts/search/export', headers={'x-access-token': token},
                               json=self.payload)
        assert resp.status_code == 400

    def test_export_node_search_query_csv_with_compulsory_payload_value(self, client, url_prefix, token):
        """
        Test-case with compulsory payload value i.e., query_name
        and without existing result_log and node data,
        expected output:- status is failure
        """
        payload = {'query_name': 'kernel_modules'}

        resp = client.post(url_prefix + '/hosts/search/export', headers={'x-access-token': token},
                               json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_export_node_search_query_csv_with_all_payload_value(self, client, url_prefix, token):
        """
        Test-case with all payload value
        and without existing result_log and node data,
        expected output:- status is failure
        """
        payload = {'query_name': 'kernel_modules', 'conditions': {}, 'host_identifier': 'foobar', 'node_id': 1}

        resp = client.post(url_prefix + '/hosts/search/export', headers={'x-access-token': token},
                               json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_export_node_search_query_csv_with_invalid_method(self, client, url_prefix, token, result_log):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.get(url_prefix + '/hosts/search/export', headers={'x-access-token': token},
                           json=self.payload)
        assert resp.status_code == 405

    def test_export_node_search_query_csv_with_invalid_node_id(self, client, url_prefix, token, result_log):
        """
        Test-case with compulsory payload value i.e., query_name
        and with existing result_log and node data,
        expected output:- status is failure
        """
        payload = {'query_name': 'kernel_modules', 'node_id': 30}

        resp = client.post(url_prefix + '/hosts/search/export', headers={'x-access-token': token},
                               json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_export_node_search_query_csv_with_valid_node_id(self, client, url_prefix, token, result_log):
        """
        Test-case with compulsory payload value i.e., query_name
        and with existing result_log and node data,
        expected output:- status_code is 200, and
        a csv file data
        """
        payload = {'node_id': 1, 'query_name': 'kernel_modules'}

        resp = client.post(url_prefix + '/hosts/search/export', headers={'x-access-token': token},
                           json=payload)
        assert resp.status_code == 200
        assert resp.data == node_search_query_csv(1, 'kernel_modules').data

    def test_export_node_search_query_csv_with_invalid_host_identifier(self, client, url_prefix, token, result_log):
        """
        Test-case with compulsory payload value i.e., query_name
        and invalid host_identifier, and with existing result_log and node data,
        expected output:- status is failure
        """
        payload = {'query_name': 'kernel_modules', 'host_identifier': 'foo'}

        resp = client.post(url_prefix + '/hosts/search/export', headers={'x-access-token': token},
                               json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_export_node_search_query_csv_with_valid_host_identifier(self, client, url_prefix, token, result_log):
        """
        Test-case with compulsory payload value i.e., query_name
        and valid host_identifier
        and with existing result_log and node data,
        expected output:- status_code is 200, and
        resultant data of node search query csv file data
        """
        payload = {'host_identifier': 'foobar', 'query_name': 'kernel_modules'}

        resp = client.post(url_prefix + '/hosts/search/export', headers={'x-access-token': token},
                           json=payload)
        assert resp.status_code == 200
        nod = hosts_dao.get_node_by_host_identifier('foobar')
        assert resp.data == node_search_query_csv(nod.id, 'kernel_modules').data

    def test_export_node_search_query_csv_with_all_payload_values(self, client, url_prefix, token, result_log):
        """
        Test-case with all payloads value
        and with existing result_log and node data,
        expected output:- status_code is 200, and
        resultant data of node search query csv file data
        """
        payload = {'query_name': 'kernel_modules', 'conditions': {}, 'host_identifier': 'foobar', 'node_id': 1}

        resp = client.post(url_prefix + '/hosts/search/export', headers={'x-access-token': token},
                           json=payload)
        assert resp.status_code == 200
        assert resp.data == node_search_query_csv(1, 'kernel_modules', {}).data


class TestNodeRemoved:

    def test_node_removed_by_id_without_hosts_data(self, client, url_prefix, token):
        """
        Test-case with valid/invalid node_id and without existing hosts data,
        expected output:- status is failure
        """
        resp = client.delete(url_prefix + '/hosts/1/delete', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_node_removed_by_host_identifier_without_hosts_data(self, client, url_prefix, token):
        """
        Test-case with valid/invalid host_identifier and without existing hosts data,
        expected output:- status is failure
        """
        resp = client.delete(url_prefix + '/hosts/foobar/delete', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_node_removed_with_invalid_method(self, client, url_prefix, token, node):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.get(url_prefix + '/hosts/1/delete', headers={'x-access-token': token})
        assert resp.status_code == 405

    def test_node_removed_by_invalid_id_with_hosts_data(self, client, url_prefix, token, node):
        """
        Test-case with invalid node_id and with existing hosts data,
        expected output:- status is failure
        """
        resp = client.delete(url_prefix + '/hosts/5/delete', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_node_removed_by_valid_id_with_hosts_data(self, client, url_prefix, token, node):
        """
        Test-case with valid node_id and with existing hosts data,
        expected output:- status is Success
        """

        resp = client.delete(url_prefix + '/hosts/1/delete', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'Success'
        assert hosts_dao.getNodeById(1) is None

    def test_node_removed_by_invalid_host_identifier_with_hosts_data(self, client, url_prefix, token, node):
        """
        Test-case with invalid host_identifier and with existing hosts data,
        expected output:- status is failure
        """
        resp = client.delete(url_prefix + '/hosts/foo/delete', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_node_removed_by_valid_host_identifier_with_hosts_data(self, client, url_prefix, token, node):
        """
        Test-case with valid host_identifier and with existing hosts data,
        expected output:- status is Success
        """

        resp = client.delete(url_prefix + '/hosts/foobar/delete', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'Success'
        assert hosts_dao.get_node_by_host_identifier('foobar') is None


class TestNodeDisable:

    def test_node_disable_by_id_without_hosts_data(self, client, url_prefix, token):
        """
        Test-case with valid/invalid node_id and without existing hosts data,
        expected output:- status is failure
        """
        resp = client.put(url_prefix + '/hosts/1/delete', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_node_disable_by_host_identifier_without_hosts_data(self, client, url_prefix, token):
        """
        Test-case with valid/invalid host_identifier and without existing hosts data,
        expected output:- status is failure
        """
        resp = client.put(url_prefix + '/hosts/foobar/delete', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_node_disable_with_invalid_method(self, client, url_prefix, token, node):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.get(url_prefix + '/hosts/1/delete', headers={'x-access-token': token})
        assert resp.status_code == 405

    def test_node_disable_by_invalid_id_with_hosts_data(self, client, url_prefix, token, node):
        """
        Test-case with invalid node_id and with existing hosts data,
        expected output:- status is failure
        """
        resp = client.put(url_prefix + '/hosts/5/delete', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_node_disable_by_valid_id_with_hosts_data(self, client, url_prefix, token, node):
        """
        Test-case with valid node_id and with existing hosts data,
        expected output:- status is Success
        """
        resp = client.put(url_prefix + '/hosts/1/delete', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'Success'
        assert db.session.query(Node).filter(and_(Node.id == 1, Node.state == Node.ACTIVE)).first() is None
        nod = hosts_dao.getNodeById(1)
        assert nod.host_identifier == 'foobar'

    def test_node_disable_by_invalid_host_identifier_with_hosts_data(self, client, url_prefix, token, node):
        """
        Test-case with invalid host_identifier and with existing hosts data,
        expected output:- status is failure
        """
        resp = client.put(url_prefix + '/hosts/foo/delete', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_node_disable_by_valid_host_identifier_with_hosts_data(self, client, url_prefix, token, node):
        """
        Test-case with valid host_identifier and with existing hosts data,
        expected output:- status is Success
        """
        resp = client.put(url_prefix + '/hosts/foobar/delete', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'Success'
        assert db.session.query(Node).filter(and_(Node.host_identifier == 'foobar', node.state == Node.ACTIVE)).first() is None
        nod = hosts_dao.get_node_by_host_identifier('foobar')
        assert nod.host_identifier == 'foobar'


class TestNodeEnable:

    def test_node_enable_by_id_without_hosts_data(self, client, url_prefix, token):
        """
        Test-case with valid/invalid node_id and without existing hosts data,
        expected output:- status is failure
        """
        resp = client.put(url_prefix + '/hosts/1/enable', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_node_enable_by_host_identifier_without_hosts_data(self, client, url_prefix, token):
        """
        Test-case with valid/invalid host_identifier and without existing hosts data,
        expected output:- status is failure
        """
        resp = client.put(url_prefix + '/hosts/foobar/enable', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_node_enable_with_invalid_method(self, client, url_prefix, token, node):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.get(url_prefix + '/hosts/1/enable', headers={'x-access-token': token})
        assert resp.status_code == 405

    def test_node_enable_by_invalid_id_with_hosts_data(self, client, url_prefix, token, node):
        """
        Test-case with invalid node_id and with existing hosts data,
        expected output:- status is failure
        """
        resp = client.put(url_prefix + '/hosts/5/enable', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_node_enable_by_valid_id_with_hosts_data(self, client, url_prefix, token, node):
        """
        Test-case with valid node_id and with existing hosts data,
        expected output:- status is Success
        """
        n = Node.query.filter_by(id=1).first()
        n.update(state=1)
        resp = client.put(url_prefix + '/hosts/1/enable', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'Success'
        assert db.session.query(Node).filter(and_(Node.id == 1, Node.state == Node.REMOVED)).first() is None
        nod = hosts_dao.getNodeById(1)
        assert nod.host_identifier == 'foobar'

    def test_node_enable_by_invalid_host_identifier_with_hosts_data(self, client, url_prefix, token, node):
        """
        Test-case with invalid host_identifier and with existing hosts data,
        expected output:- status is failure
        """
        resp = client.put(url_prefix + '/hosts/foo/enable', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_node_enable_by_valid_host_identifier_with_hosts_data(self, client, url_prefix, token, node):
        """
        Test-case with valid host_identifier and with existing hosts data,
        expected output:- status is Success
        """
        n = Node.query.filter_by(id=1).first()
        n.update(state=1)
        resp = client.put(url_prefix + '/hosts/foobar/enable', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'Success'
        assert db.session.query(Node).filter(
            and_(Node.host_identifier == 'foobar', Node.state == Node.REMOVED)).first() is None
        nod = hosts_dao.get_node_by_host_identifier('foobar')
        assert nod.host_identifier == 'foobar'


def recent_activity_data(node_id, query_name, start, limit, searchterm=''):
    qs = hosts_dao.get_result_log_of_a_query(node_id, query_name, start, limit, searchterm)
    data = {'count': qs[0], 'total_count': qs[2], 'results': [
        {'timestamp': list_ele[1].strftime('%m/%d/%Y %H/%M/%S'), 'action': list_ele[2],
         'columns': list_ele[3]} for list_ele in qs[1]]}
    return data


def get_host_list_data(status=None, platform=None, searchterm='', enabled=True, start=None, limit=None):
    query_set = hosts_dao.get_hosts_paginated(status, platform, searchterm, enabled).offset(
        start).limit(limit).all()
    total_count = hosts_dao.get_hosts_total_count(status, platform, enabled)

    return {
        'results': [node.get_dict() for node in query_set],
        'count':hosts_dao.get_hosts_paginated(status, platform, searchterm, enabled).count(),
        'total_count':total_count
    }


def node_search_query_csv(node_id, query_name, conditions=None):
    if conditions:
        try:
            root = search_rules.parse_group(conditions)
            filter = root.run('', [], 'result_log')
        except:
            pass
        results = hosts_dao.node_result_log_search_results(filter, node_id, query_name)

    else:
        results = hosts_dao.node_result_log_results(node_id, query_name)
    if results:
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

        response = send_file(
            bio,
            mimetype='text/csv',
            as_attachment=True,
            attachment_filename=query_name + '_' + str(node_id) + str(dt.datetime.now()) + '.csv'
        )
        response.direct_passthrough = False
        return response
