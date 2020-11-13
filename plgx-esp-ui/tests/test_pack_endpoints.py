"""
All Test-Case required client, url_prefix and token,
and these all we need to just pass as parameters in the function.
"""

import json, os
from flask_restplus import marshal

from polylogyx.dao import packs_dao, queries_dao
from polylogyx.models import Tag
from polylogyx.wrappers import pack_wrappers, query_wrappers
from .base import TestUtils


class TestPacksList:
    """
    Test-case inside this block where these payloads are used,
    start and limit value should be integer,
    these are optionals payload values
    """
    payload = {'start': None, 'limit':None}

    def test_packs_list_without_payload(self, client, url_prefix, token):
        """
        Test-Case without Payloads and without existing packs data,
        expected output:- status is success, and
        packs count i.e., 0 and packs data i.e., empty list in this case
        """
        resp = client.post(url_prefix + '/packs', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == {'count': 0, 'results': [], 'total_count': 0}

    def test_packs_list_with_payload_value_empty_dict(self, client, url_prefix, token):
        """
        Test-Case with Payloads empty dictionary and without existing packs data,
        expected output:- status is success, and
        packs count i.e., 0 and packs data i.e., empty list in this case
        """
        resp = client.post(url_prefix + '/packs', headers={'x-access-token': token}, json={})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == {'count': 0, 'results': [], 'total_count': 0}

    def test_packs_list_with_payload_value_None(self, client, url_prefix, token):
        """
        Test-Case with Payloads values are None and without existing packs data,
        expected output:- status is success, and
        packs count i.e., 0 and packs data i.e., empty list in this case
        """
        resp = client.post(url_prefix + '/packs', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == {'count': 0, 'results': [], 'total_count': 0}

    def test_packs_list_with_payload_value(self, client, url_prefix, token):
        """
        Test-Case with Payloads values and without existing packs data,
        expected output:- status is success, and
        packs count i.e., 0 and packs data i.e., empty list in this case
        """
        self.payload['start'] = 0
        self.payload['limit'] = 10
        resp = client.post(url_prefix + '/packs', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == {'count': 0, 'results': [], 'total_count': 0}

    def test_packs_list_with_invalid_method(self, client, url_prefix, token, packs, tag, queries):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.put(url_prefix + '/packs', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_packs_lists_without_payload(self, client, url_prefix, token, packs, tag, queries):
        """
        Test-Case without Payloads and with existing packs data,
        expected output:- status is success, and
        packs count i.e., 1 and packs data(like, name, version, descriptions, tags, queries, etc.,)
        """
        tags = Tag.query.filter(Tag.value == 'test').first()
        pack = packs_dao.get_pack_by_name('pytest_pack')
        q = queries_dao.get_query_by_name('test_query')
        pack.queries.append(q)
        pack.tags.append(tags)
        resp = client.post(url_prefix + '/packs', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        queryset = packs_dao.get_all_packs().offset(None).limit(None).all()
        data = marshal(queryset, pack_wrappers.pack_wrapper)
        for index in range(len(data)):
            data[index]['tags'] = [tag.to_dict() for tag in queryset[index].tags]
            data[index]['queries'] = marshal(queryset[index].queries, query_wrappers.query_wrapper)
            for query_index in range(len(queryset[index].queries)):
                data[index]['queries'][query_index]['tags'] = [tag.to_dict() for tag in
                                                               queryset[index].queries[query_index].tags]
                data[index]['queries'][query_index]['packs'] = [pack.name for pack in
                                                                queryset[index].queries[query_index].packs]
        assert response_dict['data']['results'] == data

    def test_packs_lists_with_payload_value_empty_dict(self, client, url_prefix, token, packs, tag, queries):
        """
        Test-Case with payload value empty dictionary and with existing packs data,
        expected output:- status is success, and
        packs count i.e., 1 and packs data(like, name, version, descriptions, tags, queries, etc.,)
        """
        tags = Tag.query.filter(Tag.value == 'test').first()
        pack = packs_dao.get_pack_by_name('pytest_pack')
        q = queries_dao.get_query_by_name('test_query')
        pack.queries.append(q)
        pack.tags.append(tags)
        resp = client.post(url_prefix + '/packs', headers={'x-access-token': token}, json={})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        queryset = packs_dao.get_all_packs().offset(None).limit(None).all()
        data = marshal(queryset, pack_wrappers.pack_wrapper)
        for index in range(len(data)):
            data[index]['tags'] = [tag.to_dict() for tag in queryset[index].tags]
            data[index]['queries'] = marshal(queryset[index].queries, query_wrappers.query_wrapper)
            for query_index in range(len(queryset[index].queries)):
                data[index]['queries'][query_index]['tags'] = [tag.to_dict() for tag in
                                                               queryset[index].queries[query_index].tags]
                data[index]['queries'][query_index]['packs'] = [pack.name for pack in
                                                                queryset[index].queries[query_index].packs]
        assert response_dict['data']['results'] == data

    def test_packs_lists_with_payload_value_none(self, client, url_prefix, token, packs, tag, queries):
        """
        Test-Case with payload value none and with existing packs data,
        expected output:- status is success, and
        packs count i.e., 1 and packs data(like, name, version, descriptions, tags, queries, etc.,)
        """
        self.payload['start'] = None
        self.payload['limit'] = None
        tags = Tag.query.filter(Tag.value == 'test').first()
        pack = packs_dao.get_pack_by_name('pytest_pack')
        q = queries_dao.get_query_by_name('test_query')
        pack.queries.append(q)
        pack.tags.append(tags)
        resp = client.post(url_prefix + '/packs', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        queryset = packs_dao.get_all_packs().offset(None).limit(None).all()
        data = marshal(queryset, pack_wrappers.pack_wrapper)
        for index in range(len(data)):
            data[index]['tags'] = [tag.to_dict() for tag in queryset[index].tags]
            data[index]['queries'] = marshal(queryset[index].queries, query_wrappers.query_wrapper)
            for query_index in range(len(queryset[index].queries)):
                data[index]['queries'][query_index]['tags'] = [tag.to_dict() for tag in
                                                               queryset[index].queries[query_index].tags]
                data[index]['queries'][query_index]['packs'] = [pack.name for pack in
                                                                queryset[index].queries[query_index].packs]
        assert response_dict['data']['results'] == data

    def test_packs_lists_with_payload_value(self, client, url_prefix, token, packs, tag, queries):
        """
        Test-Case with payload and with existing packs data,
        expected output:- status is success, and
        packs count i.e., 1 and packs data(like, name, version, descriptions, tags, queries, etc.,)
        """
        self.payload['start'] = 0
        self.payload['limit'] = 7
        tags = Tag.query.filter(Tag.value == 'test').first()
        pack = packs_dao.get_pack_by_name('pytest_pack')
        q = queries_dao.get_query_by_name('test_query')
        pack.queries.append(q)
        pack.tags.append(tags)
        resp = client.post(url_prefix + '/packs', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        queryset = packs_dao.get_all_packs().offset(None).limit(None).all()
        data = marshal(queryset, pack_wrappers.pack_wrapper)
        for index in range(len(data)):
            data[index]['tags'] = [tag.to_dict() for tag in queryset[index].tags]
            data[index]['queries'] = marshal(queryset[index].queries, query_wrappers.query_wrapper)
            for query_index in range(len(queryset[index].queries)):
                data[index]['queries'][query_index]['tags'] = [tag.to_dict() for tag in
                                                               queryset[index].queries[query_index].tags]
                data[index]['queries'][query_index]['packs'] = [pack.name for pack in
                                                                queryset[index].queries[query_index].packs]
        assert response_dict['data']['results'] == data


class TestAddPack:
    """
    Test-case inside this block where these payloads are using,
    out of all name and queries are compulsory value of payloads,
    otherwise it will return 400 i.e., bad request
    platform and categories having some choices i.e., platform(
    windows/linux/darwin/all/posix/freebsd) we have to choose any one, and
    categories(Intrusion Detection/Monitoring/Compliance and Management/Forensics
    and Incident Response/General/Others) we have to choose any one,
    """

    def test_add_pack_without_payload(self, client, url_prefix, token):
        """
        Test-case without payloads and without existing packs and queries data,
        expected output:- status code is 400
        """
        resp = client.post(url_prefix + '/packs/add', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_add_pack_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payloads empty dictionary and without existing packs and queries data,
        expected output:- status code is 400
        """
        resp = client.post(url_prefix + '/packs/add', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_add_pack_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with payloads values are none and without existing packs and queries data,
        expected output:- status code is 400
        """
        payload = {
            'name': None, 'queries':None, 'tags':None, 'description': None,
            'category': None, 'platform': None, 'version': None, 'shard': None
        }
        resp = client.post(url_prefix + '/packs/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 400

    def test_add_pack_with_compulsory_payload_value(self, client, url_prefix, token):
        """
        Test-case with compulsory payloads values and without existing packs and queries data,
        expected output:- status is success and pack_id
        """
        payload = {
            'name': 'pytest_pack',
            'queries': {
                'test_query': {
                    'query': 'select * from osquery_info;',
                    'interval': 30
                }
            }
        }
        resp = client.post(url_prefix + '/packs/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['pack_id'] == 1

    def test_add_pack_with_all_payload_value(self, client, url_prefix, token):
        """
        Test-case with all payloads values and without existing packs and queries data,
        expected output:- status is success and pack_id
        """
        payload = {
            'name': 'pytest_pack',
            'queries': {
                'test_query': {
                    'query': 'select * from osquery_info;', 'interval': 30
                }
            }, "tags": "foo,foobar", "category": 'Monitoring',
            "platform": 'linux', "version": '2.0', "description": 'pytest_pack', "shard": 2
        }
        resp = client.post(url_prefix + '/packs/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['pack_id'] == 1

    def test_add_pack_with_all_payload_value_with_invalid_patform(self, client, url_prefix, token):
        """
        Test-case with all payloads values with invalid platform value
        and without existing packs and queries data,
        expected output:- status_code is 400
        """
        payload = {
            'name': 'pytest_pack',
            'queries': {
                'test_query': {
                    'query': 'select * from osquery_info;', 'interval': 30
                }
            }, "tags": "foo,foobar", "category": 'Monitoring',
            "platform": 'abc', "version": '2.0', "description": 'pytest_pack', "shard": 2
        }
        resp = client.post(url_prefix + '/packs/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 400

    def test_add_pack_with_all_payload_value_with_invalid_category(self, client, url_prefix, token):
        """
        Test-case with all payloads values with invalid category value
        and without existing packs and queries data,
        expected output:- status_code is 400
        """
        payload = {
            'name': 'pytest_pack',
            'queries': {
                'test_query': {
                    'query': 'select * from osquery_info;', 'interval': 30
                }
            }, "tags": "foo,foobar", "category": 'testing',
            "platform": 'linux', "version": '2.0', "description": 'pytest_pack', "shard": 2
        }
        resp = client.post(url_prefix + '/packs/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 400

    def test_add_pack_with_invalid_method(self, client, url_prefix, token):
        """
      Test-case with invalid request method,
      expected output:- status code is 405
      """
        payload = {
            'name': 'pytest_pack',
            'queries': {
                'test_query': {
                    'query': 'select * from osquery_info;', 'interval': 30
                }
            }, "tags": "foo,foobar", "category": 'Monitoring',
            "platform": 'linux', "version": '2.0', "description": 'pytest_pack', "shard": 2
        }
        resp = client.put(url_prefix + '/packs/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 405

    def test_add_packs_with_compulsory_payload_value(self, client, url_prefix, token, packs, queries):
        """
        Test-case with compulsory payloads values and with existing packs and queries data,
        expected output:- status is success and pack_id
        """
        payload = {
            'name': 'pytest_pack',
            'queries': {
                'test_query': {
                    'query': 'select * from osquery_info;',
                    'interval': 30
                }
            }
        }
        resp = client.post(url_prefix + '/packs/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['pack_id'] == 1

    def test_add_packs_with_all_payload_value(self, client, url_prefix, token, packs, queries):
        """
        Test-case with all payloads values and with existing packs and queries data,
        expected output:- status is success and pack_id
        """
        payload = {
            'name': 'pytest_pack',
            'queries': {
                'test_query': {
                    'query': 'select * from osquery_info;', 'interval': 30
                }
            }, "tags": "foo,foobar", "category": 'Monitoring',
            "platform": 'linux', "version": '2.0', "description": 'pytest_pack', "shard": 2
        }
        resp = client.post(url_prefix + '/packs/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['pack_id'] == 1

    def test_add_packs_with_all_payload_value_with_invalid_patform(self, client, url_prefix, token, packs, queries):
        """
        Test-case with all payloads values with invalid platform value
        and with existing packs and queries data,
        expected output:- status_code is 400
        """
        payload = {
            'name': 'pytest_pack',
            'queries': {
                'test_query': {
                    'query': 'select * from osquery_info;', 'interval': 30
                }
            }, "tags": "foo,foobar", "category": 'Monitoring',
            "platform": 'abc', "version": '2.0', "description": 'pytest_pack', "shard": 2
        }
        resp = client.post(url_prefix + '/packs/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 400

    def test_add_packs_with_all_payload_value_with_invalid_category(self, client, url_prefix, token, packs, queries):
        """
        Test-case with all payloads values with invalid category value
        and without existing packs and queries data,
        expected output:- status_code is 400
        """
        payload = {
            'name': 'pytest_pack',
            'queries': {
                'test_query': {
                    'query': 'select * from osquery_info;', 'interval': 30
                }
            }, "tags": "foo,foobar", "category": 'testing',
            "platform": 'linux', "version": '2.0', "description": 'pytest_pack', "shard": 2
        }
        resp = client.post(url_prefix + '/packs/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 400


class TestGetPackById:

    def test_get_pack_by_invalid_id(self, client, url_prefix, token):
        """
        Test-case with invalid pack_id which is passing through url,
        and without existing packs and queries data,
        expected output:- status is failure
        """
        resp = client.get(url_prefix + '/packs/4', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_pack_by_valid_id(self, client, url_prefix, token):
        """
        Test-case with valid pack_id which is passing through url,
        and without existing packs and queries data,
        expected output:- status is failure
        """
        resp = client.get(url_prefix + '/packs/4', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_pack_by_id_with_invalid_method(self, client, url_prefix, token, packs, queries):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.post(url_prefix + '/packs/1', headers={'x-access-token': token})
        assert resp.status_code == 405

    def test_get_packs_by_invalid_id(self, client, url_prefix, token, packs, queries):
        """
        Test-case with invalid pack_id which is passing through url,
        and with existing packs and queries data,
        expected output:- status is fai lure
        """
        resp = client.get(url_prefix + '/packs/4', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_packs_by_valid_id(self, client, url_prefix, token, packs, queries, tag):
        """
        Test-case with valid pack_id which is passing through url,
        and with existing packs and queries data,
        expected output:- status is success, and
        packs data in dictionary format with key values of tags and queries, etc.
        """
        p = packs_dao.get_pack_by_name('pytest_pack')
        t = Tag.query.filter(Tag.value == 'test').first()
        q = queries_dao.get_query_by_name('test_query')
        p.queries.append(q)
        p.tags.append(t)
        resp = client.get(url_prefix + '/packs/1', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['id'] == 1
        assert response_dict['data']['tags'] == ['test']
        assert response_dict['data']['queries'] == ['test_query']


class TestGetListTagsOfPacks:

    def test_get_list_of_packs_with_invalid_pack_name(self, client, url_prefix, token):
        """
        Test-case with invalid pack name which is passing through url
        and without existing packs and tags data,
        expected output:- status is failure
        """
        resp = client.get(url_prefix + '/packs/test/tags', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_list_of_packs_with_valid_pack_name(self, client, url_prefix, token):
        """
        Test-case with valid pack name which is passing through url
        and without existing packs and tags data,
        expected output:- status is failure
        """
        resp = client.get(url_prefix + '/packs/pytest_pack/tags', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_list_of_packs_with_invalid_pack_id(self, client, url_prefix, token):
        """
        Test-case with invalid pack id which is passing through url
        and without existing packs and tags data,
        expected output:- status is failure
        """
        resp = client.get(url_prefix + '/packs/3/tags', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_list_of_packs_with_valid_pack_id(self, client, url_prefix, token):
        """
        Test-case with valid pack id which is passing through url
        and without existing packs and tags data,
        expected output:- status is failure
        """
        resp = client.get(url_prefix + '/packs/1/tags', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_list_of_packs_with_invalid_method(self, client, url_prefix, token, packs, tag):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.put(url_prefix + '/packs/test/tags', headers={'x-access-token': token})
        assert resp.status_code == 405

    def test_get_list_of_pack_with_invalid_pack_name(self, client, url_prefix, token, packs, tag):
        """
        Test-case with invalid pack name which is passing through url
        and with existing packs and tags data,
        expected output:- status is failure
        """
        p = packs_dao.get_pack_by_name('pytest_pack')
        t = Tag.query.filter(Tag.value == 'test').first()
        p.tags.append(t)
        resp = client.get(url_prefix + '/packs/test/tags', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_list_of_pack_with_valid_pack_name(self, client, url_prefix, token, packs, tag):
        """
        Test-case with valid pack name which is passing through url
        and with existing packs and tags data,
        expected output:- status is success, and
        list of tag's name
        """
        p = packs_dao.get_pack_by_name('pytest_pack')
        t = Tag.query.filter(Tag.value == 'test').first()
        p.tags.append(t)
        resp = client.get(url_prefix + '/packs/pytest_pack/tags', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == ['test']

    def test_get_list_of_pack_with_invalid_pack_id(self, client, url_prefix, token, packs, tag):
        """
        Test-case with invalid pack id which is passing through url
        and with existing packs and tags data,
        expected output:- status is failure
        """
        p = packs_dao.get_pack_by_name('pytest_pack')
        t = Tag.query.filter(Tag.value == 'test').first()
        p.tags.append(t)
        resp = client.get(url_prefix + '/packs/3/tags', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_list_of_pack_with_valid_pack_id(self, client, url_prefix, token, packs, tag):
        """
        Test-case with valid pack id which is passing through url
        and with existing packs and tags data,
        expected output:- status is success, and
        list of tag's name
        """
        p = packs_dao.get_pack_by_name('pytest_pack')
        t = Tag.query.filter(Tag.value == 'test').first()
        p.tags.append(t)
        resp = client.get(url_prefix + '/packs/1/tags', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == ['test']


class TestAddTagsOfPack:
    """
    Test-case inside this block where this payload value is used,
    this is compulsory payload value of any string type,
    if value is none or anything  other than string,
    it will return 400 i.e., bad request
    """
    payload = {'tag': None,}

    def test_add_pack_of_tags_without_payload(self, client, url_prefix, token):
        """
        Test-case without payload and without existing packs and tags data,
        pack name/id is passing through url,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/packs/test/tags', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_add_pack_of_tags_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload is empty dictionary and without existing packs and tags data,
        pack id/name is passing through url,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/packs/1/tags', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_add_pack_of_tags_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with payload value is none and without existing packs and tags data,
        pack name/id is passing through url,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/packs/test12/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_add_pack_of_tags_with_valid_payload_value(self, client, url_prefix, token):
        """
        Test-case with valid payload value and without existing packs and tags data,
        pack name/id is passing through url,
        expected output:- status is failure
        """
        self.payload['tag'] = 'test-dummydata123'
        resp = client.post(url_prefix + '/packs/1/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_add_pack_of_tags_with_invalid_method(self, client, url_prefix, token):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.put(url_prefix + '/packs/test/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_add_pack_of_tags_with_invalid_pack_name_or_id(self, client, url_prefix, token, packs, tag):
        """
        Test-case with valid payload value and with existing packs and tags data,
        pack name/id is passing through url,
        expected output:- status is failure
        """
        self.payload['tag'] = 'test-dummy'
        resp = client.post(url_prefix + '/packs/test12/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_add_pack_of_tags_with_valid_pack_name_or_id(self, client, url_prefix, token, packs, tag):
        """
        Test-case with valid payload value and with existing packs and tags data,
        pack name/id is passing through url,
        expected output:- status is success
        """
        self.payload['tag'] = 'test'
        resp = client.post(url_prefix + '/packs/1/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        p = packs_dao.get_pack_by_id(1)
        assert [tag.value for tag in p.tags] == ['test']


class TestDeleteTagsOfPack:
    """
    Test-case inside this block where this payload value is used,
    this is compulsory payload value of any string type,
    if value is none or anything  other than string,
    it will return 400 i.e., bad request
    """
    payload = {'tag': None,}

    def test_delete_pack_of_tags_without_payload(self, client, url_prefix, token):
        """
        Test-case without payload and without existing packs and tags data,
        pack name/id is passing through url,
        expected output:- status_code is 400
        """
        resp = client.delete(url_prefix + '/packs/test/tags', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_delete_pack_of_tags_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload is empty dictionary and without existing packs and tags data,
        pack id/name is passing through url,
        expected output:- status_code is 400
        """
        resp = client.delete(url_prefix + '/packs/1/tags', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_delete_pack_of_tags_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with payload value is none and without existing packs and tags data,
        pack name/id is passing through url,
        expected output:- status_code is 400
        """
        resp = client.delete(url_prefix + '/packs/test12/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_delete_pack_of_tags_with_valid_payload_value(self, client, url_prefix, token):
        """
        Test-case with valid payload value and without existing packs and tags data,
        pack name/id is passing through url,
        expected output:- status is failure
        """
        self.payload['tag'] = 'test-dummydata123'
        resp = client.delete(url_prefix + '/packs/1/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_delete_pack_of_tags_with_invalid_method(self, client, url_prefix, token, packs, tag):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.put(url_prefix + '/packs/test/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_delete_pack_of_tags_with_invalid_pack_name_or_id(self, client, url_prefix, token, packs, tag):
        """
        Test-case with valid payload value and with existing packs and tags data,
        pack name/id is passing through url,
        expected output:- status is failure
        """
        self.payload['tag'] = 'test-dummy'
        resp = client.delete(url_prefix + '/packs/test12/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_delete_pack_of_tags_with_valid_pack_name_or_id(self, client, url_prefix, token, packs, tag):
        """
        Test-case with valid payload value and with existing packs and tags data,
        pack name/id is passing through url,
        expected output:- status is success
        """
        self.payload['tag'] = 'test'
        p = packs_dao.get_pack_by_id(1)
        t = Tag.query.filter(Tag.value == 'test').first()
        p.tags.append(t)
        resp = client.delete(url_prefix + '/packs/1/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        p = packs_dao.get_pack_by_id(1)
        assert [tag.value for tag in p.tags] == []

    def test_delete_pack_of_tags_with_invalid_tag_value(self, client, url_prefix, token, packs, tag):
        """
        Test-case with invalid payload value and with existing packs and tags data,
        pack name/id is passing through url,
        expected output:- status is failure
        """
        self.payload['tag'] = 'test12'
        resp = client.delete(url_prefix + '/packs/1/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'


class TestUploadPack:
    """
    Test-case inside this block where these payloads are used,
    file is compulsory payload values,
    category have choices that are:- Intrusion Detection/Monitoring/Compliance
    and Management/Forensics and Incident Response/General/Others) we have to choose any one,
    if we didn't give valid category and for file value file object or
    if we pass none value then it will return 400 i.e., bad request, and

    """
    payload = {'file': None, 'category': None}

    def test_upload_pack_with_empty_packs_data(self, client, url_prefix, token):
        """
        Test-case without payloads, and without existing packs, tags, and queries data,
        expected output:- status code is 400
        """
        resp = client.post(url_prefix + '/packs/upload', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_upload_pack_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payloads are empty dictionary,
        and without existing packs, tags, and queries data,
        expected output:- status code is 400
        """
        resp = client.post(url_prefix + '/packs/upload', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_upload_pack_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with payloads are None,
        and without existing packs, tags, and queries data,
        expected output:- status code is 400
        """
        resp = client.post(url_prefix + '/packs/upload', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 400

    def test_upload_pack_with_only_payload_file_value(self, client, url_prefix, token):
        """
        Test-case with only payloads value of file i.e., file object ,
        and without existing packs, tags, and queries data,
         expected output:- status is success, and
        pack_id i.e., 1 in this case
        """
        payload = {}
        payload['file'] = open(os.getcwd() + '/tests/TestUtilFiles/packs_test.json', 'rb')
        resp = client.post(url_prefix + '/packs/upload', headers={'x-access-token': token}, data=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['pack_id'] == 1

    def test_upload_pack_with_all_payload_value(self, client, url_prefix, token):
        """
        Test-case with all payloads value,
        and without existing packs, tags, and queries data,
        expected output:- status is success, and
        pack_id i.e., 1 in this case
        """
        self.payload['file'] = open(os.getcwd() + '/tests/TestUtilFiles/packs_test.json', 'rb')
        self.payload['category'] = 'Intrusion Detection'
        resp = client.post(url_prefix + '/packs/upload', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['pack_id'] == 1

    def test_upload_pack_with_invalid_value_of_category(self, client, url_prefix, token):
        """
        Test-case with all payloads value,
        and without existing packs, tags, and queries data,
        expected output:- status_code is 400
        """
        self.payload['file'] = open(os.getcwd() + '/tests/TestUtilFiles/packs_test.json', 'rb')
        self.payload['category'] = 'abc'
        resp = client.post(url_prefix + '/packs/upload', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 400

    def test_upload_pack_with_invalid_method(self, client, url_prefix, token, packs, queries, tag):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        self.payload['file'] = open(os.getcwd() + '/tests/TestUtilFiles/packs_test.json', 'rb')
        resp = client.get(url_prefix + '/packs/upload', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 405

    def test_upload_packs_with_invalid_value_of_category(self, client, url_prefix, token, packs, queries, tag):
        """
        Test-case with all payloads value,
        and with existing packs, tags, and queries data,
        expected output:- status_code is 400
        """
        self.payload['file'] = open(os.getcwd() + '/tests/TestUtilFiles/packs_test.json', 'rb')
        self.payload['category'] = 'abc'
        resp = client.post(url_prefix + '/packs/upload', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 400

    def test_upload_pack_with_packs_data(self, client, url_prefix, token, packs, queries, tag):
        """
        Test-case with all payloads value,
        and without existing packs, tags, and queries data,
        expected output:- status is success, and
        pack_id i.e., 2 in this case
        """
        self.payload['file'] = open(os.getcwd() + '/tests/TestUtilFiles/packs_test.json', 'rb')
        self.payload['category'] = 'Compliance and Management'
        resp = client.post(url_prefix + '/packs/upload', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['pack_id'] == 2

    def test_upload_pack_with_packs_data_with_inavlid_json_file(self, client, url_prefix, token, packs, queries, tag):
        """
        Test-case with all payloads value,
        and without existing packs, tags, and queries data,
        expected output:- status is failure
        """
        self.payload['file'] = open(os.getcwd() + '/tests/TestUtilFiles/eicar.yara', 'rb')
        self.payload['category'] = 'Compliance and Management'
        resp = client.post(url_prefix + '/packs/upload', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'


class TestPackRemoved:

    def test_pack_removed_by_id_without_pack_data(self, client, url_prefix, token):
        """
        Test-case with valid/invalid pack_id and without existing packs data,
        expected output:- status is failure
        """
        resp = client.delete(url_prefix + '/packs/1/delete', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_pack_removed_by_name_without_pack_data(self, client, url_prefix, token):
        """
        Test-case with valid/invalid pack_name and without existing packs data,
        expected output:- status is failure
        """
        resp = client.delete(url_prefix + '/packs/pytest_pack/delete', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_pack_removed_with_invalid_method(self, client, url_prefix, token, packs):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.get(url_prefix + '/packs/1/delete', headers={'x-access-token': token})
        assert resp.status_code == 405

    def test_pack_removed_by_invalid_id_with_pack_data(self, client, url_prefix, token, packs):
        """
        Test-case with invalid pack_id and with existing packs data,
        expected output:- status is failure
        """
        resp = client.delete(url_prefix + '/packs/5/delete', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_pack_removed_by_valid_id_with_pack_data(self, client, url_prefix, token, packs):
        """
        Test-case with valid pack_id and with existing packs data,
        expected output:- status is Success
        """
        resp = client.delete(url_prefix + '/packs/1/delete', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'Success'
        assert packs_dao.get_pack_by_id(1) is None

    def test_pack_removed_by_invalid_name_with_pack_data(self, client, url_prefix, token, packs):
        """
        Test-case with invalid pack_name and with existing packs data,
        expected output:- status is failure
        """
        resp = client.delete(url_prefix + '/packs/test_pack/delete', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_pack_removed_by_valid_name_with_pack_data(self, client, url_prefix, token, packs):
        """
        Test-case with valid pack_name and with existing packs data,
        expected output:- status is Success
        """
        resp = client.delete(url_prefix + '/packs/pytest_pack/delete', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'Success'
        assert response_dict['message'] == 'Successfully removed the Pack'
        assert packs_dao.get_pack_by_name('pytest_pack') is None
