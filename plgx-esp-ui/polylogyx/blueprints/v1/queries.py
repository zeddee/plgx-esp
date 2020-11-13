from flask_restplus import Namespace, Resource

from polylogyx.blueprints.v1.utils import *
from polylogyx.utils import require_api_key, validate_osquery_query, create_tags, is_number_positive
from polylogyx.dao.v1 import queries_dao as dao, tags_dao
from polylogyx.wrappers.v1 import parent_wrappers as parentwrapper, query_wrappers as wrapper

ns = Namespace('queries', description='queries related operations')


parser = reqparse.RequestParser()
nodes_post = parser.copy()


@require_api_key
@ns.route('', endpoint = "list_queries")
@ns.doc(params={})
class QueriesList(Resource):
    '''Lists all queries of the Nodes'''
    parser = requestparse(["start", "limit", "searchterm"], [int, int, str],
                          ["start", "limit", "searchterm"], [False, False, False], [None, None, None], [None, None, ''])

    @ns.expect(parser)
    @ns.marshal_with(parentwrapper.common_response_wrapper)
    def post(self):
        args = self.parser.parse_args()
        queryset = dao.get_all_queries(args['searchterm']).offset(args['start']).limit(args['limit']).all()
        data = marshal(queryset, wrapper.query_wrapper)
        for i in range(len(data)):
            data[i]['tags'] = [tag.to_dict() for tag in queryset[i].tags]
            data[i]['packs'] = [pack.name for pack in queryset[i].packs]
        message = "Successfully fetched the queries info!"
        status = "success"
        if not data:
            data = []
        data = {'count':dao.get_all_queries(args['searchterm']).count(), 'total_count':dao.get_total_count(), 'results':data}
        return respcls(message,status,data)


@require_api_key
@ns.route('/packed', endpoint = "list_packed_queries")
@ns.doc(params={})
class PackedQueriesList(Resource):
    '''List all packed queries of the Nodes'''

    parser = requestparse(["start", "limit", "searchterm"], [int, int, str],
                          ["start", "limit", "searchterm"], [False, False, False], [None, None, None], [None, None, ''])

    @ns.expect(parser)
    @ns.marshal_with(parentwrapper.common_response_wrapper)
    def post(self):
        args = self.parser.parse_args()
        queryset = dao.get_all_packed_queries(args['searchterm']).offset(args['start']).limit(args['limit']).all()
        data = marshal(queryset,wrapper.query_wrapper)
        for i in range(len(data)):
            data[i]['tags'] = [tag.to_dict() for tag in queryset[i].tags]
            data[i]['packs'] = [pack.name for pack in queryset[i].packs]
        message = "Successfully fetched the packed queries info"
        status = "success"
        if not data:
            data = []
        data = {'count':dao.get_all_packed_queries(args['searchterm']).count(), 'total_count':dao.get_total_packed_queries_count(), 'results':data}
        return respcls(message,status,data)



@require_api_key
@ns.route('/<int:query_id>', endpoint = "query_by_id")
@ns.doc(params={'query_id': 'id of the query'})
class QueryById(Resource):
    ''' Returns the query info for the given query id'''

    def get(self, query_id):
        if query_id:
            query_qs = dao.get_query_by_id(query_id)
            if query_qs:
                query=marshal(query_qs,wrapper.query_wrapper)
                query['tags'] = [tag.to_dict() for tag in query_qs.tags]
                query['packs'] = [pack.name for pack in query_qs.packs]
                return marshal(respcls("Successfully fecthed the query info for the given id","success",query) , parentwrapper.common_response_wrapper)
            else:
                message = "Query with this id does not exist"
        else:
            message = "Missing query id"
        return marshal(respcls(message), parentwrapper.failure_response_parent)


@require_api_key
@ns.route('/<int:query_id>', endpoint = "edit_query")
@ns.doc(params={'query_id': 'id of the query'})
class EditQueryById(Resource):
    '''Edit query by its id'''
    parser = requestparse(
        ['name', 'query', 'interval', 'tags', 'platform', 'version', 'description', 'value', 'snapshot', 'packs'],
        [str, str, int, str, str, str, str, str, str, str],
        ["name of the query", "query", "interval of the query", "list of comma separated tags of the query to add", "platform(all/windows/linux/darwin/freebsd/posix)", "version",
         "description", "value", "snapshot('true'/'false')", "list of comma separated pack names to add"],
        [True, True, True, False, False, False, False, False, False, False],
        [None, None, None, None, ["all","windows","linux","darwin","freebsd","posix"], None, None, None, ['true', 'false'], None],
        [None, None, None, None, None, None, None, None, "true", None])

    @ns.expect(parser)
    def post(self, query_id):
        args = self.parser.parse_args()
        if args['snapshot']=="true":
            args['snapshot']=True
        else:
            args['snapshot'] = False
        if args['tags']:
            args['tags'] = args['tags'].split(',')
        else:
            args['tags'] = []
        if query_id:
            query = dao.get_query_by_id(query_id)
            if query:
                if validate_osquery_query(args['query']):
                    query = dao.edit_query_by_id(query, args)
                    return marshal(respcls("Successfully fecthed the query info for the given id","success",marshal(query,wrapper.query_wrapper)) , parentwrapper.common_response_wrapper)
                else:
                    message = "Query is not a valid SQL!"
            else:
                message = "Query with this id does not exist"
        else:
            message = "Missing query id"
        return marshal(respcls(message), parentwrapper.failure_response_parent)


@require_api_key
@ns.route('/add', endpoint = "add_query")
@ns.doc(params={'name': 'name of the query', 'query':"query", 'interval':"interval for the query", 'tags':"tags of the query", 'platform':"platform", 'version':"version", 'description':"description", 'value':"value", 'snapshot':"snapshot"})
class AddQuery(Resource):
    '''add queries'''
    parser = requestparse(
        ['name', 'query', 'interval', 'tags', 'platform', 'version', 'description', 'value', 'snapshot', 'packs'],
        [str, str, int, str, str, str, str, str, str, str],
        ["name of the query", "query", "interval of the query", "list of comma separated tags of the query to add", "platform(all/windows/linux/darwin/freebsd/posix)", "version",
         "description", "value", "snapshot('true'/'false')", "list of comma separated pack names to add"],
        [True, True, True, False, False, False, False, False, False, False],
        [None, None, None, None, ["all","windows","linux","darwin","freebsd","posix"], None, None, None, ["true", "false"], None],
        [None, None, None, None, None, None, None, None, "true", None])

    @ns.expect(parser)
    def post(self):
        from polylogyx.dao.v1 import packs_dao
        args = self.parser.parse_args()

        name = args['name']
        sql = args['query']
        interval = args['interval']
        if args['snapshot']=="true":
            args['snapshot']=True
        else:
            args['snapshot']=False

        if args['tags']:
            tags = args['tags'].split(',')
        else:
            tags = args['tags']
        packs = []
        if args['packs']: packs=args['packs'].split(',')
        query = dao.get_query_by_name(name)
        if query:
            message = 'Query with this name already exists'
        elif not validate_osquery_query(sql):
            message = ('Invalid osquery query: "{0}"'.format(args['query']))
        elif not is_number_positive(interval):
            message = 'Interval provided is not valid! Please provide an inverval greater than 0'
        else:
            query = dao.create_query_obj(name, sql, interval, args['platform'], args['version'], args['description'],
                                       args['value'], 100, snapshot=args['snapshot'])
            if tags:
                query.tags = create_tags(*tags)
            if packs:
                packs_list = []
                for pack_name in packs:
                    pack = packs_dao.get_pack_by_name(pack_name)
                    if pack:
                        packs_list.append(pack)
                query.packs = packs_list
            query.save()
            return marshal({'query_id': query.id}, wrapper.add_query_wrapper)
        return marshal(respcls(message), parentwrapper.failure_response_parent)


@require_api_key
@ns.route('/<int:query_id>/tags', endpoint='query_tags_list')
@ns.doc(params={'query_id': 'query id', 'tag': "tag"})
class ListTagsOfQuery(Resource):
    """Resource for tags of a Query"""
    parser = requestparse(['tag'], [str],
                          ["tag to add/remove for the query"], [True])

    @ns.doc(params={'query_id': 'id of the query'})
    def get(self, query_id=None):
        """Lists tags of a Query by its id"""
        status = 'failure'
        if query_id:
            query = dao.get_query_by_id(query_id)
        else:
            query = None
        if not query:
            message = "Query id passed it not correct"
            data = None
        else:
            data = [tag.value for tag in query.tags]
            status = "success"
            message = "Successfully fetched the tags of query"
        return marshal(respcls(message, status, data), parentwrapper.common_response_wrapper, skip_none=True)

    @ns.doc(params={'query_id': 'id of the query'})
    @ns.expect(parser)
    def post(self, query_id=None):
        """Adds tags of a Query by its id"""
        args = self.parser.parse_args()
        status = 'failure'

        if query_id:
            query = dao.get_query_by_id(query_id)
        else:
            query = None
        if query:
            tag = args['tag'].strip()
            if not tag:
                message = "Tag provided is invalid!"
            else:
                tag = tags_dao.create_tag_obj(tag)
                query.tags.append(tag)
                query.save()
                status="success"
                message = "Successfully created tags to query"
        else:
            message = "query id passed it not correct"

        return marshal(respcls(message, status), parentwrapper.common_response_wrapper, skip_none=True)

    @ns.doc(params={'query_id': 'id of the query'})
    @ns.expect(parser)
    def delete(self, query_id=None):
        """Removes tags of a Query by its id"""
        args = self.parser.parse_args()
        status = 'failure'

        if query_id:
            query = dao.get_query_by_id(query_id)
        else:
            query = None
        if query:
            tag = args['tag'].strip()
            tag = tags_dao.get_tag_by_value(tag)
            if tag:
                if dao.is_tag_of_query(query, tag):
                    query.tags.remove(tag)
                    query.save()
                    message = "Successfully removed tags from query"
                    status = "success"
                else:
                    message = "Tag provided is not in query's tag list, Please check tag once again"
            else:
                message = "Tag provided doesn't exists"
        else:
            message = "Query id name passed it not correct"
        return marshal(respcls(message, status), parentwrapper.common_response_wrapper, skip_none=True)


@ns.route('/<string:query_name>/delete', endpoint='query_removed')
@ns.route('/<int:query_id>/delete', endpoint='query_removed_by_id')
class QueryRemoved(Resource):

    @ns.doc(params={'query_id': "id of the query", "query_name": "query name"})
    def delete(self, query_name=None, query_id=None):
        status = "failure"
        message = "Query is not available with this query_name or query_id"
        query = None
        if query_id:
            query = dao.get_query_by_id(query_id)

        if query_name:
            query = dao.get_query_by_name(query_name)

        if query:
            current_app.logger.info("Query {} is requested to delete".format(query.name))
            db.session.delete(query)
            db.session.commit()
            message = "Successfully Removed the query"
            status = "Success"
            return marshal(respcls(message, status), parentwrapper.common_response_wrapper, skip_none=True)
        return marshal(respcls(message, status), parentwrapper.common_response_wrapper, skip_none=True)
