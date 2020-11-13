from flask_restplus import Namespace, Resource

from polylogyx.blueprints.v1.utils import *
from polylogyx.utils import require_api_key
from polylogyx.dao.v1 import iocs_dao as dao
from polylogyx.wrappers.v1 import parent_wrappers as parentwrapper

ns = Namespace('iocs', description='iocs related operations')


@require_api_key
@ns.route('', endpoint='get_ioc_data')
@ns.doc(params={})
class ListIocs(Resource):
    '''lists ioc json data'''
    def get(self):
        ioc_full_data = {}
        for ioc in dao.get_intel_data('self'):
            if not ioc.threat_name in ioc_full_data:
                ioc_full_data[ioc.threat_name] = {'type':ioc.type, 'severity':ioc.severity, 'intel_type':ioc.intel_type, 'values':ioc.value}
            else:
                ioc_full_data[ioc.threat_name]['values'] = ioc_full_data[ioc.threat_name]['values'] + ',' + str(ioc.value)
        if not ioc_full_data:
            ioc_full_data = {
                "test-intel_ipv4": {
                    "type": "remote_address",
                    "values": "3.30.1.15,3.30.1.16",
                    "severity": "WARNING"
                },
                "test-intel_domain_name": {
                    "type": "domain_name",
                    "values":"unknown.com,slackabc.com",
                    "severity": "WARNING"
                },
                "test-intel_md5": {
                    "type": "md5",
                    "values": "3h8dk0sksm0,9sd772ndd80",
                    "severity": "INFO"
                }
            }
        status="success"
        message="Successfully fetched the iocs"

        return marshal(respcls(message,status,ioc_full_data),parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/add', endpoint='add_ioc')
@ns.doc(params={'file': 'ioc json file to upload'})
class AddIocs(Resource):
    '''Uploads and adds an ioc file to the iocs folder'''
    parser = requestparse(['data'], [dict], ['Threat Intel Data Json'], [True])

    @ns.expect(parser)
    def post(self):
        args = self.parser.parse_args()
        data = args['data']
        dao.del_manual_threat_intel('self')
        try:
            for intel_name, values in data.items():
                if ('severity' in values and 'type' in values) and (type(values['values']) == type("")):
                    for value in values['values'].split(','):
                        dao.create_manual_threat_intel(intel_type='self', type=values['type'],value=value,severity=values['severity'], threat_name=intel_name)
            current_app.logger.info("IOCS(Indicators of compromise) are updated")
            message = "Successfully updated the intel data"
            status = "success"
        except Exception as e:
            message = str(e)
            status = "failure"
        return marshal(respcls(message,status),parentwrapper.common_response_wrapper,skip_none=True)