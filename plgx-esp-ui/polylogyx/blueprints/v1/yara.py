import os
from werkzeug import datastructures
from flask_restplus import Namespace, Resource

from polylogyx.blueprints.v1.utils import *
from polylogyx.utils import require_api_key
from polylogyx.wrappers.v1 import parent_wrappers as parentwrapper

ns = Namespace('yara', description='yara related operations')


@require_api_key
@ns.route('', endpoint='list_yara')
@ns.doc(params={})
class ListYara(Resource):
    '''Lists yara files'''
    def get(self):
        from os import walk
        file_list = []
        for (dirpath, dirnames, filenames) in walk(current_app.config['BASE_URL'] + "/yara/"):
            file_list.extend(filenames)
            break
        if "list.txt" in file_list:
            file_list.remove("list.txt")
        return marshal(respcls("Successfully fetched the yara files",'success',file_list),parentwrapper.common_response_wrapper)


@require_api_key
@ns.route('/add', endpoint='add_yara')
@ns.doc(params={'file': 'yara file to upload'})
class AddYara(Resource):
    '''Uploads and adds an yara file to the yara folder'''
    parser = requestparse(['file'], [datastructures.FileStorage], ['Threat file'], [True])

    @ns.expect(parser)
    def post(self):
        import os
        args = self.parser.parse_args()
        if not (args['file'].filename.lower().split('.')[1]=="yara" or args['file'].filename.lower().split('.')[1]=="yar"):
            message = "Please upload only yara(.yara/.yar) files!"
            status = "failure"
        else:
            file_path=current_app.config['BASE_URL'] + "/yara/" + args['file'].filename.lower()
            if os.path.isfile(file_path):
                message = "This file already exists"
                status = "failure"
            else:
                try:
                    args['file'].save(file_path)
                    current_app.logger.info("yara file {} is added".format(args['file'].filename.lower()))
                except FileNotFoundError:
                    os.makedirs(file_path.replace(args['file'].filename.lower(),''))
                    args['file'].save(file_path)
                files = os.listdir(current_app.config['BASE_URL'] + "/yara/")
                with open(current_app.config['BASE_URL'] + "/yara/"+'list.txt', 'w') as the_file:
                    for file_name in files:
                        if file_name!='list.txt':
                            the_file.write(file_name+'\n')
                message = "Successfully uploaded the file"
                status = "success"
        return marshal(respcls(message,status),parentwrapper.common_response_wrapper,skip_none=True)


@require_api_key
@ns.route('/view', endpoint='view_yara')
@ns.doc(params={'file_name':"name of the yara file to view the content for"})
class ViewYara(Resource):
    '''Returns yara file'''
    parser = requestparse(['file_name'], [str], ['name of the yara file to view the content for'], [True])

    @ns.expect(parser)
    def post(self):
        args = self.parser.parse_args()
        status = "failure"
        message = None
        data = None
        try:
            file_path = current_app.config['BASE_URL'] + "/yara/" + args['file_name'].lower()
            if os.path.exists(file_path):
                with open(file_path, 'r') as the_file:
                    data = the_file.read()
                status = "success"
                message = "Successfully fetched the yara file content!"
        except Exception as e:
            message = str(e)
        return marshal(respcls(message, status, data), parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/delete', endpoint='delete_yara')
@ns.doc(params={'file_name':"name of the yara file to delete"})
class DeleteYara(Resource):
    '''Deletes yara file from the yara base path'''
    parser = requestparse(['file_name'], [str], ['name of the yara file to delete'], [True])

    @ns.expect(parser)
    def post(self):
        args = self.parser.parse_args()
        try:
            current_app.logger.info("yara file {} is requested to delete".format(args['file_name']))
            os.remove(current_app.config['BASE_URL'] + "/yara/"+args['file_name'])
            return marshal(respcls("File with the given file name is deleted successfully", "success"),
                           parentwrapper.common_response_wrapper, skip_none=True)
        except Exception:
            return marshal(respcls("File with the given file name doesnot exists", "failure"), parentwrapper.common_response_wrapper, skip_none=True)
