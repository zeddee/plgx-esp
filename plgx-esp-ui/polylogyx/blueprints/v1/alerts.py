import datetime

from flask_restplus import Namespace, Resource
from polylogyx.blueprints.v1.utils import *
from polylogyx.utils import require_api_key
from polylogyx.dao.v1 import alerts_dao as dao
from polylogyx.wrappers.v1 import parent_wrappers as parentwrapper
from polylogyx.wrappers.v1.resultlog_wrappers import result_log_wrapper

ns = Namespace('alerts', description='Alerts related operations')


@require_api_key
@ns.route('/count_by_source', endpoint='alert_source_count')
@ns.doc(params={})
class AlertSourceCount(Resource):
    from flask_restplus import inputs

    parser = requestparse(['resolved', 'duration', 'type', 'date', 'host_identifier', 'rule_id'],
                          [inputs.boolean, int, int, str, str, int],
                          ['True to get all resolved alerts', 'duration', 'type', 'date', 'host_identifier', 'rule id'],
                          [False, False, False, False, False, False],
                          [None, [1, 2, 3, 4], [1, 2], None, None, None],
                          [None, 3, 2, None, None, None])

    @ns.expect(parser)
    @ns.marshal_with(parentwrapper.common_response_wrapper)
    def get(self):
        args = self.parser.parse_args()

        start_date = None
        end_date = None
        if args['date']:
            try:
                start_date, end_date = get_start_dat_end_date(args)
            except:
                return abort(400, {'message': 'Date format passed is invalid!'})
        node = node_dao.get_node_by_host_identifier(args['host_identifier'])
        alert_source_tuple_list = alerts_dao.get_distinct_alert_source(args['resolved'], start_date, end_date, node, args['rule_id'])
        source_names = ['virustotal', 'rule', 'ibmxforce', 'alienvault', 'ioc']
        alert_source_count = [{'name': source, 'count': 0} for source in source_names]
        for source in alert_source_count:
            for source_count in alert_source_tuple_list:
                if source['name'] == source_count[0]:
                    source['count'] = source_count[1]
        alerts_data = {"alert_source": alert_source_count}
        if alerts_data['alert_source']:
            message = 'Data is fetched successfully'
            status = 'success'
        else:
            message = 'No data present'
            status = 'failure'
            alerts_data = {}
        return marshal(respcls(message, status, alerts_data),
                       parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('', endpoint='alert_data')
@ns.doc(params={'start': 'Start num for pagination', 'limit': 'End num for pagination',
                'source': 'source name'})
class AlertsData(Resource):
    from flask_restplus import inputs

    parser = requestparse(['start', 'limit', 'source', 'searchterm', 'resolved', 'event_ids', 'duration', 'type', 'date', 'host_identifier', 'query_name', 'rule_id', 'events_count'],
                          [int, int, str, str, inputs.boolean, list, int, int, str, str, str, int, inputs.boolean],
                          ['Start', 'Limit', 'source', 'searchterm',
                           'True to get all resolved alerts', 'Event Ids', 'Duration', 'Type', 'Date', 'host_identifier', 'query_name', 'rule_id', 'events_count(true/false)'],
                          [False, False, False, False, False, False, False, False, False, False, False, False, False], [None, None, None, None, None, None, [1,2,3,4], [1,2], None, None, None, None, None],
                          [0, 10, None, "", False, None, 3, 2, None, None, None, None, True])

    put_parser = requestparse(['resolve', 'alert_ids'], [inputs.boolean, list],
                              ['Set True to resolve or False to move to non-resolved state', 'alert ids to resolve/unresolve'], [False, True])

    @ns.expect(parser)
    def post(self):
        """ Display Alerts by source table content. """
        from polylogyx.dao.v1.hosts_dao import get_node_by_host_identifier
        from polylogyx.dao.v1.queries_dao import get_query_by_name
        from polylogyx.dao.v1.rules_dao import get_rule_by_id
        args = self.parser.parse_args()
        source = args['source']
        start = args['start']
        limit = args['limit']
        resolved = args['resolved']
        event_ids = args['event_ids']
        query_name = args['query_name']
        rule_id = args['rule_id']
        start_date = None
        end_date = None
        node_id = None

        if args['host_identifier']:
            node = get_node_by_host_identifier(args['host_identifier'])
            if not node:
                return marshal(respcls("No Host present for the host identifier given!", "failure"), parentwrapper.common_response_wrapper, skip_none=True)
            node_id = node.id
        if query_name and not get_query_by_name(query_name):
            return marshal(respcls("No Query present for the query name given!", "failure"),
                               parentwrapper.common_response_wrapper, skip_none=True)
        if rule_id and not get_rule_by_id(rule_id):
            return marshal(respcls("No Rule present for the rule id given!", "failure"),
                           parentwrapper.common_response_wrapper, skip_none=True)
        if args['date']:
            try:
                start_date, end_date = get_start_dat_end_date(args)
            except:
                return abort(400, {'message': 'Date format passed is invalid!'})

        results = get_results_by_alert_source(start, limit, source, args['searchterm'], resolved, event_ids, start_date, end_date, node_id, query_name, rule_id, args['events_count'])
        message = "Data is fetched successfully"
        status = "success"
        return marshal(respcls(message, status, results), parentwrapper.common_response_wrapper, skip_none=True)

    @ns.expect(put_parser)
    def put(self):
        args = self.put_parser.parse_args()
        status = args['resolve']
        alert_ids = args['alert_ids']
        if status:
            dao.edit_alerts_status_by_alert(alert_ids, True)
        else:
            dao.edit_alerts_status_by_alert(alert_ids)
        message = "Selected alerts status is changed successfully"
        status = "success"
        return marshal(respcls(message, status), parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/<int:alert_id>', endpoint='alert_investigate')
@ns.doc(params={})
class AlertInvestigate(Resource):

    @ns.marshal_with(parentwrapper.common_response_wrapper)
    def get(self, alert_id):
        alert = alerts_dao.get_alerts_by_alert_id(alert_id)
        if alert:
            alert = alerts_details(alert)
            message = "Successfully fetched the Alerts data"
            status = 'success'
        else:
            message = 'No Alerts present for the alert id given'
            status = 'failure'
            alert = {}
        return marshal(respcls(message, status, alert),
                       parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/<int:alert_id>/alerted_events', endpoint='alerted_events')
@ns.doc(params={})
class AlertAggregatedEvents(Resource):

    def get(self, alert_id):
        alert = alerts_dao.get_alerts_by_alert_id(alert_id)
        if alert:
            queryset = dao.get_all_events_of_an_alert(alert)
            if queryset:
                events = [event.to_dict() for event in queryset]
            else:
                events = []
            message = "Successfully fetched the Alert's events data"
            status = 'success'
        else:
            message = 'No Alert present for the alert id given'
            status = 'failure'
            events = []
        return marshal(respcls(message, status, events),
                       parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/alert_source/export', endpoint='export_alert')
@ns.doc(params={'source': 'source name'})
class ExportCsvAlerts(Resource):
    parser = requestparse(['source', 'duration', 'type', 'date', 'host_identifier', 'rule_id', 'event_ids'],
                          [str, int, int, str, str, int, list],
                          ['source name', 'duration', 'type', 'date', 'host identifier', 'rule id', 'event_ids'],
                          [True, False, False, False, False, False, False],
                          [None, [1, 2, 3, 4], [1, 2], None, None, None, None],
                          [None, 3, 2, None, None, None, None])

    @ns.expect(parser)
    def post(self):
        args = self.parser.parse_args()
        source = args['source']
        start_date = None
        end_date = None
        if args['date']:
            try:
                start_date, end_date = get_start_dat_end_date(args)
            except:
                return abort(400, {'message': 'Date format passed is invalid!'})
        node = node_dao.get_node_by_host_identifier(args['host_identifier'])
        results = alerts_dao.get_alert_source(source, start_date, end_date, node, args['rule_id'], args['event_ids'])
        return get_response(results)
