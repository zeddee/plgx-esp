from flask_restplus import Namespace, Resource

from polylogyx.wrappers.v1 import parent_wrappers as parentwrapper
from polylogyx.utils import require_api_key
from polylogyx.constants import PolyLogyxServerDefaults
from polylogyx.blueprints.v1.utils import *


ns = Namespace('schema', description='schema related operations')


@require_api_key
@ns.route('', endpoint = "get_schema")
@ns.doc(params = {})
class GetSchema(Resource):
    '''Returns the response of schema'''
    parser = requestparse(['export_type'], [str], ['export_type(json/sql schema)'], [False], [['sql', 'json']], ['sql'])

    @ns.expect(parser)
    def get(self):
        from polylogyx.dao.v1.common_dao import get_osquery_agent_schema
        args = self.parser.parse_args()
        if args['export_type'] == 'sql':
            schema = PolyLogyxServerDefaults.POLYLOGYX_OSQUERY_SCHEMA_JSON
        elif args['export_type'] == 'json':
            schema = [table.to_dict() for table in get_osquery_agent_schema()]
        message = "PolyLogyx agent schema is fetched successfully"
        status = "success"
        return marshal(respcls(message, status, schema), parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/<string:table>', endpoint = "get_table_schema")
@ns.doc(params = {'table':"table"})
class GetTableSchema(Resource):
    '''Returns the response of schema of the table given'''

    def get(self, table):
        schema_json = PolyLogyxServerDefaults.POLYLOGYX_OSQUERY_SCHEMA_JSON
        if table:
            try:
                table_schema = schema_json[table]
                return marshal(respcls('Successfully fetched the table schema',"success",table_schema), parentwrapper.common_response_wrapper,skip_none=True)
            except:
                message = 'Table with this name does not exist'
        else:
            message = "Please provide a table name"
        return marshal(respcls(message,"failure"), parentwrapper.failure_response_parent)

