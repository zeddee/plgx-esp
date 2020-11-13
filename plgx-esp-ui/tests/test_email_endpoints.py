"""
All Test-Case required client, url_prefix and token,
and these all we need to just pass as parameters in the function,

Note:- make sure about email and password is correct.
"""

import json, base64

from polylogyx.constants import PolyLogyxServerDefaults
from polylogyx.dao import settings_dao
from polylogyx.models import Settings
from .base import TestUtils
from .factories import SettingsFactory

test_utils_obj = TestUtils()

settings_data = {
        'email': 'abcd@gmail.com', 'smtpPort': '12', 'smtpAddress': 'smtp.gmail.com',
        'password': 'abcd', 'emailRecipients': 'foobar@gmail.com,test2@gmail.com'
    }


class TestGetConfigureEmailRecipientAndSender:

    def test_get_configure_email_without_existing_settings_data(self, client, url_prefix, token):
        """
        Test-case without payloads and without existing settings data,
        expected output:- status is success
        """
        resp = client.get(url_prefix + '/email/configure', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'

    def test_get_configure_email_with_invalid_method(self, client, url_prefix, token, settings):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.put(url_prefix + '/email/configure', headers={'x-access-token': token})
        assert resp.status_code == 405

    def test_get_configure_email_without_default_settings_data(self, client, url_prefix, token, settings):
        """
        Test-case without payloads and without existing settings data of plgx_config_all_settings,
        expected output:- status is success
        """
        resp = client.get(url_prefix + '/email/configure', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'

    def test_get_configure_email_with_default_settings_data(self, client, url_prefix, token, settings):
        """
        Test-case with all payloads value and settings data of plgx_config_all_settings,
        expected output:- status is success, and
        resultant data of settings
        """
        SettingsFactory(name=PolyLogyxServerDefaults.plgx_config_all_settings, setting=json.dumps(settings_data))
        resp = client.get(url_prefix + '/email/configure', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        data = get_settings_by_name()
        assert response_dict['data'] == data


class TestUpdateConfigureEmailRecipientAndSender:
    """
        to check Valid/invalid of test-case must be gmail login with
        less_Secure_app is turned on gmail account which used in this, and

        Test-case inside these blocks where these payloads are used,
        all values are compulsory values all are string type,
        so if we pass any none value or value type which
        is not matching with specified type it will return 400 i.e., bad request
    """
    payload = {
        'email': 'abcd@gmail.com', 'smtpPort': '12', 'smtpAddress': 'smtp.gmail.com',
        'password': 'abcd', 'emailRecipients': 'foo@gmail.com,test2@gmail.com'
    }

    def test_get_configure_email_without_payload(self, client, url_prefix, token):
        """
        Test-case without payloads but without existing settings data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/email/configure', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_get_configure_email_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload is empty dictionary but without existing settings data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/email/configure', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_get_configure_email_with_none_value_email(self, client, url_prefix, token):
        """
        Test-case with invalid payloads but without existing settings data,
        expected output:- status_code is 400
        """
        self.payload['email'] = None
        self.payload['smtpPort'] = None
        self.payload['smtpAddress'] = None
        self.payload['password'] = None
        self.payload['emailRecipients'] = None
        resp = client.post(url_prefix + '/email/configure', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_get_configure_email_with_all_valid_credentials(self, client, url_prefix, token):
        """
        Test-case with valid payloads and valid credentials
        as well as existing data to update with payload,
        expected output:- status is success, and
        resultant data is same as payload value
        """
        payload = {
            'email': 'abcd@gmail.com', 'smtpPort': '12', 'smtpAddress': 'smtp.gmail.com',
            'password': 'abcd', 'emailRecipients': 'foo@gmail.com,test2@gmail.com'
        }
        resp = client.post(url_prefix + '/email/configure', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['email'] == payload['email']
        assert response_dict['data']['smtpPort'] == int(payload['smtpPort'])
        assert response_dict['data']['smtpAddress'] == payload['smtpAddress']
        assert response_dict['data']['password'] == base64.b64encode(
            payload['password'].encode('ascii')).decode('ascii') + '\n'
        assert response_dict['data']['emailRecipients'] == payload['emailRecipients'].split(',')

    def test_get_configure_email_with_invalid_method(self, client, url_prefix, token, settings):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.put(url_prefix + '/email/configure', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_get_configure_emails_with_all_valid_credentials(self, client, url_prefix, token, settings):
        """
        Test-case with valid payloads and valid credentials
        as well as existing data to update with payload,
        expected output:- status is success, and
        resultant data is same as payload value
        """
        payload = {
            'email': 'abcd@gmail.com', 'smtpPort': '12', 'smtpAddress': 'smtp.gmail.com',
            'password': 'abcd', 'emailRecipients': 'foobar@gmail.com,test2@gmail.com'
        }
        resp = client.post(url_prefix + '/email/configure', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['email'] == payload['email']
        assert response_dict['data']['smtpPort'] == int(payload['smtpPort'])
        assert response_dict['data']['smtpAddress'] == payload['smtpAddress']
        assert response_dict['data']['password'] == base64.b64encode(
            payload['password'].encode('ascii')).decode('ascii') + '\n'
        assert response_dict['data']['emailRecipients'] == payload['emailRecipients'].split(',')


class TestEmailRecipientAndSender:
    """
    Test-case inside these blocks where these payloads are used,
    all values are compulsory values except smtpPort and only type of smtpPort is positive integer,
    remainings all are string type, so if we pass any none value or value type which
    is not matching with specified type it will return 400 i.e., bad request
    """
    payload = {
        'email': 'abcd@gmail.com', 'smtpPort': '12', 'smtpAddress': 'smtp.gmail.com',
        'password': 'abcd', 'emailRecipients': 'foo@gmail.com,test2@gmail.com'
    }

    def test_email_receipient_and_sender_without_payload(self, client, url_prefix, token):
        """
        Test-case without payloads but without existing settings data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/email/test', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_email_receipient_and_sender_with_empty_payload(self, client, url_prefix, token):
        """
        Test-Case with empty dictionary payload and with existing Settings Data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/email/test', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_email_receipient_and_sender_with_all_payload(self, client, url_prefix, token):
        """
        Test-Case with all payload value and with existing Settings Data,
        expected output:- status is success
        """
        resp = client.post(url_prefix + '/email/test', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'

    def test_email_receipient_and_sender_with_all_payload_except_smtp_port(self, client, url_prefix, token):
        """
        Test-Case with all payload value except smtp port and with existing Settings Data,
        expected output:- status is failure
        """
        payload = {
            'email': 'abcd@gmail.com', 'smtpPort': '12', 'smtpAddress': 'smtp.gmail.com',
            'password': 'abcd', 'emailRecipients': 'foo@gmail.com,test2@gmail.com'
        }
        resp = client.post(url_prefix + '/email/test', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'

    def test_email_receipient_and_sender_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-Case with all payloads values are none and with existing Settings Data,
        expected output:- status_code is 400
        """
        self.payload['email'] = None
        self.payload['smtpPort'] = None
        self.payload['smtpAddress'] = None
        self.payload['password'] = None
        self.payload['emailRecipients'] = None
        resp = client.post(url_prefix + '/email/test', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_email_receipient_and_sender_with_invalid_method(self, client, url_prefix, token, settings):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.get(url_prefix + '/email/test', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_email_receipient_and_sender_with_invalid_credentials(self, client, url_prefix, token, settings):
        """
        Test-Case with invalid data but with existing settings data,
        expected output:- status is failure
        """
        self.payload['email'] = 'abcd@gmail.com'
        self.payload['smtpPort'] = '12'
        self.payload['smtpAddress'] = 'smtp.gmail.com'
        self.payload['password'] = 'abcd'
        self.payload['emailRecipients'] = 'foo@gmail.com,test2@gmail.com'
        resp = client.post(url_prefix + '/email/test', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_email_receipient_and_sender_with_data(self, client, url_prefix, token, settings):
        """
        Test-Case with valid credentials along with existing settings data,
        expected output:- status is success
        """
        self.payload['email'] = 'abcd@gmail.com'
        self.payload['smtpPort'] = None
        self.payload['smtpAddress'] = 'smtp.gmail.com'
        self.payload['password'] = 'abcd'
        self.payload['emailRecipients'] = 'polylogyx@gmail.com,test2@gmail.com'
        settings = Settings.create(
            setting=json.dumps(
                {
                    "email": "test@gmail.com",
                    "emailRecipients": ["foo@gmail.com", "test2@gmail.com"], "password": "VGVzdEAxMjM0",
                    "smtpAddress": "smtp.googlemail.com", "smtpPort": 465
                }
            ),
            name='plgx_config_all_settings'
        )
        resp = client.post(url_prefix + '/email/test', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'

    def test_email_receipient_and_sender_with_existing_data(self, client, url_prefix, token, settings):
        """
        Test-Case with valid credentials and with existing settings data,
        expected output:- status is success
        """
        settings.update(
            setting=json.dumps(
                {
                    "email": "abc@gmail.com",
                    "emailRecipients": ["foo@gmail.com", "test2@gmail.com"], "password": "VGVzdEAxMjM0",
                    "smtpAddress": "smtp.googlemail.com", "smtpPort": 465
                }
            )
        )
        resp = client.post(url_prefix + '/email/test', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'


def get_settings_by_name():
    existing_setting = settings_dao.get_settings_by_name(PolyLogyxServerDefaults.plgx_config_all_settings)
    setting = ''
    if existing_setting:
        setting = json.loads(existing_setting.setting)
        setting['password'] = base64.b64encode(setting['password'].encode('ascii')).decode('ascii')

    return setting

