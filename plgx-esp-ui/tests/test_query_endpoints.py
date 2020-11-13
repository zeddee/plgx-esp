"""
All Test-Case required client, url_prefix and token,
and these all we need to just pass as parameters in the function.
"""

import json
from polylogyx.dao import queries_dao, packs_dao
from polylogyx.models import Tag


class TestGetQueriesList:
    """
    Test-case inside this block where these payloads are used,
    start and limit value should be integer value,
    these are optionals payload values
    """
    payload = {'start': None, 'limit': None}

    def test_queries_list_without_payload(self, client, url_prefix, token):
        """
        Test-Case without Payloads and without existing queries, packs and tags data,
        expected output:- status is success, and
        queries count i.e., 0 and queries data i.e., empty list in this case
        """
        resp = client.post(url_prefix + '/queries', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == {'count': 0, 'results': [], 'total_count': 0}

    def test_queries_list_with_payload_value_empty_dict(self, client, url_prefix, token):
        """
        Test-Case with Payloads empty dictionary and without existing queries, packs, and tags data,
        expected output:- status is success, and
        queries count i.e., 0 and queries data i.e., empty list in this case
        """
        resp = client.post(url_prefix + '/queries', headers={'x-access-token': token}, json={})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == {'count': 0, 'results': [], 'total_count': 0}

    def test_queries_list_with_payload_value_None(self, client, url_prefix, token):
        """
        Test-Case with Payloads values are None and without existing queries, packs and tags data,
        expected output:- status is success, and
        queries count i.e., 0 and queries data i.e., empty list in this case
        """
        resp = client.post(url_prefix + '/queries', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == {'count': 0, 'results': [], 'total_count': 0}

    def test_queries_list_with_payload_value(self, client, url_prefix, token):
        """
        Test-Case with Payloads values and without existing queries, packs and tags data,
        expected output:- status is success, and
        queries count i.e., 0 and queries data i.e., empty list in this case
        """
        self.payload['start'] = 0
        self.payload['limit'] = 10
        resp = client.post(url_prefix + '/queries', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == {'count': 0, 'results': [], 'total_count': 0}

    def test_queries_list_with_invalid_method(self, client, url_prefix, token, packs, tag, queries):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.put(url_prefix + '/queries', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_queries_lists_without_payload(self, client, url_prefix, token, packs, tag, queries):
        """
        Test-Case without Payloads and with existing queries, packs and tags data,
        expected output:- status is success, and
        queries count i.e., 1 and queries data(like, name, version, descriptions, tags, packs, etc.,)
        """
        t = Tag.query.filter(Tag.value == 'test').first()
        p = packs_dao.get_pack_by_name('pytest_pack')
        q = queries_dao.get_query_by_name('test_query')
        q.packs.append(p)
        q.tags.append(t)
        resp = client.post(url_prefix + '/queries', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        assert response_dict['data']['results'][0]['name'] == 'test_query'
        assert response_dict['data']['results'][0]['sql'] == 'select * from osquery_info;'
        assert response_dict['data']['results'][0]['tags'] == ['test']
        assert response_dict['data']['results'][0]['packs'] == ['pytest_pack']

    def test_queries_lists_with_payload_value_empty_dict(self, client, url_prefix, token, packs, tag, queries):
        """
        Test-Case with payload value empty dictionary and with existing queries, packs and tags data,
        expected output:- status is success, and
        queries count i.e., 1 and queries data(like, name, version, descriptions, tags, packs, etc.,)
        """
        t = Tag.query.filter(Tag.value == 'test').first()
        p = packs_dao.get_pack_by_name('pytest_pack')
        q = queries_dao.get_query_by_name('test_query')
        q.packs.append(p)
        q.tags.append(t)
        resp = client.post(url_prefix + '/queries', headers={'x-access-token': token}, json={})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        assert response_dict['data']['results'][0]['name'] == 'test_query'
        assert response_dict['data']['results'][0]['sql'] == 'select * from osquery_info;'
        assert response_dict['data']['results'][0]['tags'] == ['test']
        assert response_dict['data']['results'][0]['packs'] == ['pytest_pack']

    def test_queries_lists_with_payload_value_none(self, client, url_prefix, token, packs, tag, queries):
        """
        Test-Case with payload value none and with existing queries, packs and tags data,
        expected output:- status is success, and
        queries count i.e., 1 and queries data(like, name, version, descriptions, tags, packs, etc.,)
        """
        self.payload['start'] = None
        self.payload['limit'] = None
        t = Tag.query.filter(Tag.value == 'test').first()
        p = packs_dao.get_pack_by_name('pytest_pack')
        q = queries_dao.get_query_by_name('test_query')
        q.packs.append(p)
        q.tags.append(t)
        resp = client.post(url_prefix + '/queries', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        assert response_dict['data']['results'][0]['name'] == 'test_query'
        assert response_dict['data']['results'][0]['sql'] == 'select * from osquery_info;'
        assert response_dict['data']['results'][0]['tags'] == ['test']
        assert response_dict['data']['results'][0]['packs'] == ['pytest_pack']

    def test_queries_lists_with_payload_value(self, client, url_prefix, token, packs, tag, queries):
        """
        Test-Case with payload and with existing queries, packs and tags data,
        expected output:- status is success, and
        queries count i.e., 1 and queries data(like, name, version, descriptions, tags, packs, etc.,)
        """
        self.payload['start'] = 0
        self.payload['limit'] = 7
        t = Tag.query.filter(Tag.value == 'test').first()
        p = packs_dao.get_pack_by_name('pytest_pack')
        q = queries_dao.get_query_by_name('test_query')
        q.packs.append(p)
        q.tags.append(t)
        resp = client.post(url_prefix + '/queries', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        assert response_dict['data']['results'][0]['name'] == 'test_query'
        assert response_dict['data']['results'][0]['sql'] == 'select * from osquery_info;'
        assert response_dict['data']['results'][0]['tags'] == ['test']
        assert response_dict['data']['results'][0]['packs'] == ['pytest_pack']


class TestAddQueriesList:
    """
    Test-case inside this block where these payloads are using,
    out of all name, query and intervals are compulsory value of payloads,
    otherwise it will return 400 i.e., bad request
    platform and snapshot having some choices i.e., platform(
    windows/linux/darwin/all/posix/freebsd) we have to choose any one, and
    snapshot(True/False) we have to choose any one
    """
    payload = {
        "name": None, "query": None, "interval": None,
        "tags": None, "platform": None, "value": None,
        "version": None, "description": None, "snapshot": None, "packs": None
    }

    def test_add_query_without_payload(self, client, url_prefix, token):
        """
        Test-case without payloads and without existing packs and queries data,
        expected output:- status code is 400
        """
        resp = client.post(url_prefix + '/queries/add', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_add_query_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payloads empty dictionary and without existing packs and queries data,
        expected output:- status code is 400
        """
        resp = client.post(url_prefix + '/queries/add', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_add_query_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with payloads values are none and without existing packs and queries data,
        expected output:- status code is 400
        """
        resp = client.post(url_prefix + '/queries/add', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_add_query_with_compulsory_payload_value(self, client, url_prefix, token):
        """
        Test-case with compulsory payloads values and without existing packs and queries data,
        expected output:- status is success, and query_id
        """
        payload = {
            'name': 'test_query',
            'query': 'select * from osquery_info;',
            'interval': 30
        }
        resp = client.post(url_prefix + '/queries/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['query_id'] == 1

    def test_add_query_with_all_payload_value(self, client, url_prefix, token):
        """
        Test-case with all payloads values and without existing packs and queries data,
        expected output:- status is success, and query_id
        """
        payload = {
            'name': 'test_query',
            'query': 'select * from osquery_info;',
            'interval': 30, "tags": "foo,foobar",
            "platform": 'linux', "version": '2.0', "description": 'Processes',
            "snapshot": "true", "packs": "pytest_pack"
        }
        resp = client.post(url_prefix + '/queries/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['query_id'] == 1

    def test_add_query_with_all_payload_value_with_false_snapshot(self, client, url_prefix, token):
        """
        Test-case with all payloads with false value of snapshot
        values and without existing packs and queries data,
        expected output:- status is success, and query_id
        """
        payload = {
            'name': 'test_query',
            'query': 'select * from osquery_info;',
            'interval': 30, "tags": "foo,foobar",
            "platform": 'linux', "version": '2.0', "description": 'Processes',
            "snapshot": "false", "packs": "pytest_pack"
        }
        resp = client.post(url_prefix + '/queries/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['query_id'] == 1

    def test_add_query_with_all_payload_value_with_invalid_platform(self, client, url_prefix, token):
        """
        Test-case with all payloads values with invalid platform values
        and without existing packs and queries data,
        expected output:- status_code ids 400
        """
        payload = {
            'name': 'test_query',
            'query': 'select * from osquery_info;',
            'interval': 30, "tags": "foo,foobar",
            "platform": 'abc', "version": '2.0', "description": 'Processes',
            "snapshot": "true", "packs": "pytest_pack"
        }
        resp = client.post(url_prefix + '/queries/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 400

    def test_add_query_with_all_payload_value_with_invalid_snapshot(self, client, url_prefix, token):
        """
        Test-case with all payloads values with invalid platform values
        and without existing packs and queries data,
        expected output:- status_code ids 400
        """
        payload = {
            'name': 'test_query',
            'query': 'select * from osquery_info;',
            'interval': 30, "tags": "foo,foobar",
            "platform": 'linux', "version": '2.0', "description": 'Processes',
            "snapshot": True, "packs": "pytest_pack"
        }
        resp = client.post(url_prefix + '/queries/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 400

    def test_add_query_with_invalid_method(self, client, url_prefix, token, packs, queries):
        """
      Test-case with invalid request method,
      expected output:- status code is 405
      """
        resp = client.put(url_prefix + '/queries/add', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_add_queries_with_compulsory_payload_value(self, client, url_prefix, token, packs, queries):
        """
        Test-case with compulsory payloads values and with existing packs and queries data,
        expected output:- status is failure
        """
        payload = {
            'name': 'test_query',
            'query': 'select * from osquery_info;',
            'interval': 30
        }
        resp = client.post(url_prefix + '/queries/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_add_queries_with_all_payload_value(self, client, url_prefix, token, packs, queries):
        """
        Test-case with compulsory payloads values and with existing packs data,
        expected output:- status is success, and query_id
        """
        payload = {
            'name': 'test_query2',
            'query': 'select * from osquery_info',
            'interval': 30, "tags": "foo,foobar",
            "platform": 'linux', "version": '2.0', "description": 'Processes',
            "snapshot": "true", "packs": "pytest_pack"
        }
        resp = client.post(url_prefix + '/queries/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['query_id'] == 2

    def test_add_query_with_all_payload_value_with_false_snapshots(self, client, url_prefix, token, packs, queries):
        """
        Test-case with all payloads with false value of snapshot
        values and with existing packs and queries data,
        expected output:- status is failure
        """
        payload = {
            'name': 'test_query',
            'query': 'select * from osquery_info;',
            'interval': 30, "tags": "foo,foobar",
            "platform": 'linux', "version": '2.0', "description": 'Processes',
            "snapshot": "false", "packs": "pytest_pack"
        }
        resp = client.post(url_prefix + '/queries/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_add_query_with_all_payload_value_with_invalid_platforms(self, client, url_prefix, token, packs, queries):
        """
        Test-case with all payloads values with invalid platform values
        and with existing packs and queries data,
        expected output:- status_code ids 400
        """
        payload = {
            'name': 'test_query',
            'query': 'select * from osquery_info;',
            'interval': 30, "tags": "foo,foobar",
            "platform": 'abc', "version": '2.0', "description": 'Processes',
            "snapshot": "true", "packs": "pytest_pack"
        }
        resp = client.post(url_prefix + '/queries/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 400

    def test_add_query_with_all_payload_value_with_invalid_snapshots(self, client, url_prefix, token, packs, queries):
        """
        Test-case with all payloads values with invalid platform values
        and with existing packs and queries data,
        expected output:- status_code ids 400
        """
        payload = {
            'name': 'test_query',
            'query': 'select * from osquery_info;',
            'interval': 30, "tags": "foo,foobar",
            "platform": 'linux', "version": '2.0', "description": 'Processes',
            "snapshot": True, "packs": "pytest_pack"
        }
        resp = client.post(url_prefix + '/queries/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 400


class TestPackedQueriesList:
    """
    Test-case inside this block where these payloads are used,
    start and limit value should be integer value,
    these are optionals payload values
    """
    payload = {'start': None, 'limit': None}

    def test_queries_list_without_payload(self, client, url_prefix, token):
        """
        Test-Case without Payloads and without existing queries, packs and tags data,
        expected output:- status is success, and
        queries count i.e., 0 and queries data i.e., empty list in this case
        """
        resp = client.post(url_prefix + '/queries/packed', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == {'count': 0, 'results': [], 'total_count': 0}

    def test_queries_list_with_payload_value_empty_dict(self, client, url_prefix, token):
        """
        Test-Case with Payloads empty dictionary and without existing queries, packs, and tags data,
        expected output:- status is success, and
        queries count i.e., 0 and queries data i.e., empty list in this case
        """
        resp = client.post(url_prefix + '/queries/packed', headers={'x-access-token': token}, json={})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == {'count': 0, 'results': [], 'total_count': 0}

    def test_queries_list_with_payload_value_None(self, client, url_prefix, token):
        """
        Test-Case with Payloads values are None and without existing queries, packs and tags data,
        expected output:- status is success, and
        queries count i.e., 0 and queries data i.e., empty list in this case
        """
        resp = client.post(url_prefix + '/queries/packed', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == {'count': 0, 'results': [], 'total_count': 0}

    def test_queries_list_with_payload_value(self, client, url_prefix, token):
        """
        Test-Case with Payloads values and without existing queries, packs and tags data,
        expected output:- status is success, and
        queries count i.e., 0 and queries data i.e., empty list in this case
        """
        self.payload['start'] = 0
        self.payload['limit'] = 10
        resp = client.post(url_prefix + '/queries/packed', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == {'count': 0, 'results': [], 'total_count': 0}

    def test_queries_list_with_invalid_method(self, client, url_prefix, token, packs, tag, queries):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.put(url_prefix + '/queries/packed', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_queries_lists_without_payload(self, client, url_prefix, token, packs, tag, queries):
        """
        Test-Case without Payloads and with existing queries, packs and tags data,
        expected output:- status is success, and
        queries count i.e., 1 and queries data(like, name, version, descriptions, tags, packs, etc.,)
        """
        t = Tag.query.filter(Tag.value == 'test').first()
        p = packs_dao.get_pack_by_name('pytest_pack')
        q = queries_dao.get_query_by_name('test_query')
        q.packs.append(p)
        q.tags.append(t)
        resp = client.post(url_prefix + '/queries/packed', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        assert response_dict['data']['results'][0]['name'] == 'test_query'
        assert response_dict['data']['results'][0]['sql'] == 'select * from osquery_info;'
        assert response_dict['data']['results'][0]['tags'] == ['test']
        assert response_dict['data']['results'][0]['packs'] == ['pytest_pack']

    def test_queries_lists_with_payload_value_empty_dict(self, client, url_prefix, token, packs, tag, queries):
        """
        Test-Case with payload value empty dictionary and with existing queries, packs and tags data,
        expected output:- status is success, and
        queries count i.e., 1 and queries data(like, name, version, descriptions, tags, packs, etc.,)
        """
        t = Tag.query.filter(Tag.value == 'test').first()
        p = packs_dao.get_pack_by_name('pytest_pack')
        q = queries_dao.get_query_by_name('test_query')
        q.packs.append(p)
        q.tags.append(t)
        resp = client.post(url_prefix + '/queries/packed', headers={'x-access-token': token}, json={})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        assert response_dict['data']['results'][0]['name'] == 'test_query'
        assert response_dict['data']['results'][0]['sql'] == 'select * from osquery_info;'
        assert response_dict['data']['results'][0]['tags'] == ['test']
        assert response_dict['data']['results'][0]['packs'] == ['pytest_pack']

    def test_queries_lists_with_payload_value_none(self, client, url_prefix, token, packs, tag, queries):
        """
        Test-Case with payload value none and with existing queries, packs and tags data,
        expected output:- status is success, and
        queries count i.e., 1 and queries data(like, name, version, descriptions, tags, packs, etc.,)
        """
        self.payload['start'] = None
        self.payload['limit'] = None
        t = Tag.query.filter(Tag.value == 'test').first()
        p = packs_dao.get_pack_by_name('pytest_pack')
        q = queries_dao.get_query_by_name('test_query')
        q.packs.append(p)
        q.tags.append(t)
        resp = client.post(url_prefix + '/queries/packed', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        assert response_dict['data']['results'][0]['name'] == 'test_query'
        assert response_dict['data']['results'][0]['sql'] == 'select * from osquery_info;'
        assert response_dict['data']['results'][0]['tags'] == ['test']
        assert response_dict['data']['results'][0]['packs'] == ['pytest_pack']

    def test_queries_lists_with_payload_value(self, client, url_prefix, token, packs, tag, queries):
        """
        Test-Case with payload and with existing queries, packs and tags data,
        expected output:- status is success, and
        queries count i.e., 1 and queries data(like, name, version, descriptions, tags, packs, etc.,)
        """
        self.payload['start'] = 0
        self.payload['limit'] = 7
        t = Tag.query.filter(Tag.value == 'test').first()
        p = packs_dao.get_pack_by_name('pytest_pack')
        q = queries_dao.get_query_by_name('test_query')
        q.packs.append(p)
        q.tags.append(t)
        resp = client.post(url_prefix + '/queries/packed', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        assert response_dict['data']['results'][0]['name'] == 'test_query'
        assert response_dict['data']['results'][0]['sql'] == 'select * from osquery_info;'
        assert response_dict['data']['results'][0]['tags'] == ['test']
        assert response_dict['data']['results'][0]['packs'] == ['pytest_pack']


class TestGetQueryById:

    def test_get_query_by_invalid_id(self, client, url_prefix, token):
        """
        Test-case with invalid query_id which is passing through url,
        and without existing packs ,queries and tags data,
        expected output:- status is failure
        """
        resp = client.get(url_prefix + '/queries/4', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_query_by_valid_id(self, client, url_prefix, token):
        """
        Test-case with valid query_id which is passing through url,
        and without existing packs, queries and tags data,
        expected output:- status is failure
        """
        resp = client.get(url_prefix + '/queries/4', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_query_by_id_with_invalid_method(self, client, url_prefix, token, packs, queries):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.put(url_prefix + '/queries/1', headers={'x-access-token': token})
        assert resp.status_code == 405

    def test_get_queries_by_invalid_id(self, client, url_prefix, token, packs, queries):
        """
        Test-case with invalid query_id which is passing through url,
        and without existing packs queries, and tags data,
        expected output:- status is failure
        """
        resp = client.get(url_prefix + '/queries/4', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_queries_by_valid_id(self, client, url_prefix, token, packs, queries, tag):
        """
        Test-case with valid query_id which is passing through url,
        and without existing packs queries, and tags data,
        expected output:- status is success, and
        packs data in dictionary format with key values of tags and packs, etc.
        """
        p = packs_dao.get_pack_by_name('pytest_pack')
        t = Tag.query.filter(Tag.value == 'test').first()
        q = queries_dao.get_query_by_name('test_query')
        q.packs.append(p)
        q.tags.append(t)
        resp = client.get(url_prefix + '/queries/1', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['id'] == 1
        assert response_dict['data']['tags'] == ['test']
        assert response_dict['data']['packs'] == ['pytest_pack']


class TestEditQueryById:
    """
        Test-case inside this block where these payloads are using,
        out of all name, query and intervals are compulsory value of payloads,
        otherwise it will return 400 i.e., bad request
        platform and snapshot having some choices i.e., platform(
        windows/linux/darwin/all/posix/freebsd) we have to choose any one, and
        snapshot(True/False) we have to choose any one
        """
    payload = {
        "name": None, "query": None, "interval": None,
        "tags": None, "platform": None, "value": None,
        "version": None, "description": None, "snapshot": None, "packs": None
    }

    def test_edit_query_without_payload(self, client, url_prefix, token):
        """
        Test-case without payloads and without existing packs, queries and tags data,
        and valid/invalid query_id which is passing through url
        expected output:- status code is 400
        """
        resp = client.post(url_prefix + '/queries/1', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_edit_query_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payloads empty dictionary and without existing packs, queries and tags data,
        and valid/invalid query_id which is passing through url
        expected output:- status code is 400
        """
        resp = client.post(url_prefix + '/queries/1', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_edit_query_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with payloads values are none and without existing packs, queries and tags data,
        and valid/invalid query_id which is passing through url
        expected output:- status code is 400
        """
        resp = client.post(url_prefix + '/queries/1', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_edit_query_with_compulsory_payload_value(self, client, url_prefix, token):
        """
        Test-case with compulsory payloads values and without existing packs, queries and tags data,
        and valid/invalid query_id which is passing through url
        expected output:- status is failure
        """
        payload = {
            'name': 'test_query',
            'query': 'select * from osquery_info;',
            'interval': 30
        }
        resp = client.post(url_prefix + '/queries/1', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_edit_query_with_all_payload_value(self, client, url_prefix, token):
        """
        Test-case with all payloads values and without existing packs data,
        and valid/invalid query_id which is passing through url
        expected output:- status is failure
        """
        payload = {
            'name': 'test_query',
            'query': 'select * from osquery_info;',
            'interval': 30, "tags": "foo,foobar",
            "platform": 'linux', "version": '2.0', "description": 'Processes',
            "snapshot": "true", "packs": "pytest_pack"
        }
        resp = client.post(url_prefix + '/queries/1', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_edit_query_with_all_payload_value_with_false_snapshot(self, client, url_prefix, token):
        """
        Test-case with all payloads with false value of snapshot
        values and without existing packs and queries data,
        expected output:- status is failure
        """
        payload = {
            'name': 'test_query',
            'query': 'select * from osquery_info;',
            'interval': 30, "tags": "foo,foobar",
            "platform": 'linux', "version": '2.0', "description": 'Processes',
            "snapshot": "false", "packs": "pytest_pack"
        }
        resp = client.post(url_prefix + '/queries/1', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_edit_query_with_all_payload_value_with_invalid_platform(self, client, url_prefix, token):
        """
        Test-case with all payloads values with invalid platform values
        and without existing packs and queries data,
        expected output:- status_code ids 400
        """
        payload = {
            'name': 'test_query',
            'query': 'select * from osquery_info;',
            'interval': 30, "tags": "foo,foobar",
            "platform": 'abc', "version": '2.0', "description": 'Processes',
            "snapshot": "true", "packs": "pytest_pack"
        }
        resp = client.post(url_prefix + '/queries/1', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 400

    def test_edit_query_with_all_payload_value_with_invalid_snapshot(self, client, url_prefix, token):
        """
        Test-case with all payloads values with invalid platform values
        and without existing packs and queries data,
        expected output:- status_code ids 400
        """
        payload = {
            'name': 'test_query',
            'query': 'select * from osquery_info;',
            'interval': 30, "tags": "foo,foobar",
            "platform": 'linux', "version": '2.0', "description": 'Processes',
            "snapshot": True, "packs": "pytest_pack"
        }
        resp = client.post(url_prefix + '/queries/1', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 400

    def test_edit_query_with_invalid_method(self, client, url_prefix, token):
        """
      Test-case with invalid request method,
      expected output:- status code is 405
      """
        resp = client.put(url_prefix + '/queries/1', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_edit_queries_with_compulsory_payload_value_and_invalid_query_id(self, client, url_prefix, token, packs, queries):
        """
        Test-case with compulsory payloads values and with existing packs data,
        and invalid query_id which is passing through url
        expected output:- status is failure
        """
        payload = {
            'name': 'test_query',
            'query': 'select * from osquery_info;',
            'interval': 30
        }
        resp = client.post(url_prefix + '/queries/3', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_edit_queries_with_compulsory_payload_value_and_valid_query_id(self, client, url_prefix, token, packs, queries):
        """
        Test-case with compulsory payloads values and with existing packs data,
        and valid query_id which is passing through url
        expected output:- status is success, and
        response data of queries in dict format(with_key_values pairs)
        """
        payload = {
            'name': 'test_query',
            'query': 'select * from osquery_info;',
            'interval': 30
        }
        resp = client.post(url_prefix + '/queries/1', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['id'] == 1
        assert response_dict['data']['interval'] == 30
        assert response_dict['data']['name'] == 'test_query'
        assert response_dict['data']['sql'] == 'select * from osquery_info;'

    def test_edit_queries_with_all_payload_value_and_invalid_query_id(self, client, url_prefix, token, packs, queries):
        """
        Test-case with compulsory payloads values and with existing packs data,
        and invalid query_id which is passing through url
        expected output:- status is failure
        """
        payload = {
            'name': 'test_query2',
            'query': 'select * from osquery_info',
            'interval': 30, "tags": "foo,foobar",
            "platform": 'linux', "version": '2.0', "description": 'Processes',
            "snapshot": "true", "packs": "pytest_pack"
        }
        resp = client.post(url_prefix + '/queries/3', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_edit_queries_with_all_payload_value_and_valid_query_id(self, client, url_prefix, token, packs, queries):
        """
        Test-case with compulsory payloads values and with existing packs data,
        and invalid query_id which is passing through url
        expected output:- status is success, and
        response data of queries in dict format(with_key_values pairs)
        """
        payload = {
            'name': 'test_query2',
            'query': 'select * from osquery_info',
            'interval': 30, "tags": "foo,foobar",
            "platform": 'linux', "version": '2.0', "description": 'Processes',
            "snapshot": "true", "packs": "pytest_pack"
        }
        resp = client.post(url_prefix + '/queries/1', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['id'] == 1
        assert response_dict['data']['interval'] == 30
        assert response_dict['data']['name'] == 'test_query2'
        assert response_dict['data']['sql'] == 'select * from osquery_info'

    def test_edit_query_with_all_payload_value_with_false_snapshots(self, client, url_prefix, token, packs, queries):
        """
        Test-case with all payloads with false value of snapshot
        values and with existing packs and queries data,
        expected output:- status is success, , and
        response data of queries in dict format(with_key_values pairs)
        """
        payload = {
            'name': 'test_query',
            'query': 'select * from osquery_info;',
            'interval': 30, "tags": "foo,foobar",
            "platform": 'linux', "version": '2.0', "description": 'Processes',
            "snapshot": "false", "packs": "pytest_pack"
        }
        resp = client.post(url_prefix + '/queries/1', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['id'] == 1
        assert response_dict['data']['interval'] == 30
        assert response_dict['data']['name'] == 'test_query'
        assert response_dict['data']['sql'] == 'select * from osquery_info;'

    def test_edit_query_with_all_payload_value_with_invalid_platforms(self, client, url_prefix, token, packs, queries):
        """
        Test-case with all payloads values with invalid platform values
        and with existing packs and queries data,
        expected output:- status_code ids 400
        """
        payload = {
            'name': 'test_query',
            'query': 'select * from osquery_info;',
            'interval': 30, "tags": "foo,foobar",
            "platform": 'abc', "version": '2.0', "description": 'Processes',
            "snapshot": "true", "packs": "pytest_pack"
        }
        resp = client.post(url_prefix + '/queries/1', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 400

    def test_edit_query_with_all_payload_value_with_invalid_snapshots(self, client, url_prefix, token, packs, queries):
        """
        Test-case with all payloads values with invalid platform values
        and with existing packs and queries data,
        expected output:- status_code ids 400
        """
        payload = {
            'name': 'test_query',
            'query': 'select * from osquery_info;',
            'interval': 30, "tags": "foo,foobar",
            "platform": 'linux', "version": '2.0', "description": 'Processes',
            "snapshot": True, "packs": "pytest_pack"
        }
        resp = client.post(url_prefix + '/queries/1', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 400


class TestAddListTagsOfQuery:
    """
    Test-case inside this block where this payload value is used,
    this is compulsory payload value of any string type,
    if value is none or anything other than string,
    it will return 400 i.e., bad request
    """
    payload = {'tag': None,}

    def test_add_list_of_tags_of_query_without_payload(self, client, url_prefix, token):
        """
        Test-case without payload and without existing queries and tags data,
        valid/invalid query_id is passing through url,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/queries/1/tags', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_add_list_of_tags_of_query_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload is empty dictionary and without existing queries and tags data,
        valid/invalid query_id is passing through url,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/queries/3/tags', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_add_list_of_tags_of_query_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with payload value is none and without existing queries and tags data,
        valid/invalid query_id is passing through url,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/queries/1/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_add_list_of_tags_of_query_with_valid_payload_value(self, client, url_prefix, token):
        """
        Test-case with valid payload value and without existing queries and tags data,
        valid/invalid query_id is passing through url,
        expected output:- status is failure
        """
        self.payload['tag'] = 'test-dummydata123'
        resp = client.post(url_prefix + '/queries/3/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_add_list_of_tags_of_query_with_invalid_method(self, client, url_prefix, token):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.put(url_prefix + '/queries/3/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_add_list_of_tags_of_query_with_invalid_query_id(self, client, url_prefix, token, queries, tag):
        """
        Test-case with valid payload value and with existing queries and tags data,
        valid/invalid query_id is passing through url,
        expected output:- status is failure
        """
        self.payload['tag'] = 'test-dummy'
        resp = client.post(url_prefix + '/queries/3/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_add_list_of_tags_of_query_with_valid_query_id(self, client, url_prefix, token, queries, tag):
        """
        Test-case with valid payload value and with existing query and tags data,
        valid/invalid query_id is passing through url,
        expected output:- status is success
        """
        self.payload['tag'] = 'test-dummy'
        resp = client.post(url_prefix + '/queries/1/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        q = queries_dao.get_query_by_id(1)
        assert [tag.value for tag in q.tags] == ['test-dummy']


class TestGetListTagsOfQuery:

    def test_get_list_of_tags_of_query_with_invalid_query_id(self, client, url_prefix, token):
        """
        Test-case with invalid query_id name which is passing through url
        and without existing queries and tags data,
        expected output:- status is failure
        """
        resp = client.get(url_prefix + '/queries/3/tags', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_list_of_tags_of_query_with_valid_query_id(self, client, url_prefix, token):
        """
        Test-case with valid query_id which is passing through url
        and without existing queries and tags data,
        expected output:- status is failure
        """
        resp = client.get(url_prefix + '/queries/1/tags', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_list_of_tags_of_query_with_invalid_method(self, client, url_prefix, token, queries, tag):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.put(url_prefix + '/queries/1/tags', headers={'x-access-token': token})
        assert resp.status_code == 405

    def test_get_lists_of_tags_of_query_with_invalid_query_id(self, client, url_prefix, token, queries, tag):
        """
        Test-case with invalid query id which is passing through url
        and without existing queries and tags data,
        expected output:- status is failure
        """
        resp = client.get(url_prefix + '/queries/3/tags', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_lists_of_tags_of_query_with_valid_query_id(self, client, url_prefix, token, queries, tag):
        """
        Test-case with valid query id which is passing through url
        and without existing queries and tags data,
        expected output:- status is success, and
        list of tag's name
        """
        q = queries_dao.get_query_by_id(1)
        t = Tag.query.filter(Tag.value == 'test').first()
        q.tags.append(t)
        resp = client.get(url_prefix + '/queries/1/tags', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == ['test']


class TestDeleteListTagsOfQuery:
    """
    Test-case inside this block where this payload value is used,
    this is compulsory payload value of any string type,
    if value is none or anything  other than string,
    it will return 400 i.e., bad request
    """
    payload = {'tag': None,}

    def test_delete_query_list_of_tags_without_payload(self, client, url_prefix, token):
        """
        Test-case without payload and without existing queries and tags data,
        valid/invalid query_id is passing through url,
        expected output:- status_code is 400
        """
        resp = client.delete(url_prefix + '/queries/1/tags', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_delete_query_list_of_tags_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload is empty dictionary and without existing packs and tags data,
        valid/invalid query_id is passing through url,
        expected output:- status_code is 400
        """
        resp = client.delete(url_prefix + '/queries/3/tags', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_delete_query_list_of_tags_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with payload value is none and without existing packs and tags data,
        valid/invalid query_id is passing through url,
        expected output:- status_code is 400
        """
        resp = client.delete(url_prefix + '/queries/1/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_delete_query_list_of_tags_with_valid_payload_value(self, client, url_prefix, token):
        """
        Test-case with valid payload value and without existing packs and tags data,
        valid/invalid query_id is passing through url,
        expected output:- status is failure
        """
        self.payload['tag'] = 'test-dummydata123'
        resp = client.delete(url_prefix + '/queries/3/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_delete_pack_of_tags_with_invalid_method(self, client, url_prefix, token, queries, tag):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.put(url_prefix + '/queries/3/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_delete_pack_of_tags_with_invalid_query_id(self, client, url_prefix, token, queries, tag):
        """
        Test-case with valid payload value and with existing queries and tags data,
        invalid query_id is passing through url,
        expected output:- status is failure
        """
        self.payload['tag'] = 'test-dummy'
        resp = client.delete(url_prefix + '/queries/3/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_delete_pack_of_tags_with_valid_query_id(self, client, url_prefix, token, queries, tag):
        """
        Test-case with valid payload value and with existing queies and tags data,
        valid query_id is passing through url,
        expected output:- status is success
        """
        self.payload['tag'] = 'test'
        q = queries_dao.get_query_by_id(1)
        t = Tag.query.filter(Tag.value == 'test').first()
        q.tags.append(t)
        resp = client.delete(url_prefix + '/queries/1/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        q = queries_dao.get_query_by_id(1)
        assert [tag.value for tag in q.tags] == []

    def test_delete_pack_of_tags_with_invalid_tag_value(self, client, url_prefix, token, queries, tag):
        """
        Test-case with invalid payload value and with existing packs and tags data,
        valid query_id is passing through url,
        expected output:- status is failure
        """
        self.payload['tag'] = 'test12'
        resp = client.delete(url_prefix + '/queries/1/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'


class TestQueryRemoved:

    def test_query_removed_by_id_without_queries_data(self, client, url_prefix, token):
        """
        Test-case with valid/invalid query_id and without existing queries data,
        expected output:- status is failure
        """
        resp = client.delete(url_prefix + '/queries/1/delete', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_query_removed_by_name_without_queries_data(self, client, url_prefix, token):
        """
        Test-case with valid/invalid query_name and without existing queries data,
        expected output:- status is failure
        """
        resp = client.delete(url_prefix + '/queries/test_query/delete', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_query_removed_with_invalid_method(self, client, url_prefix, token, queries):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.get(url_prefix + '/queries/1/delete', headers={'x-access-token': token})
        assert resp.status_code == 405

    def test_query_removed_by_invalid_id_with_queries_data(self, client, url_prefix, token, queries):
        """
        Test-case with invalid query_id and with existing queries data,
        expected output:- status is failure
        """
        resp = client.delete(url_prefix + '/queries/5/delete', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_query_removed_by_valid_id_with_queries_data(self, client, url_prefix, token, queries):
        """
        Test-case with valid query_id and with existing packs data,
        expected output:- status is Success
        """
        resp = client.delete(url_prefix + '/queries/1/delete', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'Success'
        assert queries_dao.get_query_by_id(1) is None

    def test_query_removed_by_invalid_name_with_queries_data(self, client, url_prefix, token, queries):
        """
        Test-case with invalid query_name and with existing queries data,
        expected output:- status is failure
        """
        resp = client.delete(url_prefix + '/queries/test_queries/delete', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_query_removed_by_valid_name_with_queries_data(self, client, url_prefix, token, queries):
        """
        Test-case with valid query_name and with existing queries data,
        expected output:- status is Success
        """
        resp = client.delete(url_prefix + '/queries/test_query/delete', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'Success'
        assert queries_dao.get_query_by_name('test_query') is None
