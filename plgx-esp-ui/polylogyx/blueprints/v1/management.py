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
        return marshal(respcls(message,status),parentwrapper.common_response_wrapper,skip_none=True)


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
        return marshal(respcls(message,status),parentwrapper.common_response_wrapper,skip_none=True)


@require_api_key
@ns.route('/apikeys', endpoint='add_apikey')
@ns.doc(params = {'vt_key':"vt key",'IBMxForceKey':"IBMxForceKey",'IBMxForcePass':"IBMxForcePass",'otx_key':"otx_key"})
class UpdateApiKeys(Resource):
    """Resource for Threat Intel API keys management"""
    parser = requestparse(['vt_key', 'IBMxForceKey', 'IBMxForcePass','otx_key'], [str, str, str,str],
                          ['vt key', 'IBMxForceKey', 'IBMxForcePass','otx key'],[False,False,False,False])
    parser_get = requestparse([], [], [], [])

    def func(self):
        args = self.parser.parse_args()
        status = "success"
        vt_key = args['vt_key']
        ibm_key = args['IBMxForceKey']
        ibm_pass = args['IBMxForcePass']
        otx_key = args['otx_key']

        is_ibm_key_valid = True
        is_vt_key_valid = True
        is_otx_key_valid = True

        errors = {}

        if ibm_key and ibm_pass:
            response = api_validator_obj.is_valid_api_ibmxforce(ibm_key, ibm_pass)
            if response[0]:
                ibm_x_force_credentials = db.session.query(ThreatIntelCredentials).filter(
                    ThreatIntelCredentials.intel_name == 'ibmxforce').first()

                if ibm_x_force_credentials:
                    new_credentials = dict(ibm_x_force_credentials.credentials)
                    new_credentials['key'] = ibm_key
                    new_credentials['pass'] = ibm_pass
                    ibm_x_force_credentials.credentials = new_credentials
                    db.session.add(ibm_x_force_credentials)
                    db.session.commit()
                else:
                    credentials = {}
                    credentials['key'] = ibm_key
                    credentials['pass'] = ibm_pass
                    ThreatIntelCredentials.create(intel_name='ibmxforce', credentials=credentials)
                if response[1]:
                    if 'message' in response[1]:
                        errors['ibmxforce'] = response[1]['message']
                    elif 'error' in response[1]:
                        errors['ibmxforce'] = response[1]['error']
            else:
                is_ibm_key_valid = False
        else:
            is_ibm_key_valid=False

        if vt_key:
            response = api_validator_obj.is_valid_api_virustotal(vt_key)
            if response[0]:
                vt_credentials = db.session.query(ThreatIntelCredentials).filter(
                    ThreatIntelCredentials.intel_name == 'virustotal').first()

                if vt_credentials:
                    new_credentials = dict(vt_credentials.credentials)
                    new_credentials['key'] = vt_key
                    vt_credentials.credentials = new_credentials
                    db.session.add(vt_credentials)
                    db.session.commit()
                else:
                    credentials = {}
                    credentials['key'] = vt_key
                    ThreatIntelCredentials.create(intel_name='virustotal', credentials=credentials)
                if response[1]:
                    if 'message' in response[1]:
                        errors['virustotal'] = response[1]['message']
                    elif 'error' in response[1]:
                        errors['virustotal'] = response[1]['error']
            else:
                is_vt_key_valid=False
        else:
            is_vt_key_valid=False

        if otx_key:
            response = api_validator_obj.is_valid_api_otx(otx_key)
            if response[0]:
                alienvault_credentials = db.session.query(ThreatIntelCredentials).filter(
                    ThreatIntelCredentials.intel_name == 'alienvault').first()

                if alienvault_credentials:
                    new_credentials = dict(alienvault_credentials.credentials)
                    new_credentials['key'] = otx_key
                    alienvault_credentials.credentials = new_credentials
                    db.session.add(alienvault_credentials)
                    db.session.commit()
                else:
                    credentials = {}
                    credentials['key'] = otx_key
                    ThreatIntelCredentials.create(intel_name='alienvault', credentials=credentials)
                if response[1]:
                    if 'message' in response[1]:
                        errors['alienvault'] = response[1]['message']
                    elif 'error' in response[1]:
                        errors['alienvault'] = response[1]['error']
            else:
                is_otx_key_valid=False
        else:
            is_otx_key_valid=False

        API_KEYS = {}
        threat_intel_credentials = ThreatIntelCredentials.query.all()
        for threat_intel_credential in threat_intel_credentials:
            API_KEYS[threat_intel_credential.intel_name] = threat_intel_credential.credentials
        if (is_ibm_key_valid and is_otx_key_valid) and is_vt_key_valid:
            message = "Threat Intel keys are updated successfully"
            current_app.logger.info("Threat Intel keys are updated")
        elif (not is_ibm_key_valid and not is_otx_key_valid) and not is_vt_key_valid:
            message = "All Threat Intel keys passed are invalid!"
            status = "failure"
        else:
            status = "failure"
            message = ""
            if not is_vt_key_valid:
                message = message + "VirusTotal"
            if is_otx_key_valid:
                if message != "":
                    message = message + ","
                message = message + "OTX"
            if is_ibm_key_valid:
                if message != "":
                    message = message + ","
                message = message + "IBM"
            message = message + "api keys is/are invalid"
        return marshal({'status':status, 'message':message, 'data':API_KEYS, 'errors':errors}, parentwrapper.common_response_with_errors_wrapper, skip_none=True)

    @ns.doc(body=parser)
    @ns.expect(parser)
    def post(self):
        """Updates Threat Intel API keys"""
        return self.func()

    @ns.doc(body=parser_get)
    @ns.expect(parser_get)
    def get(self):
        """Returns Threat Intel API keys"""
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
        message="virustotal_min_match_count or av engines are not set"
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
                if minimum_count>0:
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
