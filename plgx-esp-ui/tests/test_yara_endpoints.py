"""
All Test-Case required client, url_prefix and token,
and these all we need to just pass as parameters in the function.
"""

import json, os
from flask import current_app


class TestListYara:

    def test_get_yara_list(self, client, url_prefix, token):
        """
        Test-case to get yara list,
        expected output:- status is success,
        and resultant data is yara file list if present else empty list
        will return as resultant data
        """
        resp = client.get(url_prefix + '/yara', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        data= get_yara_list()
        if data:
            assert response_dict['data'] == data
        else:
            assert response_dict['data'] == []

    def test_get_yara_list_with_invalid_method(self, client, url_prefix, token):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.put(url_prefix + '/yara', headers={'x-access-token': token})
        assert resp.status_code == 405


class TestAddYara:

    """
    Test-case inside this block where these payloads values are used,
    only file value is compulsory payload value of file_object and
    filename is of str type and it's an optional payload value as well as
    location of the args of filename is in headers,
    so if compulsory payload value is not passed or type of payload
    value is not matched with the specified value then it will return
    400 i.e., bad request
    """
    payload = {'file': None}

    def test_add_yara_file_without_payload(self, client, url_prefix, token):
        """
        Test-case without payload,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/yara/add', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_add_yara_file_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload is empty dictionary,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/yara/add', headers={'x-access-token': token}, data={})
        assert resp.status_code == 400

    def test_add_yara_file_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with payload value none,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/yara/add', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 400

    def test_add_invalid_yara_file(self, client, url_prefix, token):
        """
        Test-case with invalid yara file,
        expected output:- status is failure
        """
        payload = {'file': open(os.getcwd() + '/tests/TestUtilFiles/iocs.json', 'rb')}
        resp = client.post(
            url_prefix + '/yara/add',
            headers={'x-access-token': token, 'filename':'eicar2.yara'}, data=payload
        )
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_add_valid_yara_file(self, client, url_prefix, token):
        """
        Test-case works only when if that file is
        not existing what we are sending, and
        directory should have enable permission to read and write and
        also in list.txt file that filename should not be there as well as
        list.txt file also have enabled permission of read and write
        expected output:- status is success
         """
        self.payload['file'] = open(os.getcwd() + '/tests/TestUtilFiles/eicar.yara', 'rb')
        resp = client.post(
            url_prefix + '/yara/add',
            headers={'x-access-token': token, 'filename':'eicar2.yara'}, data=self.payload
        )
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'

    def test_add_valid_yara_file_when_file_exists(self, client, url_prefix, token):
        """
        Test-case when file is already exists,
        expected output:- status is failure
        """
        self.payload['file'] = open(os.getcwd() + '/tests/TestUtilFiles/eicar.yara', 'rb')
        resp = client.post(url_prefix + '/yara/add', headers={'x-access-token': token, 'filename':'eicar.yara'}, data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_add_yara_file_with_invalid_method(self, client, url_prefix, token):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        self.payload['file'] = open(os.getcwd()+'/tests/TestUtilFiles/eicar.yara', 'rb')
        resp = client.put(url_prefix + '/yara/add', headers={'x-access-token': token, 'filename':'eicar.yara'}, data=self.payload)
        assert resp.status_code == 405


class TestViewYara:

    """
    Test-case inside this block where this payload value is used,
    this is compulsory payload value of str type, so if value is not passed or
    passed value type is not str type then it will return 400 i.e., bad request
    """
    payload = {'file_name': None}

    def test_add_yara_file_without_payload(self, client, url_prefix, token):
        """
        Test-case without payload,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/yara/view', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_view_yara_file_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload is empty dictionary,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/yara/view', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_view_yara_file_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with payload value none,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/yara/view', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_view_yara_file(self, client, url_prefix, token):
        """
        Test-case with content in the file,
        expecetd output:- status is success, and
        response data i.e., the content of that particular file
        """
        self.payload['file_name'] = 'eicar.yara'
        resp = client.post(url_prefix + '/yara/view', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        file_path = current_app.config['BASE_URL'] + "/yara/" + 'eicar.yara'
        if os.path.exists(file_path):
            with open(file_path, 'r') as the_file:
                data = the_file.read()
        assert response_dict['data'] == data

    def test_view_yara_when_file_not_present(self, client, url_prefix, token):
        """
        Test-case if file is not present,
        expected output:- status is failure
        """
        self.payload['file_name'] = 'test.yara'
        resp = client.post(url_prefix + '/yara/view', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_view_empty_yara(self, client, url_prefix, token):
        """
        Test-case with empty content in the file,
        expected output:- status is success,
        and resultant data should be empty str in this case
        """
        self.payload['file_name'] = 'empty_eicar.yara'
        resp = client.post(url_prefix + '/yara/view', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == ''

    def test_view_yara_with_invalid_method(self, client, url_prefix, token):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        self.payload['filename'] = 'eicar.yara'
        resp = client.get(url_prefix + '/yara/view', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405


class TestDeleteYara:
    """
   Test-case inside this block where this payload value is used,
   this is compulsory payload value of str type, so if value is not passed or
   passed value type is not str type then it will return 400 i.e., bad request
   """
    payload = {'file_name': None}

    def test_delete_yara_file_without_payload(self, client, url_prefix, token):
        """
        Test-case without payload,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/yara/delete', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_delete_yara_file_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload is empty dictionary,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/yara/delete', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_delete_yara_file_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with payload value none,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/yara/delete', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_delete_yara_file(self, client, url_prefix, token):
        """
        Test-case with valid file_name that is present in the specified location,
        expecetd output:- status is success
        """
        self.payload['file_name'] = 'eicar2.yara'
        resp = client.post(url_prefix + '/yara/delete', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'

    def test_view_yara_when_file_not_present(self, client, url_prefix, token):
        """
        Test-case if file is not present in the specified location,
        expected output:- status is failure
        """
        self.payload['file_name'] = 'test.yara'
        resp = client.post(url_prefix + '/yara/delete', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_view_yara_with_invalid_method(self, client, url_prefix, token):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        self.payload['filename'] = 'eicar.yara'
        resp = client.get(url_prefix + '/yara/delete', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405


def get_yara_list():
    file_list = []
    for (dirpath, dirnames, filenames) in os.walk(current_app.config['BASE_URL'] + "/yara/"):
        file_list.extend(filenames)
        break
    if "list.txt" in file_list:
        file_list.remove("list.txt")
    return file_list
