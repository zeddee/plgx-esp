from flask_restplus import Namespace, Resource

from polylogyx.blueprints.v1.utils import *
from polylogyx.utils import require_api_key, validate_osquery_query
from polylogyx.dao.v1 import distributed_dao as dao, hosts_dao as nodedao
from polylogyx.wrappers.v1 import parent_wrappers as parentwrapper

ns = Namespace('distributed', description='distributed query related operations')


@require_api_key
@ns.route('/add', endpoint = 'distributed_add')
@ns.doc(params={'query':'query', 'tags': 'tags', 'nodes':'nodes', 'description':'description for the post method'})
class DistributedQueryClass(Resource):
    '''
    Retrieve an osquery configuration for a given node.
    returns: an osquery configuration file
    '''
    parser = requestparse(['query','tags','nodes','description'],[str, str, str, str],['query','tags list string seperated by commas','nodes list by comma separated','description'],[True, False, False, False])

    @ns.expect(parser)
    def post(self, node=None):
        from manage import declare_queue

        args = self.parser.parse_args()  # need to exists for input payload validation
        onlineNodes = 0
        hosts_array = []
        sql = args['query']
        if not validate_osquery_query(sql):
            message = u'Field must contain valid SQL to be run against osquery tables'
        else:
            status = 'success'
            message = 'Distributed query is sent successfully'
            tag_all = 'all'
            current_app.logger.info(
                "%s - %s checking in for distributed query",
                request.remote_addr, node
            )
            # all nodes get this query
            nodes = []
            tags = []
            if args['tags']:
                tags = args['tags'].split(',')
            if args['nodes']:
                nodeKeyList = args['nodes'].split(',')
            else:
                nodeKeyList = []

            if not nodeKeyList and not tags:
                # all nodes get this query
                nodes = nodedao.get_all_nodes()

            if nodeKeyList:
                nodes.extend(nodedao.extendNodesByNodeKeyList(nodeKeyList))
            if tags:
                nodes.extend(nodedao.extendNodesByTag(tags))
            query = dao.add_distributed_query(sql,args['description'])

            if nodes:
                for node in nodes:
                    if node.node_is_active():
                        onlineNodes += 1
                        hosts_array.append({"host_identifier": node.host_identifier, "hostname": node.display_name, "node_id": node.id})
                        task = dao.create_distributed_task_obj(node, query)
                        db.session.add(task)
                else:
                    db.session.commit()
            declare_queue(query.id)
            if onlineNodes == 0:
                message = 'No active node present'
            else:
                current_app.logger.info("Distributed Query {0} is added to the hosts {1}".format(query.id, [host['host_identifier'] for host in hosts_array]))
                return marshal(respcls(message, status, {'query_id': query.id, 'onlineNodes': onlineNodes, 'online_nodes_details': hosts_array}), parentwrapper.common_response_wrapper)
        return marshal(respcls(message), parentwrapper.failure_response_parent)
