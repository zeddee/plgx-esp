"""
All Test-Case required client, url_prefix and token,
and these all we need to just pass as parameters in the function.
"""

import json
from flask_restplus import marshal

from polylogyx.dao import tags_dao, packs_dao, hosts_dao, queries_dao
from polylogyx.models import Tag
from polylogyx.wrappers import tag_wrappers, query_wrappers, pack_wrappers


class TestTagsList:
    """
    Test-case inside this block where these payloads are used,
    all are optional value and start, limit are of positive natural number type,
    while searchterm is of str type and default value is empty str,
    so if types of values passed that is not matched with specified type,
    then it will return 400 i.e., bad request
    """
    payload = {'start': None, "limit": None, "searchterm": ''}

    def test_get_tag_list_without_payload(self, client, url_prefix, token):
        """
        Test-case without paylods and without existing node, queries, tags and file_path,
        expected output:- status is success, and
        count, total_count and resultant data
        """
        resp = client.get(url_prefix + '/tags', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 0
        assert response_dict['data']['total_count'] == 0
        assert response_dict['data']['results'] == []

    def test_get_tag_list_with_empty_payload(self, client, url_prefix, token):
        """
        Test-case with paylod is empty dictionary and
        without existing node, queries, tags and file_path,
        expected output:- status is success, and
        count, total_count and resultant data
        """
        resp = client.get(url_prefix + '/tags', headers={'x-access-token': token}, json={})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 0
        assert response_dict['data']['total_count'] == 0
        assert response_dict['data']['results'] == []

    def test_get_tag_list_with_payload(self, client, url_prefix, token):
        """
        Test-case with paylod values are none and empty str
        and without existing node, queries, tags and file_path,
        expected output:- status is success, and
        count, total_count and resultant data
        """
        self.payload['start'] = 0
        self.payload['limit'] = 5
        self.payload['searchterm'] = "abc"
        resp = client.get(url_prefix + '/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 0
        assert response_dict['data']['total_count'] == 0
        assert response_dict['data']['results'] == []

    def test_get_tag_list_invalid_method(self, client, url_prefix, token):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.put(url_prefix + '/tags', headers={'x-access-token': token})
        assert resp.status_code == 405

    def test_get_tag_list_without_payload_with_data(self, client, url_prefix, token, tag):
        """
        Test-case without paylods and with existing node, queries, tags and file_path,
        expected output:- status is success, and
        count, total_count and resultant data
        """
        resp = client.get(url_prefix + '/tags', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        list_dict_data = [
            {
                'value': tag.value, 'nodes': [node.host_identifier for node in tag.nodes],
                'packs': [pack.name for pack in tag.packs],
                'queries': [query.name for query in tag.queries],
                'file_paths': tag.file_paths
            }
            for tag in tags_dao.get_all_tags()
        ]
        data = marshal(list_dict_data, tag_wrappers.tag_wrapper)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        assert response_dict['data']['results'] == data

    def test_get_tag_list_without_empty_payload_with_data(self, client, url_prefix, token, tag):
        """
        Test-case with paylod is empty dictionary and
        with existing node, queries, tags and file_path,
        expected output:- status is success, and
        count, total_count and resultant data
        """
        resp = client.get(url_prefix + '/tags', headers={'x-access-token': token}, json={})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        list_dict_data = [
            {
                'value': tag.value, 'nodes': [node.host_identifier for node in tag.nodes],
                'packs': [pack.name for pack in tag.packs],
                'queries': [query.name for query in tag.queries],
                'file_paths': tag.file_paths
            }
            for tag in tags_dao.get_all_tags()
        ]
        data = marshal(list_dict_data, tag_wrappers.tag_wrapper)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        assert response_dict['data']['results'] == data

    def test_get_tag_list_with_payload_with_data(self, client, url_prefix, token, tag):
        """
        Test-case with all payload value and
        without existing node, queries, tags and file_path,
        expected output:- status is success, and
        count, total_count and resultant data
        """
        self.payload['start'] = 0
        self.payload['limit'] = 5
        self.payload['searchterm'] = "abc"
        resp = client.get(url_prefix + '/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 0
        assert response_dict['data']['total_count'] == 1
        assert response_dict['data']['results'] == []

    def test_get_tag_list_with_valid_payload_with_data(self, client, url_prefix, token, tag):
        """
        Test-case with paylod values are none and empty str
        and with existing node, queries, tags and file_path,
        expected output:- status is success, and
        count, total_count and resultant data
        """
        self.payload['start'] = 0
        self.payload['limit'] = 5
        self.payload['searchterm'] = "test"
        resp = client.get(url_prefix + '/tags', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        list_dict_data = [
            {
                'value': tag.value, 'nodes': [node.host_identifier for node in tag.nodes],
                'packs': [pack.name for pack in tag.packs],
                'queries': [query.name for query in tag.queries],
                'file_paths': tag.file_paths
            }
            for tag in tags_dao.get_all_tags()
        ]
        data = marshal(list_dict_data, tag_wrappers.tag_wrapper)
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        assert response_dict['data']['total_count'] == 1
        assert response_dict['data']['results'] == data


class TestAddTag:
    """
    Test-case inside this block where this payload value is used,
    this payload is compulsory value and of str type,
    so if value is not passed or passed  any other value than string type,
    it will return 400 i.e., bad request
    """
    payload = {'tag': ''}

    def test_tag_without_payload(self, client, url_prefix, token):
        """
        Test-case without payloads and without existing tag data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/tags/add', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_tag_with_empty_payload(self, client, url_prefix, token):
        """
        Test-case without payloads and without existing tag data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/tags/add', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_tag_with_empty_str_payload(self, client, url_prefix, token):
        """
        Test-case with payloads value is empty str and without existing tag data,
        expected output:- status is failure
        """
        resp = client.post(url_prefix + '/tags/add', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_tag_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with payloads value is none and without existing tag data,
        expected output:- status_code is 400
        """
        self.payload['tag'] = None
        resp = client.post(url_prefix + '/tags/add', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_tag_with_invalid_method(self, client, url_prefix, token):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.put(url_prefix + '/tags/add', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_tag_with_data(self, client, url_prefix, token, tag):
        """
        Test-case with payloads value and with existing tag data,
        expected output:- status is failure
        """
        self.payload['tag'] = 'test'
        resp = client.post(url_prefix + '/tags/add', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'


class TestDeleteTag:
    """
    Test-case inside this block where this payload value is used,
    this payload is compulsory value and of str type,
    so if value is not passed or passed  any other value than string type,
    it will return 400 i.e., bad request
    """
    payload = {'tag': ''}

    def test_tag_without_payload(self, client, url_prefix, token):
        """
        Test-case without payloads and without existing tag data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/tags/delete', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_tag_with_empty_payload(self, client, url_prefix, token):
        """
        Test-case without payloads and without existing tag data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/tags/delete', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_tag_with_empty_str_payload(self, client, url_prefix, token):
        """
        Test-case with payloads value is empty str and without existing tag data,
        expected output:- status is failure
        """
        resp = client.post(url_prefix + '/tags/delete', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'

    def test_tag_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with payloads value is none and without existing tag data,
        expected output:- status_code is 400
        """
        self.payload['tag'] = None
        resp = client.post(url_prefix + '/tags/delete', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_tag_with_invalid_method(self, client, url_prefix, token):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.put(url_prefix + '/tags/delete', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_tag_with_data(self, client, url_prefix, token, tag):
        """
        Test-case with payloads value and with existing tag data,
        expected output:- status is success
        """
        self.payload['tag'] = 'test'
        resp = client.post(url_prefix + '/tags/delete', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'


class TestTaggedList:
    """
    Test-case inside this block where this payload value is used,
    this payload is compulsory value and of str type and here tag name
    may more than one is also possible but that should be comma separated
    in str type, so if value is not passed or passed
    any other value than string type, it will return 400 i.e., bad request
    """
    payload = {'tags': None}

    def test_tagged_tags_without_payload(self, client, url_prefix, token):
        """
        Test-case without payload, and
        without existing tag, node, packa and queries data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/tags/tagged', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_tagged_tags_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload is empty dictionary, and
        without existing tag, node, packa and queries data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/tags/tagged', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_tagged_tags_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with payload values is none, and
        without existing tag, node, packa and queries data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/tags/tagged', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_tagged_tags_with_single_tag_name(self, client, url_prefix, token):
        """
        Test-case with valid single tag name, and
        without existing tag node, packa and queries data,
        expected output:- status is success,
        and resultant_data of hosts, packs and queries values are mepty list in this case.
        """
        self.payload['tags'] = 'test'
        resp = client.post(url_prefix + '/tags/tagged', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == {"hosts": [], "packs": [], "queries": []}

    def test_tagged_tags_with_multiple_tag_name(self, client, url_prefix, token):
        """
        Test-case with valid multiple tag name, and
        without existing tag node, packa and queries data,
        expected output:- status is success,
        and resultant_data of hosts, packs and queries values are mepty list in this case.
        """
        self.payload['tags'] = 'test,test1'
        resp = client.post(url_prefix + '/tags/tagged', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == {"hosts": [], "packs": [], "queries": []}

    def test_tagged_tag_with_invalid_method(self, client, url_prefix, token, tag):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        self.payload['tags'] = 'test'
        resp = client.get(url_prefix + '/tags/tagged', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_tagged_tag_with_single_tag_name(self, client, url_prefix, token, node, packs, queries, tag):
        """
        Test-case with valid single tag name,
        and with existing tag, node, packa and queries data,
        expected output:- status is success,
        and resultant_data of hosts, packs and queries.
        """
        self.payload['tags'] = 'test'
        packs = packs_dao.get_pack_by_name('pytest_pack')
        nod = hosts_dao.get_node_by_host_identifier('foobar')
        query = queries_dao.get_query_by_name('test_query')
        # create_tags(*self.payload['tags'].split(','))
        t = Tag.query.filter(Tag.value == 'test').first()
        packs.tags.append(t)
        nod.tags.append(t)
        query.tags.append(t)
        resp = client.post(url_prefix + '/tags/tagged', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        data = get_tagged_list(['test'])
        assert response_dict['data']['hosts'] == data['hosts']
        assert response_dict['data']['packs'] == data['packs']
        assert response_dict['data']['queries'] == data['queries']

    def test_tagged_tag_with_multiple_tag_name(self, client, url_prefix, token, node, packs, queries, tag):
        """
        Test-case with valid multiple tag name,
        and with existing tag, node, packa and queries data,
        expected output:- status is success,
        and resultant_data of hosts, packs and queries.
        """
        self.payload['tags'] = 'test,test1'
        packs = packs_dao.get_pack_by_name('pytest_pack')
        nod = hosts_dao.get_node_by_host_identifier('foobar')
        query = queries_dao.get_query_by_name('test_query')
        # create_tags(*self.payload['tags'].split(','))
        t = Tag.query.filter(Tag.value == 'test').first()
        packs.tags.append(t)
        nod.tags.append(t)
        query.tags.append(t)
        resp = client.post(url_prefix + '/tags/tagged', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        data = get_tagged_list(['test', 'test1'])
        assert response_dict['data']['hosts'] == data['hosts']
        assert response_dict['data']['packs'] == data['packs']
        assert response_dict['data']['queries'] == data['queries']


def get_tagged_list(tags):
    hosts = [node.get_dict() for node in hosts_dao.get_tagged_nodes(tags) if
             node.state != node.DELETED and node.state != node.REMOVED]

    packs_queryset = packs_dao.get_tagged_packs(tags)
    packs = marshal(packs_queryset, pack_wrappers.pack_wrapper)
    for index in range(len(packs)):
        packs[index]['tags'] = [tag.to_dict() for tag in packs_queryset[index].tags]
        packs[index]['queries'] = marshal(packs_queryset[index].queries, query_wrappers.query_wrapper)
        for query_index in range(len(packs_queryset[index].queries)):
            packs[index]['queries'][query_index]['tags'] = [tag.to_dict() for tag in
                                                            packs_queryset[index].queries[query_index].tags]
            packs[index]['queries'][query_index]['packs'] = [pack.name for pack in
                                                             packs_queryset[index].queries[query_index].packs]

    queries_qs = queries_dao.get_tagged_queries(tags)
    queries = marshal(queries_qs, query_wrappers.query_wrapper)
    for i in range(len(queries)):
        queries[i]['tags'] = [tag.to_dict() for tag in queries_qs[i].tags]
        queries[i]['packs'] = [pack.name for pack in queries_qs[i].packs]

    return {"hosts": hosts, "packs": packs, "queries": queries}