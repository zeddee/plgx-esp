"""
All Test-Case required client, url_prefix and token,
and these all we need to just pass as parameters in the function.
"""

import json

from polylogyx.dao import settings_dao
from tests.factories import SettingsFactory


class TestChangePassword:
    """
    All Test-cases inside this block where these payloads are going to be used,
    these all values are compulsory value an dof str type, if we don't pass these values, it will
    return 400 error i.e., bad request
    """
    payload = {'old_password': None, 'new_password': None, 'confirm_new_password': None}

    def test_change_password_without_payloads(self, client, url_prefix, token):
        """
        Test-case without payloads,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/management/changepw', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_change_password_with_payloads_is_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payloads is empty dict,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/management/changepw', headers={'x-access-token': token},
                          json={})
        assert resp.status_code == 400

    def test_change_password_with_payloads_val_none(self, client, url_prefix, token):
        """
        Test-case with payloads values are None,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/management/changepw', headers={'x-access-token': token},
                          json=self.payload)
        assert resp.status_code == 400

    def test_change_password_with_payloads_val_empty_str(self, client, url_prefix, token):
        """
        Test-case with payloads values are empty str,
        expected output:- status is failure
        """
        self.payload['old_password'] = ''
        self.payload['new_password'] = ''
        self.payload['confirm_new_password'] = ''
        resp = client.post(url_prefix + '/management/changepw', headers={'x-access-token': token},
                          json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_change_password_with_invalid_old_password(self, client, url_prefix, token):
        """
        Test-case with payloads values invalid old_password,
        new_password and confirm_passwird are empty str,
        expected output:- status is failure
        """
        self.payload['old_password'] = 'testing'
        self.payload['new_password'] = ''
        self.payload['confirm_new_password'] = ''
        resp = client.post(url_prefix + '/management/changepw', headers={'x-access-token': token},
                          json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_change_password_with_valid_old_password(self, client, url_prefix, token):
        """
        Test-case with payloads values valid old_password,
        new_password and confirm_passwird are empty str,
        expected output:- status is failure
        """
        self.payload['old_password'] = 'admin'
        self.payload['new_password'] = ''
        self.payload['confirm_new_password'] = ''
        resp = client.post(url_prefix + '/management/changepw', headers={'x-access-token': token},
                          json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_change_password_with_new_pass_and_confirm_new_pass_not_equal(self, client, url_prefix, token):
        """
        Test-case with payloads values valid old_password,
        but new_password and confirm_passwird are not equal,
        expected output:- status is failure
        """
        self.payload['old_password'] = 'admin'
        self.payload['new_password'] = 'admin12'
        self.payload['confirm_new_password'] = 'admin123'
        resp = client.post(url_prefix + '/management/changepw', headers={'x-access-token': token},
                          json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_change_password_with_invalid_method(self, client, url_prefix, token):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.get(url_prefix + '/management/changepw', headers={'x-access-token': token})
        assert resp.status_code == 405

    def test_change_password_with_old_and_new_pass_are_same(self, client, url_prefix, token):
        """
        Test-case with payloads values valid old_password,
        but old_password, new_password and confirm_new_password are equal,
        expected output:- status is failure
        """
        self.payload['old_password'] = 'admin'
        self.payload['new_password'] = 'admin'
        self.payload['confirm_new_password'] = 'admin'
        resp = client.post(url_prefix + '/management/changepw', headers={'x-access-token': token},
                          json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_change_password(self, client, url_prefix, token):
        """
        Test-case with payloads values valid old_password,
        new_password and confirm_passwird are equal,
        expected output:- status is success
        """
        self.payload['old_password'] = 'admin'
        self.payload['new_password'] = 'admin@123'
        self.payload['confirm_new_password'] = 'admin@123'
        resp = client.post(url_prefix + '/management/changepw', headers={'x-access-token': token},
                          json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'


class TestGetPurgeDurationUpdate:

    def test_get_purge_duration_update_without_data(self, client, url_prefix, token):
        """
        Test-Case without existing Settings Data,
        expected output is: status is failure
        """
        resp = client.get(url_prefix + '/management/purge/update', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_purge_duration_update_wit_invalid_method(self, client, url_prefix, token):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.put(url_prefix + '/management/purge/update', headers={'x-access-token': token})
        assert resp.status_code == 405

    def test_get_purge_duration_update_with_data(self, client, url_prefix, token, settings):
        """
        Test-Case with existing Settings Data,
        expected output is: status is success, and
        Purge Data Duration i.e., 9 in this case
        """
        settings = SettingsFactory(setting=9, name='purge_data_duration')
        resp = client.get(url_prefix + '/management/purge/update', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == 9


class TestUpdatePurgeDuration:
    """
    Test-case inside this block where this payload is used,
    payload value should be any integer and it's compulsory,
    so if value is not given or value is other than integer in that case,
    it will return 400 error code i.e., bad request
    """
    payload = {'days': None}

    def test_update_purge_duration_without_payload(self, client, url_prefix, token):
        """
        Test-case without payload and existing settings data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/management/purge/update', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_update_purge_duration_with_payload_val_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload value empty dictionary and without existing settings data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/management/purge/update', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_update_purge_duration_with_payload_val_None(self, client, url_prefix, token):
        """
        Test-case with payload value None and without existing settings data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/management/purge/update', headers={'x-access-token': token},
                          json=self.payload)
        assert resp.status_code == 400

    def test_update_purge_duration_with_payload_value(self, client, url_prefix, token):
        """
        Test-case with payload value of days is zero(0) and without existing settings data,
        expected output:- status is failure
        """
        self.payload['days'] = 0
        resp = client.post(url_prefix + '/management/purge/update', headers={'x-access-token': token},
                          json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_update_purge_duration_with_valid_payload_value(self, client, url_prefix, token):
        """
        Test-case with valid payload value and without existing settings data,
        expected output:- status is failure
        """
        self.payload['days'] = 10
        resp = client.post(url_prefix + '/management/purge/update', headers={'x-access-token': token},
                          json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_post_purge_duration_update_with_invalid_method(self, client, url_prefix, token):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.put(url_prefix + '/management/purge/update', headers={'x-access-token': token},
                           data=self.payload)
        assert resp.status_code == 405

    def test_post_purge_duration_update_with_payload_value_zero(self, client, url_prefix, token, settings):
        """
        Test-case with payload value of days is zero(0) and existing settings data,
        expected output:- status is failure
        """
        self.payload['days'] = 0
        settings = SettingsFactory(name='purge_data_duration', setting=7)
        resp = client.post(url_prefix + '/management/purge/update', headers={'x-access-token': token},
                           data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_post_purge_duration_update_with_valid_payload_value(self, client, url_prefix, token, settings):
        """
        Test-case with payload value of days is greater than zero(0) and existing settings data,
        expected output:- status is success
        """
        self.payload['days'] = 5
        s = settings_dao.create_settings('purge_data_duration', 7)
        assert s.setting == '7'
        resp = client.post(url_prefix + '/management/purge/update', headers={'x-access-token': token},
                           data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        sett = settings_dao.get_settings_by_name('purge_data_duration')
        assert sett.setting == '5'


class TestUpdateApiKeys:
    """
    Test-cases inside this block where these payloads used,
    these all payloads value are optionals and of str type, if payload values will not pass,
    then it will update none values,
    Note:-  all test-case inside this block require proper internet connection,
    if internet-conection is not available then most of the test-case will get failed
    """
    payload = {'vt_key': None, 'IBMxForceKey': None, 'IBMxForcePass': None, 'otx_key': None}

    def test_update_api_keys_without_payload(self, client, url_prefix, token):
        """
        Test-case without payloads and without existing ThreatIntelCredentials,
        expected output:- status is failure
        """
        resp = client.post(url_prefix + '/management/apikeys', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_update_api_keys_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload empty dictionary and without existing ThreatIntelCredentials,
        expected output:- status is failure
        """
        resp = client.post(url_prefix + '/management/apikeys', headers={'x-access-token': token},
                          json={})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_update_api_keys_with_payload_values_None(self, client, url_prefix, token):
        """
        Test-case with payload values None and without existing ThreatIntelCredentials,
        expected output:- status is failure
        """
        resp = client.post(url_prefix + '/management/apikeys', headers={'x-access-token': token},
                          json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_update_api_keys_with_payload_values_empty_str(self, client, url_prefix, token):
        """
        Test-case with payload values are empty string and without existing ThreatIntelCredentials,
        expected output:- status is failure
        """
        self.payload['vt_key'] = ''
        self.payload['IBMxForceKey'] = ''
        self.payload['IBMxForcePass'] = ''
        self.payload['otx_key'] = ''
        resp = client.post(url_prefix + '/management/apikeys', headers={'x-access-token': token},
                          json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_update_api_keys_with_payload_values(self, client, url_prefix, token):
        """
        Test-case with payload values and without existing ThreatIntelCredentials,
        expected output:- status is failure
        """
        self.payload['vt_key'] = 'vt_key'
        self.payload['IBMxForceKey'] = 'IBMxForceKey'
        self.payload['IBMxForcePass'] = 'IBMxForcePass'
        self.payload['otx_key'] = 'otx_key'
        resp = client.post(url_prefix + '/management/apikeys', headers={'x-access-token': token},
                          json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_update_api_keys_with_only_payload_value_vt_key(self, client, url_prefix, token):
        """
        Test-case with only payload value vt_key and without existing ThreatIntelCredentials,
        expected output:- status is failure
        """
        payload = {'vt_key': 'vt_key'}
        resp = client.post(url_prefix + '/management/apikeys', headers={'x-access-token': token},
                          json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_update_api_keys_with_only_payload_value_otx_key(self, client, url_prefix, token):
        """
        Test-case with only payload value vt_key and without existing ThreatIntelCredentials,
        expected output:- status is failure
        """
        payload = {'otx_key': 'otx_key'}
        resp = client.post(url_prefix + '/management/apikeys', headers={'x-access-token': token},
                          json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_update_api_keys_with_only_payload_value_ibmx_key(self, client, url_prefix, token):
        """
        Test-case with only payload value vt_key and without existing ThreatIntelCredentials,
        expected output:- status is failure
        """
        payload = {'IBMxForceKey': 'IBMxForceKey'}
        resp = client.post(url_prefix + '/management/apikeys', headers={'x-access-token': token},
                          json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_update_api_keys_with_only_payload_value_ibmx_pass(self, client, url_prefix, token):
        """
        Test-case with only payload value vt_key and without existing ThreatIntelCredentials,
        expected output:- status is failure
        """
        payload = {'IBMxForcePass': 'IBMxForcePass'}
        resp = client.post(url_prefix + '/management/apikeys', headers={'x-access-token': token},
                          json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_update_api_keys_with_only_payload_value_ibmx_key_and_pass(self, client, url_prefix, token):
        """
        Test-case with only payload value vt_key and without existing ThreatIntelCredentials,
        expected output:- status is failure
        """
        payload = {'IBMxForceKey': 'IBMxForceKey','IBMxForcePass': 'IBMxForcePass'}
        resp = client.post(url_prefix + '/management/apikeys', headers={'x-access-token': token},
                          json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_update_api_keys_with_invalid_method(self, client, url_prefix, token):
        """
      Test-case with invalid request method,
      expected output:- status code is 405
      """
        resp = client.put(url_prefix + '/management/apikeys', headers={'x-access-token': token},
                           data=self.payload)
        assert resp.status_code == 405

    def test_update_api_key_without_payload(self, client, url_prefix, token, threat_intel_credentials):
        """
        Test-case without payloads and with existing ThreatIntelCredentials,
        expected output:- status is failure, and
        value of ibmxforce_key, ibmxforce_pass, virustotal_key, and alienvault_key
        """
        resp = client.post(url_prefix + '/management/apikeys', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'
        assert response_dict['data']['ibmxforce']['key'] == 'ibm_x_key'
        assert response_dict['data']['ibmxforce']['pass'] == 'ibm_x_pass'
        assert response_dict['data']['virustotal']['key'] == 'virustotal'
        assert response_dict['data']['alienvault']['key'] == 'alienvault'

    def test_update_api_key_with_payload_empty_dict(self, client, url_prefix, token, threat_intel_credentials):
        """
        Test-case with payload empty dictionary and with existing ThreatIntelCredentials,
        expected output:- status is success, and
        value of ibmxforce_key, ibmxforce_pass, virustotal_key, and alienvault_key
        """
        resp = client.post(url_prefix + '/management/apikeys', headers={'x-access-token': token},
                          json={})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'
        assert response_dict['data']['ibmxforce']['key'] == 'ibm_x_key'
        assert response_dict['data']['ibmxforce']['pass'] == 'ibm_x_pass'
        assert response_dict['data']['virustotal']['key'] == 'virustotal'
        assert response_dict['data']['alienvault']['key'] == 'alienvault'

    def test_update_api_key_with_payload_values_None(self, client, url_prefix, token, threat_intel_credentials):
        """
        Test-case with payload values None and with existing ThreatIntelCredentials,
        expected output:- status is success, and
        value of ibmxforce_key, ibmxforce_pass, virustotal_key, and alienvault_key
        """
        self.payload['vt_key'] = None
        self.payload['IBMxForceKey'] = None
        self.payload['IBMxForcePass'] = None
        self.payload['otx_key'] = None
        resp = client.post(url_prefix + '/management/apikeys', headers={'x-access-token': token},
                          json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'
        assert response_dict['data']['ibmxforce']['key'] == 'ibm_x_key'
        assert response_dict['data']['ibmxforce']['pass'] == 'ibm_x_pass'
        assert response_dict['data']['virustotal']['key'] == 'virustotal'
        assert response_dict['data']['alienvault']['key'] == 'alienvault'

    def test_update_api_key_with_payload_values_empty_str(self, client, url_prefix, token, threat_intel_credentials):
        """
        Test-case with payload values are empty string and with existing ThreatIntelCredentials,
        expected output:- status is failure, and
        value of ibmxforce_key, ibmxforce_pass, virustotal_key, and alienvault_key
        """
        self.payload['vt_key'] = ''
        self.payload['IBMxForceKey'] = ''
        self.payload['IBMxForcePass'] = ''
        self.payload['otx_key'] = ''
        resp = client.post(url_prefix + '/management/apikeys', headers={'x-access-token': token},
                          json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'
        assert response_dict['data']['ibmxforce']['key'] == 'ibm_x_key'
        assert response_dict['data']['ibmxforce']['pass'] == 'ibm_x_pass'
        assert response_dict['data']['virustotal']['key'] == 'virustotal'
        assert response_dict['data']['alienvault']['key'] == 'alienvault'

    def test_update_api_key_with_payload_values(self, client, url_prefix, token, threat_intel_credentials):
        """
        Test-case with payload values and with existing ThreatIntelCredentials,
        expected output:- status is success but if anyone keys are invalid then status is failure, and
        value of ibmxforce_key, ibmxforce_pass, virustotal_key, and alienvault_key
        """
        self.payload['vt_key'] = '69f922502ee0ea958fa0ead2979257bd084fa012c283ef9540176ce857ac6f2c'
        self.payload['IBMxForceKey'] = '304020f8-99fd-4a17-9e72-80033278810a'
        self.payload['IBMxForcePass'] = '6710f119-9966-4d94-a7ad-9f98e62373c8'
        self.payload['otx_key'] = 'e877f32db65c756bd40a9aa1489699831be49f638dfd6da2d82ff5c20f3e4358'
        resp = client.post(url_prefix + '/management/apikeys', headers={'x-access-token': token},
                          json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        # assert response_dict['status'] == 'success'
        assert response_dict['status'] == 'failure'
        assert response_dict['data']['ibmxforce']['key'] == '304020f8-99fd-4a17-9e72-80033278810a'
        assert response_dict['data']['ibmxforce']['pass'] == '6710f119-9966-4d94-a7ad-9f98e62373c8'
        assert response_dict['data']['virustotal']['key'] == 'virustotal'
        assert response_dict['data']['alienvault']['key'] == 'e877f32db65c756bd40a9aa1489699831be49f638dfd6da2d82ff5c20f3e4358'

    def test_update_api_key_with_only_payload_value_vt_key(self, client, url_prefix, token, threat_intel_credentials):
        """
        Test-case with only payload value vt_key and with existing ThreatIntelCredentials,
        expected output:- status is failure, due to other two keys not sending from here, and
        value of ibmxforce_key, ibmxforce_pass, virustotal_key, and alienvault_key
        """
        payload = {'vt_key': '69f922502ee0ea958fa0ead2979257bd084fa012c283ef9540176ce857ac6f2c'}
        resp = client.post(url_prefix + '/management/apikeys', headers={'x-access-token': token},
                          json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'
        assert response_dict['data']['ibmxforce']['key'] == 'ibm_x_key'
        assert response_dict['data']['ibmxforce']['pass'] == 'ibm_x_pass'
        assert response_dict['data']['virustotal']['key'] == 'virustotal'
        assert response_dict['data']['alienvault']['key'] == 'alienvault'

    def test_update_api_key_with_only_payload_value_otx_key(self, client, url_prefix, token, threat_intel_credentials):
        """
        Test-case with only payload value vt_key and with existing ThreatIntelCredentials,
        expected output:- status is failure, due to other two keys not sending from here, and
        value of ibmxforce_key, ibmxforce_pass, virustotal_key, and alienvault_key
        """
        payload = {'otx_key': 'e877f32db65c756bd40a9aa1489699831be49f638dfd6da2d82ff5c20f3e4358'}
        resp = client.post(url_prefix + '/management/apikeys', headers={'x-access-token': token},
                          json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'
        assert response_dict['data']['ibmxforce']['key'] == 'ibm_x_key'
        assert response_dict['data']['ibmxforce']['pass'] == 'ibm_x_pass'
        assert response_dict['data']['virustotal']['key'] == 'virustotal'
        assert response_dict['data']['alienvault']['key'] == 'e877f32db65c756bd40a9aa1489699831be49f638dfd6da2d82ff5c20f3e4358'

    def test_update_api_key_with_only_payload_value_ibmx_key(self, client, url_prefix, token, threat_intel_credentials):
        """
        Test-case with only payload value vt_key and with existing ThreatIntelCredentials,
        expected output:- status is failure, due to other two keys not sending from here, and
        value of ibmxforce_key, ibmxforce_pass, virustotal_key, and alienvault_key,
        """
        payload = {'IBMxForceKey': '304020f8-99fd-4a17-9e72-80033278810a'}
        resp = client.post(url_prefix + '/management/apikeys', headers={'x-access-token': token},
                          json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'
        assert response_dict['data']['ibmxforce']['key'] == 'ibm_x_key'
        assert response_dict['data']['ibmxforce']['pass'] == 'ibm_x_pass'
        assert response_dict['data']['virustotal']['key'] == 'virustotal'
        assert response_dict['data']['alienvault']['key'] == 'alienvault'

    def test_update_api_key_with_only_payload_value_ibmx_pass(self, client, url_prefix, token, threat_intel_credentials):
        """
        Test-case with only payload value vt_key and with existing ThreatIntelCredentials,
        expected output:- status is failure, due to other two keys not sending from here, and
        value of ibmxforce_key, ibmxforce_pass, virustotal_key, and alienvault_key
        """
        payload = {'IBMxForcePass': '6710f119-9966-4d94-a7ad-9f98e62373c8'}
        resp = client.post(url_prefix + '/management/apikeys', headers={'x-access-token': token},
                          json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'
        assert response_dict['data']['ibmxforce']['key'] == 'ibm_x_key'
        assert response_dict['data']['ibmxforce']['pass'] == 'ibm_x_pass'
        assert response_dict['data']['virustotal']['key'] == 'virustotal'
        assert response_dict['data']['alienvault']['key'] == 'alienvault'

    def test_update_api_key_with_only_payload_value_ibmx_key_and_pass(self, client, url_prefix, token, threat_intel_credentials):
        """
        Test-case with only payload value vt_key and with existing ThreatIntelCredentials,
        expected output:- status is failure, due to other two keys not sending from here, and
        value of ibmxforce_key, ibmxforce_pass, virustotal_key, and alienvault_key
        """
        payload = {'IBMxForceKey': '304020f8-99fd-4a17-9e72-80033278810a','IBMxForcePass': '6710f119-9966-4d94-a7ad-9f98e62373c8'}
        resp = client.post(url_prefix + '/management/apikeys', headers={'x-access-token': token},
                          json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'
        assert response_dict['data']['ibmxforce']['key'] == '304020f8-99fd-4a17-9e72-80033278810a'
        assert response_dict['data']['ibmxforce']['pass'] == '6710f119-9966-4d94-a7ad-9f98e62373c8'
        assert response_dict['data']['virustotal']['key'] == 'virustotal'
        assert response_dict['data']['alienvault']['key'] == 'alienvault'


class TestGetApiKeys:

    def test_get_api_keys_without_existing_api_keys(self, client, url_prefix, token):
        """
        Test-case without existing ThreatIntelCredentials,
        expected output:- status is success
        """
        resp = client.get(url_prefix + '/management/apikeys', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'

    def test_get_api_keys_with_invalid_method(self, client, url_prefix, token):
        """
      Test-case with invalid request method,
      expected output:- status code is 405
      """
        resp = client.put(url_prefix + '/management/apikeys', headers={'x-access-token': token})
        assert resp.status_code == 405

    def test_get_api_keys_with_existing_api_keys(self, client, url_prefix, token, threat_intel_credentials):
        """
        Test-case without existing ThreatIntelCredentials,
        expected output:- status is success, and
        and value of ibmxforce's key and pass, virustotal's key and alienvault's key
        """
        resp = client.get(url_prefix + '/management/apikeys', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['ibmxforce']['key'] == 'ibm_x_key'
        assert response_dict['data']['ibmxforce']['pass'] == 'ibm_x_pass'
        assert response_dict['data']['virustotal']['key'] == 'virustotal'
        assert response_dict['data']['alienvault']['key'] == 'alienvault'