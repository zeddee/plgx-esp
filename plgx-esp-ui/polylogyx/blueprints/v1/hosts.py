from flask_restplus import Namespace, Resource, inputs

from polylogyx.blueprints.v1.utils import *
from polylogyx.utils import require_api_key, assemble_configuration, assemble_additional_configuration
from polylogyx.dao.v1 import hosts_dao as dao, tags_dao
from polylogyx.wrappers.v1 import host_wrappers as wrapper, parent_wrappers as parentwrapper

ns = Namespace('hosts', description='nodes related operations')


@require_api_key
@ns.route('', endpoint='hosts_list')
class HostsList(Resource):
    """List all Nodes Filtered"""
    parser = requestparse(['status', 'platform', 'searchterm', 'start', 'limit', 'enabled', 'alerts_count'], [bool, str, str, int, int, inputs.boolean, inputs.boolean],
                          ['status(true/false)', 'platform(windows/linux/darwin)', 'searchterm', 'start', 'limit', 'enabled(true/false)', 'alerts_count(true/false)'], [False, False, False, False, False, False, False], [None, ["windows", "linux", "darwin"], None, None, None, None, None], [None, None, "", None, None, True, True])

    @ns.expect(parser)
    def post(self):
        args = self.parser.parse_args()
        query_set = dao.get_hosts_paginated(args['status'], args['platform'], args['searchterm'], args['enabled'], args['alerts_count']).offset(args['start']).limit(args['limit']).all()
        total_count = dao.get_hosts_total_count(args['status'], args['platform'], args['enabled'])
        if query_set:
            results = []
            for node_alert_count_pair in query_set:
                if args['alerts_count']:
                    node_dict = node_alert_count_pair[0].get_dict()
                    node_dict['alerts_count'] = node_alert_count_pair[1]
                else:
                    node_dict = node_alert_count_pair.get_dict()
                results.append(node_dict)
            data = {'results': results, 'count': dao.get_hosts_paginated(args['status'], args['platform'], args['searchterm'], args['enabled'], args['alerts_count']).count(), 'total_count':total_count}
        else:
            data = {'results': [], 'count': 0, 'total_count': total_count}
        status = "success"
        message = "Successfully fetched the hosts details"
        return marshal(respcls(message, status, data), parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/export')
@ns.doc(params = {})
class NodesCSV(Resource):
    '''Returns a csv file object with nodes info as data'''
    def get(self):
        from sqlalchemy import desc, and_

        record_query = Node.query.filter(and_(Node.state!=Node.REMOVED, Node.state!=Node.DELETED)).order_by(desc(Node.id)).all()
        results = []
        for value in record_query:
            res = {}
            data = value.to_dict()
            res['Host_Identifier'] = value.display_name
            if value.os_info:
                res['os'] = value.os_info['name']
            else:
                res['os'] = value.platform

            res['last_ip'] = data["last_ip"]
            res['tags'] = [tag.to_dict() for tag in value.tags]
            res['id'] = data['id']
            res['health'] = value.node_is_active()
            res['platform'] = data["platform"]
            results.append(res)

        headers = []
        if results:
            firstRecord = results[0]
            for key in firstRecord.keys():
                headers.append(key)

        bio = BytesIO()
        writer = csv.writer(bio)
        writer.writerow(headers)

        for data in results:
            row = []
            row.extend([data.get(column, '') for column in headers])
            writer.writerow(row)

        bio.seek(0)

        file_data = send_file(
            bio,
            mimetype='text/csv',
            as_attachment=True,
            attachment_filename='nodes.csv'
        )
        return file_data


@require_api_key
@ns.route('/<string:host_identifier>', endpoint='node_details')
@ns.route('/<int:node_id>', endpoint='node_details_by_id')
class NodeDetailsList(Resource):
    """List a Node Details"""

    def get(self, host_identifier=None, node_id=None):
        data = None
        if node_id:
            queryset = dao.getNodeById(node_id)
        elif host_identifier:
            queryset = dao.get_node_by_host_identifier(host_identifier)
        else: queryset = None
        db.session.commit()

        if not queryset:
            message = "There is no host exists with this host identifier or node id given!"
            status = "failure"
        else:
            data = marshal(queryset, wrapper.nodewrapper)
            if not data: data={}
            message = "Node details are fetched successfully"
            status = "success"
        return marshal(respcls(message, status, data), parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/<string:host_identifier>/alerts/distribution', endpoint='host_alerts_count_for_host_identifier')
@ns.route('/<int:node_id>/alerts/distribution', endpoint='host_alerts_count_for_node_id')
class HostAlertsDistribution(Resource):
    """List a Node Details"""

    def get(self, host_identifier=None, node_id=None):
        if node_id:
            node = dao.getNodeById(node_id)
        elif host_identifier:
            node = dao.get_node_by_host_identifier(host_identifier)
        else:
            node = None
        if not node:
            data = None
            message = "There is no host exists with this host identifier or node id given!"
            status = "failure"
        else:
            data = {}
            data['sources'] = dao.host_alerts_distribution_by_source(node)
            data['rules'] = [{"name": rule_count_pair[0], "count": rule_count_pair[1]} for rule_count_pair in dao.host_alerts_distribution_by_rule(node)]
            message = "Alerts distribution details are fetched for the host"
            status = "success"
        return marshal(respcls(message, status, data), parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/count', endpoint='nodes_related_count')
class NodeCountList(Resource):
    """Lists all Nodes Filtered count"""

    def get(self):
        data = dao.get_hosts_filtered_status_platform_count()
        return marshal(respcls("Successfully fetched the nodes status count", 'success', data),
                       parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/status_logs', endpoint='node_status_logs')
class HostStatusLogs(Resource):
    """Host Status Logs"""
    parser = requestparse(['host_identifier', 'node_id', 'start', 'limit', 'searchterm'], [str, int, int, int, str], ["host identifier of the node", "id of the node", 'start', 'limit', 'searchterm'], [False, False, False, False, False], [None, None, None, None, None], [None, None, None, None, ''])

    @ns.expect(parser)
    def post(self):
        args = self.parser.parse_args()
        data = None
        status = "failure"
        if args['node_id'] is not None or args['host_identifier'] is not None:
            if args['host_identifier'] is not None:
                qs = dao.get_node_by_host_identifier(args['host_identifier'])
            else:
                node_id = args['node_id']
                qs = dao.getNodeById(node_id)
            if qs:
                data = {'results': marshal(dao.get_status_logs_of_a_node(qs, args['searchterm']).offset(args['start']).limit(args['limit']).all(), wrapper.node_status_log_wrapper), 'count':dao.get_status_logs_of_a_node(qs, args['searchterm']).count(), 'total_count':dao.get_status_logs_total_count(qs)}
                message = "Successfully fetched the host's status logs"
                status = "success"
            else:
                message = "Host identifier or node id passed is not correct!"
        else:
            message = "Please pass one of node id or host identifier!"

        return marshal(respcls(message, status, data), parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/additional_config', endpoint='node_additional_config')
class HostAdditionalConfig(Resource):
    """Additional Config of a Node"""
    parser = requestparse(['host_identifier', 'node_id'], [str, int], ["host identifier of the node", "id of the node"], [False, False])

    @ns.expect(parser)
    def post(self):
        args = self.parser.parse_args()
        config = None
        status = "failure"
        if args['node_id'] is not None or args['host_identifier'] is not None:
            if args['host_identifier'] is not None:
                node = dao.get_node_by_host_identifier(args['host_identifier'])
            else:
                node_id = args['node_id']
                node = dao.getNodeById(node_id)
            if node:
                config = assemble_additional_configuration(node)
                status = "success"
                message = "Successfully fetched additional config of the node for the host identifier passed"
            else:
                message = "Host identifier or node id passed is not correct!"
        else:
            message = "Atleast one of host identifier or node id should be given!"

        return marshal(respcls(message, status, config), parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/config', endpoint='node_full_config')
class HostFullConfig(Resource):
    """Full Config of a Node"""
    parser = requestparse(['host_identifier', 'node_id'], [str, int], ["host identifier of the node", "id of the node"], [False, False])

    @ns.expect(parser)
    def post(self):
        args = self.parser.parse_args()
        config = None
        status = "failure"
        if args['node_id'] is not None or args['host_identifier'] is not None:
            if args['host_identifier'] is not None:
                node = dao.get_node_by_host_identifier(args['host_identifier'])
            else:
                node_id = args['node_id']
                node = dao.getNodeById(node_id)
            if node:
                config = assemble_configuration(node)
                status = "success"
                message = "Successfully fetched full config of the node for the host identifier passed"
            else:
                message = "Host identifier or node id passed is not correct!"
        else:
            message = "Atleast one of host identifier or node id should be given!"

        return marshal(respcls(message, status, config), parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/recent_activity/count', endpoint='node_recent_activity_count')
@ns.doc(params={'host_identifier': 'Host identifier of the Node', 'node_id': 'id of the Node'})
class RecentActivityCount(Resource):
    """Recent Activity count of a Node"""
    parser = requestparse(['host_identifier', 'node_id'], [str, int], ["host identifier of the node", "id of the node"], [False, False])

    @ns.expect(parser)
    def post(self):
        args = self.parser.parse_args()
        status = "failure"
        data = None
        if args['node_id'] is not None or args['host_identifier'] is not None:
            if args['host_identifier'] is not None:
                node = dao.get_node_by_host_identifier(args['host_identifier'])
                if node: node_id = node.id
                else: node_id = None
            else:
                node_id = args['node_id']
            if not node_id: message = "Please pass correct host identifier or node id to get the results"
            else:
                data = [{'name': query[0], 'count': query[1]} for query in dao.get_result_log_count(node_id)]
                status = "success"
                message = "Successfully fetched the count of schedule query results count of host identifier passed"
        else:
            message = "Atleast one of host identifier or node id should be given!"
        return marshal(respcls(message, status, data), parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/recent_activity', endpoint='node_recent_activity_results')
@ns.doc(params={'host_identifier': 'Host identifier of the Node', 'query_name': 'query name', 'start': 'start count',
                'limit': 'end count'})
class RecentActivityResults(Resource):
    """Recent Activity results of a query of a Node"""

    parser = requestparse(['host_identifier', 'node_id', 'query_name', 'start', 'limit', 'searchterm'], [str, int, str, int, int, str],
                          ["host identifier of the node", "node_id", "query", "start count", "end count", "searchterm"],
                          [False, False, True, False, False, False], [None, None, None, None, None, None], [None, None, None, 0, 10, ""])

    @ns.expect(parser)
    def post(self):
        args = self.parser.parse_args()

        status = "failure"
        data = {}
        if args['node_id'] is not None or args['host_identifier'] is not None:
            if args['host_identifier'] is not None:
                node = dao.get_node_by_host_identifier(args['host_identifier'])
                if node:
                    node_id = node.id
                else:
                    node_id = None
            else:
                node_id = args['node_id']
            if not node_id:
                message = "Please pass correct host identifier or node id to get the results"
            else:
                qs = dao.get_result_log_of_a_query(node_id, args['query_name'], args['start'],
                                                   args['limit'], args['searchterm'])
                data = {'count': qs[0], 'total_count': qs[2], 'results': [
                    {'timestamp': list_ele[1].strftime('%m/%d/%Y %H/%M/%S'), 'action': list_ele[2],
                     'columns': list_ele[3]} for list_ele in qs[1]]}
                status = "success"
                message = "Successfully fetched the count of schedule query results count of host identifier passed"
        else:
            message = "Atleast one of host identifier or node id should be given!"

        return marshal(respcls(message, status, data), parentwrapper.common_response_wrapper, skip_none=True)


# Modify Tag section

@require_api_key
@ns.route('/<string:host_identifier>/tags', endpoint='node_tags')
@ns.route('/<int:node_id>/tags', endpoint='node_tags_by_node_id')
class ListTagsOfNode(Resource):
    """Resource for tags of a host"""
    parser = requestparse(['tag'], [str],
                          ["tag to add/remove for the node"], [True])

    @ns.doc(params={'host_identifier': 'Host identifier of the Node', 'node_id': 'id of the Node'})
    def get(self, host_identifier=None, node_id=None):
        """Lists tags of a node by its host_identifier"""
        status = 'failure'
        if host_identifier: node = dao.get_node_by_host_identifier(host_identifier)
        elif node_id: node = dao.getNodeById(node_id)
        else: node = None
        if not node:
            message = "Host id or node id passed it not correct"
            data = None
        else:
            data = [tag.value for tag in node.tags]
            status = "success"
            message = "Successfully fetched the tags of host"
        return marshal(respcls(message, status, data), parentwrapper.common_response_wrapper, skip_none=True)

    @ns.doc(params={'host_identifier': 'Host identifier of the Node', 'node_id': 'id of the Node', 'tag':"tag to add to host"})
    @ns.expect(parser)
    def post(self, host_identifier=None, node_id=None):
        """Creates tags of a node by its host_identifier"""
        args = self.parser.parse_args()
        status = 'failure'

        if host_identifier: node = dao.get_node_by_host_identifier(host_identifier)
        elif node_id: node = dao.getNodeById(node_id)
        else: node = None
        if node:
            tag = args['tag'].strip()
            if not tag:
                message = "Tag provided is invalid!"
            else:
                tag = tags_dao.create_tag_obj(tag)
                node.tags.append(tag)
                node.save()
                status="success"
                message = "Successfully created tags to host"
        else:
            message = "Host id or node id passed it not correct"

        return marshal(respcls(message, status), parentwrapper.common_response_wrapper, skip_none=True)

    @ns.doc(params={'host_identifier': 'Host identifier of the Node', 'node_id': 'id of the Node', 'tag': 'tag to remove'})
    @ns.expect(parser)
    def delete(self, host_identifier=None, node_id=None):
        """Remove tags of a node by its host_identifier"""
        args = self.parser.parse_args()
        status = 'failure'

        if host_identifier:
            node = dao.get_node_by_host_identifier(host_identifier)
        elif node_id:
            node = dao.getNodeById(node_id)
        else:
            node = None
        if node:
            tag = args['tag'].strip()
            tag = tags_dao.get_tag_by_value(tag)
            if tag:
                if dao.is_tag_of_node(node, tag):
                    node.tags.remove(tag)
                    node.save()
                    message = "Successfully removed tags from host"
                    status = "success"
                else:
                    message = "Tag provided is not in host's tag list, Please check tag once again"
            else:
                message = "Tag provided doesnot exists"
        else:
            message = "Host id or node id passed it not correct"
        return marshal(respcls(message, status), parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/search/export', endpoint="nodes_search_export")
@ns.doc(params={})
class ExportNodeSearchQueryCSV(Resource):
    '''Export node search query to csv'''
    parser = requestparse(['conditions', 'host_identifier', 'query_name', 'node_id'], [dict, str, str, int],
                          ["conditions to search for", 'host_identifier of the node', 'name of the schedule query', 'id of the node'], [False, False, True, False])

    @ns.expect(parser)
    def post(self):

        args = self.parser.parse_args()
        host_identifier = args['host_identifier']
        conditions = args['conditions']
        query_name = args['query_name']
        node_id = args['node_id']

        if node_id or host_identifier:
            if host_identifier:
                node_id = get_node_id_by_host_id(host_identifier)
                if not node_id:
                    return marshal(respcls("Host identifier given is invalid!", "failure"),
                                   parentwrapper.common_response_wrapper, skip_none=True)
        else:
            return marshal(respcls("Atleast one of host identifier or node id is required!", "failure"), parentwrapper.common_response_wrapper, skip_none=True)
        if conditions:
            try:
                search_rules = SearchParser()
                root = search_rules.parse_group(conditions)
                filter = root.run('', [], 'result_log')
            except Exception as e:
                message = str(e)
                return marshal(respcls(message, "failure"), parentwrapper.common_response_wrapper, skip_none=True)

            try:
                results = dao.node_result_log_search_results(filter, node_id, query_name)
            except:
                message = "Unable to find data for the payload given"
                return marshal(respcls(message, "failure"), parentwrapper.common_response_wrapper, skip_none=True)
        else:
            results = dao.node_result_log_results(node_id, query_name)

        if results:
            results = [r for r, in results]
            headers = []
            if not len(results) == 0:
                firstRecord = results[0]
                for key in firstRecord.keys():
                    headers.append(key)

            bio = BytesIO()
            writer = csv.writer(bio)
            writer.writerow(headers)

            for data in results:
                row = []
                row.extend([data.get(column, '') for column in headers])
                writer.writerow(row)

            bio.seek(0)

            response = send_file(
                bio,
                mimetype='text/csv',
                as_attachment=True,
                attachment_filename=query_name+'_'+str(node_id)+str(dt.datetime.now())+'.csv'
            )
            return response

        else:
            message = "There are no matching results for the payload given"
        return marshal(respcls(message, "failure"), parentwrapper.common_response_wrapper, skip_none=True)


@ns.route('/<string:host_identifier>/delete', endpoint='node_removed')
@ns.route('/<int:node_id>/delete', endpoint='node_removed_by_id')
class NodeRemoved(Resource):

    @ns.doc(params={'node_id': "id of the host", 'host_identifier': "host identifier of the host"})
    def delete(self, host_identifier=None, node_id=None):
        node = None
        message = "Node is not present with this node id or host identifier"
        status = "failure"
        if host_identifier:
            node = dao.get_node_by_host_identifier(host_identifier)
        if node_id:
            node = dao.getNodeById(node_id)
        if node:
            current_app.logger.info("Host {} is requested for permanent deletion".format(node.host_identifier))
            dao.delete_host(node)
            message = "Successfully deleted the host"
            status = "Success"
            return marshal(respcls(message, status), parentwrapper.common_response_wrapper, skip_none=True)
        return marshal(respcls(message, status), parentwrapper.common_response_wrapper, skip_none=True)

    @ns.doc(params={'node_id': "id of the host", 'host_identifier': "host identifier of the host"})
    def put(self, host_identifier=None, node_id=None):
        node = None
        message = "Node is not present with this node id or host identifier"
        status = "failure"
        if host_identifier:
            node = dao.get_node_by_host_identifier(host_identifier)
        if node_id:
            node = dao.getNodeById(node_id)
        if node:
            current_app.logger.info("Host {} is requested to be disabled for all his activities from agent".format(node.host_identifier))
            dao.soft_remove_host(node)
            message = "Successfully removed the host"
            status = "Success"
            return marshal(respcls(message, status), parentwrapper.common_response_wrapper, skip_none=True)
        return marshal(respcls(message, status), parentwrapper.common_response_wrapper, skip_none=True)


@ns.route('/<string:host_identifier>/enable', endpoint='node_enabled')
@ns.route('/<int:node_id>/enable', endpoint='node_enabled_by_id')
class NodeEnabled(Resource):

    @ns.doc(params={'node_id': "id of the host", 'host_identifier': "host identifier of the host"})
    def put(self, host_identifier=None, node_id=None):
        node = None
        message = "Node is not present with this node id or host identifier"
        status = "failure"
        if host_identifier:
            node = dao.get_disable_node_by_host_identifier(host_identifier)
        if node_id:
            node = dao.getDisableNodeById(node_id)
        if node:
            current_app.logger.info("Host {} is requested to be enabled again".format(node.host_identifier))
            dao.enable_host(node)
            message = "Successfully enabled the host"
            status = "Success"
            return marshal(respcls(message, status), parentwrapper.common_response_wrapper, skip_none=True)
        return marshal(respcls(message, status), parentwrapper.common_response_wrapper, skip_none=True)

