from flask_restplus import Namespace, Resource
from json import JSONDecodeError

from polylogyx.blueprints.v1.utils import *
from polylogyx.utils import require_api_key
from polylogyx.dao.v1 import packs_dao as dao, tags_dao
from polylogyx.wrappers.v1 import pack_wrappers as wrapper, parent_wrappers as parentwrapper

ns = Namespace('packs', description='packs related operations')


@require_api_key
@ns.route('', endpoint = 'list_packs')
@ns.doc(params={})
class PacksList(Resource):
    '''List all packs of the Nodes'''
    parser = requestparse(['start', 'limit', 'searchterm'],
                          [int, int, str],
                          ['start', 'limit', 'searchterm'],
                          [False, False, False], [None, None, None], [None, None, ''])

    @ns.expect(parser)
    @ns.marshal_with(parentwrapper.common_response_wrapper)
    def post(self):
        args = self.parser.parse_args()
        queryset=dao.get_all_packs(args['searchterm']).offset(args['start']).limit(args['limit']).all()
        data = marshal(queryset, wrapper.pack_wrapper)
        for index in range(len(data)):
            data[index]['tags'] = [tag.to_dict() for tag in queryset[index].tags]
            data[index]['queries'] = marshal(queryset[index].queries, wrapper.query_wrapper)
            for query_index in range(len(queryset[index].queries)):
                data[index]['queries'][query_index]['tags'] = [tag.to_dict() for tag in queryset[index].queries[query_index].tags]
                data[index]['queries'][query_index]['packs'] = [pack.name for pack in queryset[index].queries[query_index].packs]
        message = "Successfully fetched the packs info"
        status = "success"
        if not data:
            data=[]
        data = {'count':dao.get_all_packs(args['searchterm']).count(), 'total_count':dao.get_total_count(), 'results':data}
        return respcls(message,status,data)


@require_api_key
@ns.route('/<int:pack_id>', endpoint = 'pack_by_id')
@ns.doc(params={'pack_id': 'id of the pack'})
class PackById(Resource):
    '''List all packs of the Nodes'''

    def get(self, pack_id):
        if pack_id:
            pack_qs = dao.get_pack_by_id(pack_id)
            if pack_qs:
                pack = marshal(pack_qs, wrapper.pack_wrapper)
                pack['tags'] = [tag.to_dict() for tag in pack_qs.tags]
                pack['queries'] = [query.name for query in pack_qs.queries]
                return marshal(respcls("successfully fetched the packs info","success",pack),parentwrapper.common_response_wrapper)
            else:
                message = "Pack info with this pack id does not exist"
        else:
            message = "Missing pack id"
        return marshal(respcls(message), parentwrapper.failure_response_parent)


@require_api_key
@ns.route('/add', endpoint = 'pack_add')
@ns.doc(params={'tags': 'list of tags', 'name':'name of the pack', 'queries':'list of queries', 'category':'category name', 'platform':"platform", 'version':"version", 'description':"description", 'shard':"shard"})
class AddPack(Resource):
    '''Adds a new pack to the Pack model'''

    parser = requestparse(['tags','name','queries','category','platform','version','description','shard'],[str, str, dict, str, str, str, str, int],['list of comma separated tags', 'name of the pack', 'dict of queries', 'category', 'platform(windows/linux/darwin)', 'version', 'description', 'shard'],[False, True, True, False, False, False, False, False],
                          [None, None, None, ["Intrusion Detection","Monitoring","Compliance and Management","Forensics and Incident Response","General","Others"], ["windows", "linux", "darwin"], None, None, None])

    @ns.expect(parser)
    def post(self):
        args = self.parser.parse_args()
        pack = add_pack_through_json_data(args)
        return marshal({'pack_id': pack.id}, wrapper.response_add_pack)


@require_api_key
@ns.route('/<string:pack_name>/tags', endpoint='pack_tags_list')
@ns.route('/<int:pack_id>/tags', endpoint='pack_tags_list_by_pack_id')
@ns.doc(params={'pack_name': 'pack name', 'pack_id': 'id of the pack'})
class ListOrEditsTagsOfPack(Resource):
    """Resource for tags of a Pack"""
    parser = requestparse(['tag'], [str],
                          ["tag to add/remove for the pack"], [True])

    @ns.doc(params={'pack_name': 'pack name', 'pack_id': 'id of the pack'})
    def get(self, pack_name=None, pack_id=None):
        """Lists tags of a Pack by its id or name"""
        status = 'failure'
        if pack_name:
            pack = dao.get_pack_by_name(pack_name)
        elif pack_id:
            pack = dao.get_pack_by_id(pack_id)
        else:
            pack = None
        if not pack:
            message = "Pack id or pack name passed it not correct"
            data = None
        else:
            data = [tag.value for tag in pack.tags]
            status = "success"
            message = "Successfully fetched the tags of pack"
        return marshal(respcls(message, status, data), parentwrapper.common_response_wrapper, skip_none=True)

    @ns.doc(params={'pack_name': 'pack name', 'pack_id': 'id of the pack', 'tag': 'tag'})
    @ns.expect(parser)
    def post(self, pack_name=None, pack_id=None):
        """Creates tags of a Pack by its id"""
        args = self.parser.parse_args()
        status = 'failure'

        if pack_name:
            pack = dao.get_pack_by_name(pack_name)
        elif pack_id:
            pack = dao.get_pack_by_id(pack_id)
        else:
            pack = None
        if pack:
            tag = args['tag'].strip()
            if not tag:
                message = "Tag provided is invalid!"
            else:
                tag = tags_dao.create_tag_obj(tag)
                pack.tags.append(tag)
                pack.save()
                status="success"
                message = "Successfully created tags to pack"
        else:
            message = "Pack id or pack name passed it not correct"

        return marshal(respcls(message, status), parentwrapper.common_response_wrapper, skip_none=True)

    @ns.doc(params={'pack_name': 'pack name', 'pack_id': 'id of the pack', 'tag': 'tag'})
    @ns.expect(parser)
    def delete(self, pack_name=None, pack_id=None):
        """Remove tags of a Pack by its id"""
        args = self.parser.parse_args()
        status = 'failure'

        if pack_name:
            pack = dao.get_pack_by_name(pack_name)
        elif pack_id:
            pack = dao.get_pack_by_id(pack_id)
        else:
            pack = None
        if pack:
            tag = args['tag'].strip()
            tag = tags_dao.get_tag_by_value(tag)
            if tag:
                if dao.is_tag_of_pack(pack, tag):
                    pack.tags.remove(tag)
                    pack.save()
                    message = "Successfully removed tags from pack"
                    status = "success"
                else:
                    message = "Tag provided is not in pack's tag list, Please check tag once again"
            else:
                message = "Tag provided doesn't exists"
        else:
            message = "Pack id or pack name passed it not correct"
        return marshal(respcls(message, status), parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/upload', endpoint="packs_upload")
@ns.doc(params = {})
class UploadPack(Resource):
    '''Packs will be added through the uploaded file'''

    from werkzeug import datastructures
    parser = requestparse(['file', 'category'],[datastructures.FileStorage, str],['packs file', 'pack category'],[True,False],[None,["Intrusion Detection","Monitoring","Compliance and Management","Forensics and Incident Response","General","Others"],[None, "General"]])

    @ns.expect(parser)
    def post(self):
        args = self.parser.parse_args()
        try:
            args_dict = json.loads(args['file'].read())
        except Exception:
            message = "Please upload only readable(.json/.conf) formatted files!"
            status = "failure"
            return marshal(respcls(message, status, None), parentwrapper.common_response_wrapper, skip_none=True)
        args_dict['name'] = args['file'].filename.lower().split('.')[0]
        if not 'category' in args_dict:
            args_dict['category'] = args['category']
        try:
            pack = add_pack_through_json_data(args_dict)
            return marshal({'pack_id': pack.id}, wrapper.response_add_pack)
        except JSONDecodeError:
            message = "Json uploaded is invalid!"
            status = "failure"
            pack_id = None
        except KeyError:
            message = "Queries and name are compulsory!"
            status = "failure"
            pack_id = None
        return marshal(respcls(message, status, pack_id),parentwrapper.common_response_wrapper, skip_none=True)


@ns.route('/<string:pack_name>/delete', endpoint='pack_removed')
@ns.route('/<int:pack_id>/delete', endpoint='pack_removed_by_id')
class PackRemoved(Resource):

    @ns.doc(params={'pack_id': "id of the pack", 'pack_name': "pack name"})
    def delete(self, pack_name=None, pack_id=None):
        status = "failure"
        message = "Pack is not available with this pack name or pack id"
        pack = None
        if pack_id:
            pack = dao.get_pack_by_id(pack_id)

        if pack_name:
            pack = dao.get_pack_by_name(pack_name)

        if pack:
            current_app.logger.info("Pack {} is requested to delete".format(pack.name))
            pack_tags = pack.tags
            db.session.delete(pack)
            db.session.commit()
            message = "Successfully removed the Pack"
            status = "Success"
            return marshal(respcls(message, status), parentwrapper.common_response_wrapper, skip_none=True)
        return marshal(respcls(message, status), parentwrapper.common_response_wrapper, skip_none=True)
