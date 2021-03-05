from flask_restplus import Namespace, Resource, inputs

from polylogyx.blueprints.v1.utils import *
from polylogyx.utils import require_api_key
from polylogyx.dao.v1 import tags_dao as dao
from polylogyx.wrappers.v1 import tag_wrappers as wrapper, parent_wrappers as parentwrapper, query_wrappers

ns = Namespace('tags', description='tags related operations')


@require_api_key
@ns.route('', endpoint = "list_tags")
@ns.doc(params = {})
class TagsList(Resource):
    '''List all tags of the Nodes'''
    parser = requestparse(['start', 'limit', 'searchterm'], [inputs.natural, inputs.natural, str], ['start', 'limit', "search term"], [False, False, False], [None, None, None], [None, None, ""])

    @ns.expect(parser)
    def get(self):
        args = self.parser.parse_args()
        base_qs = dao.get_all_tags(args['searchterm'])
        total_count = dao.get_tags_total_count()
        list_dict_data = [{'value':tag.value,'nodes':[node.host_identifier for node in tag.nodes if node.state!=node.REMOVED and node.state!=node.DELETED],'packs':[pack.name for pack in tag.packs],'queries':[query.name for query in tag.queries],'file_paths':tag.file_paths} for tag in base_qs.offset(args['start']).limit(args['limit']).all()]
        data = marshal(list_dict_data,wrapper.tag_wrapper)
        return marshal(respcls("Successfully fetched the tags info", "success", {'count':base_qs.count(), 'total_count':total_count, 'results':data}), parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/add', endpoint = "add_tags")
@ns.doc(params={'tag': "tag to add"})
class AddTag(Resource):
    '''Adds a new tag to the Tag model'''

    parser = requestparse(['tag'], [str], ["tag to add"], [True])

    @ns.expect(parser)
    def post(self):
        status = "failure"
        tag = self.parser.parse_args()['tag'].strip()
        if not tag:
            message = "Tag provided is invalid!"
        elif dao.get_tag_by_value(tag):
            message = "Tag is already present!"
        else:
            tag = dao.create_tag_obj(tag)
            message = "Tag added successfully"
            status = "success"
        return marshal(respcls(message,status), parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/delete', endpoint = "delete_tags")
@ns.doc(params={'tag': "tag to delete"})
class AddTag(Resource):
    '''Deletes a tag from the Tag model'''

    parser = requestparse(['tag'], [str], ["tag to delete"], [True])

    @ns.expect(parser)
    def post(self):
        args = self.parser.parse_args()
        tag = args['tag']
        message = "Tag is deleted successfully"
        status = "success"
        try:
            tag = dao.get_tag_by_value(tag)
            if tag:
                current_app.logger.info("Tag {} is requested to delete".format(tag.value))
                dao.delete_tag(tag)
            else:
                message = "Tag doesnot exists!"
        except Exception as e:
            message = str(e)
            status = "failure"
        return marshal(respcls(message,status), parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/tagged', endpoint='objects_tagged')
class TaggedList(Resource):
    """List Nodes, Queries, Packs Details of a Tag"""
    parser = requestparse(['tags'], [str], ["tags names separated by a comma"], [True])

    @ns.expect(parser)
    def post(self):
        from polylogyx.dao.v1 import queries_dao, hosts_dao, packs_dao
        from polylogyx.wrappers.v1 import pack_wrappers
        args = self.parser.parse_args()
        tag_names = args['tags'].split(',')
        tags = dao.get_tags_by_names(tag_names)
        if tags:
            hosts = [node.get_dict() for node in hosts_dao.get_tagged_nodes(tag_names) if node.state != node.DELETED and node.state != node.REMOVED]

            packs_queryset = packs_dao.get_tagged_packs(tag_names)
            packs = marshal(packs_queryset, pack_wrappers.pack_wrapper)
            for index in range(len(packs)):
                packs[index]['tags'] = [tag.to_dict() for tag in packs_queryset[index].tags]
                packs[index]['queries'] = marshal(packs_queryset[index].queries, query_wrappers.query_wrapper)
                for query_index in range(len(packs_queryset[index].queries)):
                    packs[index]['queries'][query_index]['tags'] = [tag.to_dict() for tag in
                                                                   packs_queryset[index].queries[query_index].tags]
                    packs[index]['queries'][query_index]['packs'] = [pack.name for pack in
                                                                    packs_queryset[index].queries[query_index].packs]

            queries_qs = queries_dao.get_tagged_queries(tag_names)
            queries = marshal(queries_qs, query_wrappers.query_wrapper)
            for i in range(len(queries)):
                queries[i]['tags'] = [tag.to_dict() for tag in queries_qs[i].tags]
                queries[i]['packs'] = [pack.name for pack in queries_qs[i].packs]

            message = "All hosts, queries, packs for the tag provided!"
            status = "success"
            return marshal(respcls(message, status, {"hosts":hosts, "packs":packs, "queries":queries}), parentwrapper.common_response_wrapper, skip_none=True)
        else:
            return marshal(respcls("Tag(s) doesn't exists for the value(s) provided", "failure"),
                           parentwrapper.common_response_wrapper, skip_none=True)