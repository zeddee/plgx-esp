#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json, random

class ApiError(Exception):
    pass

class BaseApiTest:
    '''Base Api Test Class'''

    def __init__(self, base="https://localhost:5000/services/api/v0", username="admin", password="admin", proxies=None):
        ''' sets variables including the headers '''
        self.base = base
        self.username = username
        self.password = password
        self.proxies = proxies
        token = self.fetch_token()
        self.headers_post = {'x-access-token': token, 'content-type': 'application/json'}
        self.headers_get = {'x-access-token': token}
        obj_utils = TestUtils()
        self.allNodes = obj_utils.get_list_of_all_host_ids()
        self.allQueries = obj_utils.get_list_of_all_queries()

    def fetch_token(self):
        ''' fetches the token from the login api '''

        url = self.base + '/login'
        request_data = {'username': self.username, 'password': self.password}
        try:
            r = requests.post(url, json=request_data, verify=False)
            response = self._return_response_and_status_code(r)
            if response['response_code'] == 200:
                return response['results']['token']
        except Exception as e:
            raise ApiError(e)

    def get_headers(self):
        return {'headers_post': self.headers_post, 'headers_get': self.headers_get}

    def get_request(self, url, payload=None, timeout=None):
        ''' method to get the data from a url '''

        try:
            if payload: response = requests.get(self.base + url, json=payload, proxies=self.proxies, timeout=timeout,headers=self.headers_get, verify=False)
            else: response = requests.get(self.base + url, proxies=self.proxies, timeout=timeout,headers=self.headers_get, verify=False)
        except requests.RequestException as e:
            return dict(error=str(e))

        return self.handle_response(response)

    def post_request(self, url, payload, timeout=None):
        ''' method to post a data to the url for the payload given '''

        try:
            response = requests.post(self.base + url, json=payload, proxies=self.proxies, timeout=timeout, headers=self.headers_post, verify=False)
        except requests.RequestException as e:
            return dict(error=str(e))

        return self.handle_response(response)

    def validate_status_code_and_success_status(self, result_response):
        assert int(result_response['response_code']) == 200 and 'results' in result_response
        assert result_response['results']['status'] == 'success'
        if 'data' in result_response['results']:
            if not result_response['results']['data']==None:
                if not len(result_response['results']['data']):
                    return None
                else:
                    return (True, result_response['results']['data'])
        else:
            return True

    def validate_status_code_and_failure_status(self, result_response):
        assert int(result_response['response_code']) == 200 and 'results' in result_response
        assert result_response['results']['status'] == 'failure'
        return True

    def handle_response(self, response):
        ''' response will be returned to the call '''
        return json.dumps(self._return_response_and_status_code(response=response))

    def _return_response_and_status_code(self, response, json_results=True):
        """ Output the requests response content or content as json and status code

        :rtype : dict
        :param response: requests response object
        :param json_results: Should return JSON or raw content
        :return: dict containing the response content and/or the status code with error string.
        """
        if response.status_code == requests.codes.ok:
            return dict(results=response.json() if json_results else response.content,
                        response_code=response.status_code)
        elif response.status_code == 400:
            return dict(
                error='package sent is either malformed or not within the past 24 hours.',
                response_code=response.status_code)
        elif response.status_code == 204:
            return dict(
                error='You exceeded the public API request rate limit (4 requests of any nature per minute)',
                response_code=response.status_code)
        elif response.status_code == 403:
            return dict(
                error='You tried to perform calls to functions for which you require a Private API key.',
                response_code=response.status_code)
        elif response.status_code == 404:
            return dict(error='File not found.', response_code=response.status_code)
        else:
            return dict(response_code=response.status_code)


class TestUtils():
    def get_list_of_all_host_ids(self):
        return ["EC2014BA-0186-6871-DF2E-096A7D61D18B"]

    def get_list_of_all_tags(self):
        pass
    def get_list_of_all_queries(self):
        pass
    def get_list_of_all_sql_raw_queries(self):
        pass
    def get_list_of_all_schema_tables(self):
        pass
