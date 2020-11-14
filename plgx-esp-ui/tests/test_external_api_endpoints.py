"""
All Test-Case required client, url_prefix and token,
and these all we need to just pass as parameters in the function.
"""

import json


class TestGetAuthToken:
    """
    Test-case inside where these payloads are used,
    all are compulsory payload values and of str type,
    so if value is not passed or passed any other type
    which is not specified then it will return 400 i.e., bad request
    """
    payload = {'username': 'admin', 'password': 'admin'}

    def test_get_auth_token(self, client, url_prefix, user):
        """
        Test-case with valid payload value of username and
        password and with existing user data,
        expected output:- status_code is 200,
        and a valid token and type of token is of str type
        """
        resp = client.post(url_prefix + '/login', headers={'Accept': None}, json=self.payload)
        assert resp.status_code == 200
        assert type(json.loads(resp.data)['token']) is str

    def test_get_auth_token_with_invalid_method(self, client, url_prefix, user):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.get(url_prefix + '/login', headers={'Accept': None}, json=self.payload)
        assert resp.status_code == 405

    def test_get_auth_token_bad_request(self, client, url_prefix, user):
        """
        Test-case with user data but empty dict as payload value,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/login', headers={'Accept': None}, json={})
        assert resp.status_code == 400

    def test_get_auth_token_with_invalid_username(self, client, url_prefix, user):
        """
        Test-case with invalid username and valid password, and with existing user data
        expected output:- status_code is 302
        """
        self.payload['username'] = 'foobar'
        resp = client.post(url_prefix + '/login', headers={'Accept': None}, json=self.payload)
        assert resp.status_code == 302

    def test_get_auth_token_with_invalid_password(self, client, url_prefix, user):
        """
        Test-case with valid username and invalid password and with existing user data,
        expected output:- status_code is 302
        """
        self.payload['username'] = 'admin'
        self.payload['password'] = 'foobar'
        resp = client.post(url_prefix + '/login', headers={'Accept': None}, json=self.payload)
        assert resp.status_code == 302

    def test_get_auth_token_with_invalid_username_and_password(self, client, url_prefix, user):
        """
        Test-case with invalid username and password, and with existing user data
        expected output:- status_code is 302
        """
        self.payload['username'] = 'foobar'
        self.payload['password'] = 'foobar'
        resp = client.post(url_prefix + '/login', headers={'Accept': None}, data=json.dumps(self.payload))
        assert resp.status_code == 302

    def test_get_auth_token_with_payload_value_none(self, client, url_prefix, user):
        """
        Test-case with username and password is None, and with existing user data
        expected output:- status_code is 302
        """
        self.payload['username'] = None
        self.payload['password'] = None
        resp = client.post(url_prefix + '/login', headers={'Accept': None}, data=json.dumps(self.payload))
        assert resp.status_code == 302

    def test_get_auth_token_with_empty_payload(self, client, url_prefix, user):
        """ Test-case with no username and valid password """
        resp = client.post(url_prefix + '/login', headers={'Accept': None}, data={})
        assert resp.status_code == 400


class TestLogoutMethod:

    def test_logout_method_with_token(self, client, url_prefix, token):
        """
        Test-case with valid token,
        expected output:- status is success
        """
        resp = client.post(url_prefix + '/logout', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'

    def test_logout_method_with_invalid_method(self, client, url_prefix, token):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.get(url_prefix + '/logout')
        assert resp.status_code == 405