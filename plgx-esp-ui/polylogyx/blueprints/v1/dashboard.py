from flask_restplus import Namespace, Resource
from polylogyx.wrappers.v1 import parent_wrappers as parentwrapper
from polylogyx.blueprints.v1.utils import *
from polylogyx.utils import require_api_key

ns = Namespace('dashboard', description='dashboard data related operation')


@require_api_key
@ns.route('', endpoint='dashboard_data')
@ns.doc(params={})
class Dashboard(Resource):
    """Getting the Index Data"""

    @ns.marshal_with(parentwrapper.common_response_wrapper)
    def get(self):
        alert_data = fetch_alert_node_query_status()
        distribution_and_status = fetch_dashboard_data()
        delete_setting = db.session.query(Settings).filter(Settings.name == 'purge_data_duration').first()
        purge_duration=None
        if delete_setting:
            purge_duration=delete_setting.setting
        chart_data = {'alert_data': alert_data,"purge_duration":purge_duration, 'distribution_and_status': distribution_and_status}
        status = 'success'
        message = 'Data is fetched successfully'

        return marshal(respcls(message, status, chart_data),
                       parentwrapper.common_response_wrapper, skip_none=True)


def count(distribution_and_status):
    for count in distribution_and_status['hosts_platform_count']:
        if count['count'] > 0:
            return True
        else:
            return
