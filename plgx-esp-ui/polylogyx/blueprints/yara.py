import os
from werkzeug import datastructures

from flask_restplus import Namespace, Resource, marshal

from .utils import *
from polylogyx.utils import require_api_key
from polylogyx.wrappers import parent_wrappers as parentwrapper
from polylogyx.constants import PolyLogyxServerDefaults


ns = Namespace('yara', description='yara related operations')
YARA_URL = PolyLogyxServerDefaults.BASE_URL + "/yara/"

@require_api_key
@ns.route('/', endpoint='list_yara')
@ns.doc(params={})
class ListYara(Resource):
    '''lists yara files'''
    def get(self):
        from os import walk
        file_list = []
        for (dirpath, dirnames, filenames) in walk(YARA_URL):
            file_list.extend(filenames)
            break
        if "list.txt" in file_list:
            file_list.remove("list.txt")
        return marshal(respcls("Successfully fetched the yara files",'success',file_list),parentwrapper.common_response_wrapper)


@require_api_key
@ns.route('/add', endpoint='add_yara')
@ns.doc(params={'file': 'yara file to upload'})
class AddYara(Resource):
    '''uploads and adds an yara file to the yara folder'''
    parser = requestparse(['file'], [datastructures.FileStorage], ['Threat file'], [True])

    @ns.expect(parser)
    def post(self):
        import os
        args = self.parser.parse_args()
        file_path=YARA_URL + args['file'].filename.lower()
        if os.path.isfile(file_path):
            message = "This file already exists"
            status = "failure"
        else:
            try:
                args['file'].save(file_path)
            except FileNotFoundError:
                os.makedirs(file_path.replace(args['file'].filename.lower(),''))
                args['file'].save(file_path)
            files = os.listdir(YARA_URL)
            with open(YARA_URL+'list.txt', 'w') as the_file:
                for file_name in files:
                    if file_name!='list.txt':
                        the_file.write(file_name+'\n')
            message = "Successfully uploaded the file"
            status = "success"
        return marshal(respcls(message,status),parentwrapper.common_response_wrapper,skip_none=True)