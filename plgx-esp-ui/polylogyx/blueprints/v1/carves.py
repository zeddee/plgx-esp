from flask_restplus import Namespace, Resource

from flask import make_response

from polylogyx.blueprints.v1.utils import *
from polylogyx.utils import require_api_key
from polylogyx.dao.v1 import hosts_dao as nodedao, carves_dao as dao
from polylogyx.wrappers.v1 import carve_wrappers as wrapper, parent_wrappers as parentwrapper
from polylogyx.models import DistributedQueryTask,db,CarveSession

ns = Namespace('carves', description='Carves related operations')


@require_api_key
@ns.route('', endpoint='node_carves_list')
@ns.doc(params={'host_identifier': 'Host identifier of the Node', 'start': 'Start Number',
                'limit': 'Maximun Number of Carves'})
class NodeCarvesList(Resource):
    '''Lists out the carves for a specific node when host_identifier given otherwise returns all carves'''
    parser = requestparse(['host_identifier', 'start', 'limit', 'searchterm'], [str, int, int, str],
                          ["host identifier of the node", "Start Number", "Maximun Number of Carves", "Searchterm"],
                          [False, False, False, False], [None, None, None, None], [None, 0, 10, ''])

    @ns.expect(parser)
    def post(self):
        from polylogyx.dao.v1.hosts_dao import getHostNameByNodeId
        carves = None
        status = 'success'
        args = self.parser.parse_args()
        host_identifier = args['host_identifier']

        if host_identifier:
            node = nodedao.get_node_by_host_identifier(host_identifier)
            if not node:
                status = 'failure'
                message = 'Node with this identifier does not exists'
            else:
                carves = marshal(dao.get_carves_by_node_id(node.id, args['searchterm']).offset(
                    args['start']).limit(args['limit']).all(), wrapper.carves_wrapper)
                count = dao.get_carves_by_node_id(node.id, args['searchterm']).count()
                total_count = dao.get_carves_total_count(node_id=node.id)
                for carve in carves:
                    carve['hostname'] = getHostNameByNodeId(carve['node_id'])
                carves = {'count':count, 'results':carves, 'total_count':total_count}
                message = 'Successfully fetched the Carves data'
        else:
            carves = marshal(dao.get_carves_all(args['searchterm']).offset(args['start']).limit(args['limit']).all(),
                             wrapper.carves_wrapper)
            count = dao.get_carves_all(args['searchterm']).count()
            total_count = dao.get_carves_total_count(node_id=None)
            for carve in carves:
                carve['hostname'] = getHostNameByNodeId(carve['node_id'])
            carves = {'count':count, 'results':carves, 'total_count':total_count}
            message = 'Successfully fetched the Carves data'
            status = "success"
        return marshal(respcls(message,status,carves),parentwrapper.common_response_wrapper)


@require_api_key
@ns.route('/download/<string:session_id>', endpoint='download_carves')
@ns.doc(params={'session_id': 'session id of the carve to Download'})
class DownloadCarves(Resource):
    '''Download carves for the session id given'''

    def get(self, session_id=None):
        status = 'failure'
        if not session_id:
            message = 'Please provide a session id'
        else:
            carve_session = dao.get_carves_by_session_id(session_id)
            if carve_session:
                response = make_response()
                response.headers['Cache-Control'] = 'no-cache'
                response.headers['Content-Type'] = 'application/octet-stream'
                response.headers['X-Accel-Redirect'] = '/carves/' + carve_session.node.host_identifier + '/' + carve_session.archive
                return response
            else:
                message = 'This session id does not exist'

        return marshal(respcls(message,status), parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/query', endpoint='get_carves_by_query_id_post')
@ns.doc(params={'query_id': 'query id','host_identifier': 'host identifier of the node'})
class CarveSessionByPostQueryId(Resource):
    '''Create Carves session by query id'''
    parser = requestparse(['query_id', 'host_identifier'], [str, str], ["query id", "host_identifier"], [True, True])

    @ns.expect(parser)
    def post(self):
        status = 'failure'
        args = self.parser.parse_args()
        host_identifier = args['host_identifier']
        query_id = args['query_id']
        carve_session = {}
        node = nodedao.get_node_by_host_identifier(host_identifier)
        if not node:
            message = 'Node with this identifier does not exists'
        else:
            dqt = db.session.query(DistributedQueryTask).filter(
                DistributedQueryTask.distributed_query_id == query_id).filter(
                DistributedQueryTask.node_id==node.id).first()
            if dqt:
                carve_session = db.session.query(CarveSession).filter(CarveSession.request_id == dqt.guid).first()
                if carve_session:
                    carve_session = marshal(carve_session, wrapper.carves_wrapper)
                    status = "success"
                    message = "Successfully fetched the Carve"
                    return marshal(respcls(message, status, carve_session), parentwrapper.common_response_wrapper)
                else:
                    message = "Carve not started"
            else:
                message = "Query id provided is invalid!"

        return marshal(respcls(message, status, carve_session), parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/delete', endpoint='delete_carves_by_session_id_post')
@ns.doc(params={'session_id': 'session id'})
class DeleteCarveSessionByPostSessionId(Resource):
    '''Delete Carves session by session id'''
    parser = requestparse(['session_id'], [str], ["session id"], [True])

    @ns.expect(parser)
    def post(self):
        args = self.parser.parse_args()
        session_id = args['session_id']
        carvesession = dao.get_carves_by_session_id(session_id)
        if carvesession:
            current_app.logger.info("Carve {} is requested to delete".format(carvesession.id))
            dao.delete_carve_by_session_id(session_id)
            db.session.commit()
            message = "Successfully deleted the Carve for the session id given!"
            status = "success"
        else:
            message = "No Carve is found for the session id provided!"
            status = "failure"
        return marshal(respcls(message, status), parentwrapper.common_response_wrapper)
