from flask_restplus import Namespace, Resource, inputs
from polylogyx.utils import require_api_key
from polylogyx.blueprints.v1.utils import *
from polylogyx.models import User, Settings, ThreatIntelCredentials
from polylogyx.dao.v1 import common_dao
from polylogyx.wrappers.v1 import parent_wrappers as parentwrapper
from polylogyx.extensions import bcrypt
from polylogyx.util.api_validator import ApiValidator
from polylogyx.dao.v1 import settings_dao

import jwt

ns = Namespace('management', description='Management operations')
api_validator_obj = ApiValidator()


@require_api_key
@ns.route('/changepw', endpoint='change_password')
@ns.doc(params = {'old_password':"old password", 'new_password':"new password", 'confirm_new_password':"confirm new password"})
class ChangePassword(Resource):
    '''Changes user password'''
    parser = requestparse(['old_password', 'new_password', 'confirm_new_password'], [str, str, str], ["old password", "new password", "confirm new password"], [True, True, True])

    @ns.expect(parser)
    def post(self):
        args = self.parser.parse_args()
        status = "failure"
        payload = jwt.decode(request.headers.environ.get('HTTP_X_ACCESS_TOKEN'), current_app.config['SECRET_KEY'])
        user = User.query.filter_by(id=payload['id']).first()
        if bcrypt.check_password_hash(user.password, args['old_password']):
            if not bcrypt.check_password_hash(user.password, args['new_password']):
                if args['new_password']==args['confirm_new_password']:
                    current_app.logger.info("%s has changed the password", user.username)
                    user.update(password=bcrypt.generate_password_hash(args['new_password'].encode("utf-8")).decode("utf-8"))
                    message = "Password is updated successfully"
                    status = "success"
                else:
                    message = "New password and confirm new password are not matching for the user"
            else:
                message = "New password and old password should not be same"
        else:
            message = "Old password is not matching"
        return marshal(respcls(message,status), parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/settings', endpoint = "settings_update")
class SettingsUpdate(Resource):
    '''to change purge data duration and alert aggregation settings'''
    parser = requestparse(['purge_data_duration', 'alert_aggregation_duration'], [inputs.positive, inputs.positive], ["purge duration", "alert aggregation duration"], [False, False])

    def get(self):
        query_set = Settings.query.filter(Settings.name.in_(['purge_data_duration', 'alert_aggregation_duration'])).all()
        settings = {setting.name : int(setting.setting) for setting in query_set}
        return marshal(respcls("Platform settings are fetched successfully", "success", settings),
                       parentwrapper.common_response_wrapper, skip_none=True)

    @ns.expect(parser)
    def put(self):
        args = self.parser.parse_args()
        if args['purge_data_duration']:
            settings_dao.update_or_create_setting('purge_data_duration', args['purge_data_duration'])
        if args['alert_aggregation_duration']:
            settings_dao.update_or_create_setting('alert_aggregation_duration', args['alert_aggregation_duration'])
        db.session.commit()
        current_app.logger.info("Purge data duration and/or Alert aggregation duration is/are changed")
        message = "Platform settings are updated successfully"
        status = "success"
        return marshal(respcls(message,status), parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/apikeys', endpoint='add_apikey')
@ns.doc(params = {'vt_key':"vt key",'IBMxForceKey':"IBMxForceKey",'IBMxForcePass':"IBMxForcePass",'otx_key':"otx_key"})
class UpdateApiKeys(Resource):
    """Resource for Threat Intel API keys management"""
    parser = requestparse(['vt_key', 'IBMxForceKey', 'IBMxForcePass', 'otx_key'], [str, str, str, str],
                          ['vt key', 'IBMxForceKey', 'IBMxForcePass', 'otx key'], [False, False, False, False])
    parser_get = requestparse([], [], [], [])

    @ns.doc(body=parser)
    @ns.expect(parser)
    def post(self):
        """
        Updates Threat Intel API keys
        """
        args = self.parser.parse_args()
        status = "success"
        passed_keys_count = 0
        for arg in args:
            if args[arg]:
                passed_keys_count += 1

        if not args['IBMxForcePass'] and args['IBMxForceKey'] or args['IBMxForcePass'] and not args['IBMxForceKey']:
            return marshal({'status': "failure", 'message': "Both IBMxForceKey and IBMxForcePass are required!",
                        'data': None, 'errors': {'ibmxforce': "Both IBMxForceKey and IBMxForcePass are required!"}},
                       parentwrapper.common_response_with_errors_wrapper, skip_none=True)

        threat_intel_creds = {'ibmxforce': {}, 'virustotal': {}, 'alienvault': {}}
        if args['IBMxForceKey'] and args['IBMxForcePass']:
            threat_intel_creds['ibmxforce'] = {'key': args['IBMxForceKey'], 'pass': args['IBMxForcePass']}
        if args['vt_key']:
            threat_intel_creds['virustotal'] = {'key': args['vt_key']}
        if args['otx_key']:
            threat_intel_creds['alienvault'] = {'key': args['otx_key']}

        errors = {}
        invalid = []
        for intel in threat_intel_creds.keys():
            is_key_valid = True
            existing_creds = None
            if threat_intel_creds[intel]:
                response = api_validator_obj.validate_threat_intel_key(intel, threat_intel_creds[intel])
                if not response[0]:
                    is_key_valid = False
                    invalid.append(intel)
                    errors[intel] = "This threat intel api key is invalid!"
                else:
                    existing_creds = db.session.query(ThreatIntelCredentials).filter(
                        ThreatIntelCredentials.intel_name == intel).first()
                if not response[1] is None:
                    try:
                        body = response[1].json()
                        if 'message' in body:
                            errors[intel] = body['message']
                        elif 'error' in body:
                            errors[intel] = body['error']
                    except:
                        errors[intel] = response[1].text
                if is_key_valid:
                    if existing_creds:
                        existing_creds.credentials = threat_intel_creds[intel]
                        db.session.add(existing_creds)
                    else:
                        ThreatIntelCredentials.create(intel_name=intel, credentials=threat_intel_creds[intel])
        db.session.commit()
        API_KEYS = {}
        threat_intel_credentials = ThreatIntelCredentials.query.all()
        for threat_intel_credential in threat_intel_credentials:
            API_KEYS[threat_intel_credential.intel_name] = threat_intel_credential.credentials
        if not invalid:
            message = "Threat Intel keys are updated successfully"
        else:
            if (passed_keys_count == len(invalid)+1 and 'ibmxforce' not in invalid) or (passed_keys_count == len(invalid)+2 and 'ibmxforce' in invalid):
                status = 'failure'
            message = "{} api key(s) provided is/are invalid!".format(','.join(invalid))
        current_app.logger.info("Threat Intel keys are updated")
        return marshal({'status': status, 'message': message, 'data': API_KEYS, 'errors': errors}, parentwrapper.common_response_with_errors_wrapper, skip_none=True)

    @ns.doc(body=parser_get)
    @ns.expect(parser_get)
    def get(self):
        """
        Returns Threat Intel API keys
        """
        API_KEYS = {}
        threat_intel_credentials = ThreatIntelCredentials.query.all()
        for threat_intel_credential in threat_intel_credentials:
            API_KEYS[threat_intel_credential.intel_name] = threat_intel_credential.credentials
        message = "Threat Intel Keys are fetched successfully"
        status = "success"
        return marshal(respcls(message, status, API_KEYS), parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/virustotal/av_engine', endpoint = "Virustotal_av_engine_update")
@ns.doc(params = {'min_match_count':"minimum count for unselected engine match","av_engines":"selected av engines"})
class VirusTotalAvEngineUpdate(Resource):
    '''to update av engine status'''
    parser = requestparse(['min_match_count', 'av_engines'], [int, dict],
                          ["minimum count for unselected engine match", "selected av engines"], [False,False],
                          [None, None])

    def get(self):
        status="failure"
        data=[]
        message = "virustotal_min_match_count or av engines are not set"
        virustotal_match_count_obj = Settings.query.filter(Settings.name == 'virustotal_min_match_count').first()
        if virustotal_match_count_obj:
            minimum_count = int(virustotal_match_count_obj.setting)
            data=common_dao.fetch_virus_total_av_engines()
            if data :
                data = {'min_match_count': minimum_count, 'av_engines':data}
                status = "success"
                message = "virus total av engines are fetched successfully"
        return respcls(message, status, data)

    @ns.expect(parser)
    def post(self):
        args = self.parser.parse_args()
        av_engines=args['av_engines']
        minimum_count=args['min_match_count']
        if not minimum_count and not av_engines:
            abort(400, "Please provide valid payload")

        if minimum_count:
                if minimum_count > 0:
                    minimum_count_obj = Settings.query.filter(Settings.name == 'virustotal_min_match_count').first()
                    minimum_count_obj.setting = minimum_count
                    minimum_count_obj.update(minimum_count_obj)
                else:
                    abort(400, "Please provide  minimum_count greater than 0")
        if av_engines:
            for av_engine in av_engines:
                if "status" not in av_engines[av_engine]:
                    abort(400, "Please provide status OR please provide valid payload")

        common_dao.update_av_engine_status(av_engines)
        current_app.logger.info("Virus Total AV engines configuration is changed")
        status = "success"
        message = "successfully updated av engines"
        return respcls(message, status)
