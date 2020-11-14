import base64

from flask_restplus import Namespace, Resource

from polylogyx.blueprints.v1.utils import *
from polylogyx.utils import require_api_key
from polylogyx.dao.v1 import settings_dao as dao
from polylogyx.wrappers.v1 import parent_wrappers as parentwrapper
from polylogyx.constants import PolyLogyxServerDefaults
from polylogyx.util.mitre import TestMail

ns = Namespace('email', description='email related operations')


@require_api_key
@ns.route('/configure', endpoint = 'configure_email')
@ns.doc(params={"email":"from email", "smtpPort":"smtp port", "smtpAddress":"smtp address", "password": "password of the from mail", "emailRecipients":"list of to-email addresses"})
class ConfigureEmailRecipientAndSender(Resource):
    '''Configures the email recipient and the sender based on the details given'''

    parser = requestparse(["email", "smtpPort", "smtpAddress", "password", "emailRecipients"],[str,str,str,str,str],["from email","smtp port","smtp address", "password of the from mail","list of to-email addresses separated by comma"],[True,True,True,True,True])

    def get(self):
        existing_setting = dao.get_settings_by_name(PolyLogyxServerDefaults.plgx_config_all_settings)
        if existing_setting:
            setting = json.loads(existing_setting.setting)
            setting['password'] = base64.decodestring(setting['password'].encode('utf-8')).decode('utf-8')
        else:
            setting = {}
        message = "Successfully fetched the email configuration"
        status = "success"
        return marshal(respcls(message,status,setting), parentwrapper.common_response_wrapper, skip_none=True)

    @ns.expect(parser)
    def post(self):
        args = self.parser.parse_args()  # need to exists for input payload validation
        is_payload_valid = configure_email_recipient_and_sender(args)
        if is_payload_valid[0]:
            message = "Successfully updated the email settings!"
            status = "success"
            data = is_payload_valid[1]
            current_app.logger.info("Email configuration is updated")
        else:
            message = "The requested settings for the details provided are not valid!"
            status = "failure"
            data = None
        return marshal(respcls(message,status,data), parentwrapper.common_response_wrapper)


def configure_email_recipient_and_sender(request_json):
    from flask import current_app
    test_mail = TestMail()

    if request_json['emailRecipients']:
        request_json['emailRecipients']=request_json['emailRecipients'].split(',')
    else:
        request_json['emailRecipients']=[]

    request_data = request_json

    is_credentials_valid = test_mail.test(username=request_json['email'], password=request_json['password'], smtp=request_json['smtpAddress'], recipients=request_json['emailRecipients'])
    request_json = json.dumps({'email':request_json['email'], 'emailRecipients': request_json['emailRecipients'], 'password':base64.encodestring(str.encode(request_json['password'])).decode('utf-8'), 'smtpAddress':request_json['smtpAddress'], 'smtpPort':int(request_json['smtpPort'])})
    if is_credentials_valid:
        existing_setting = dao.get_settings_by_name(PolyLogyxServerDefaults.plgx_config_all_settings)

        if existing_setting:
            settings = existing_setting.update(setting = request_json, synchronize_session=False)
        else:
            settings = dao.create_settings(name=PolyLogyxServerDefaults.plgx_config_all_settings, setting=request_json)

        current_app.config['MAIL_USERNAME'] = request_data['email']
        current_app.config['MAIL_PASSWORD'] = request_data['password']
        current_app.config['MAIL_SERVER'] = request_data['smtpAddress']
        current_app.config['MAIL_PORT'] = int(request_data['smtpPort'])

        settings = json.loads(settings.setting)
        return (True, settings)
    else:
        return (False, None)


@require_api_key
@ns.route('/test', endpoint = 'test_mail_for_existing_settings')
@ns.doc(params={"email":"from email", "smtpPort":"smtp port", "smtpAddress":"smtp address", "password": "password of the from mail", "emailRecipients":"list of to-email addresses"})
class TestEmailRecipientAndSender(Resource):
    '''Tests the email recipient and the sender based on the details given'''

    parser = requestparse(["email", "smtpPort", "smtpAddress", "password", "emailRecipients"],
                          [str, str, str, str, str],
                          ["from email", "smtp port", "smtp address", "password of the from mail",
                           "list of to-email addresses separated by comma"], [True, False, True, True, True])

    @ns.expect(parser)
    def post(self):
        setting = self.parser.parse_args()
        if setting['emailRecipients']:
            setting['emailRecipients'] = setting['emailRecipients'].split(',')
        else:
            setting['emailRecipients'] = []
        test_mail = TestMail()
        is_credntials_valid = test_mail.test(username=setting['email'], password=setting['password'],
                                             smtp=setting['smtpAddress'],
                                             recipients=setting['emailRecipients'])
        if is_credntials_valid:
            message = "Successfully sent the email to recipients for the existing configuration!"
            status = "success"
        else:
            message = "Mail credentials are not valid or SMTP settings might be wrong!"
            status = "failure"

        return marshal(respcls(message, status), parentwrapper.common_response_wrapper, skip_none=True)
