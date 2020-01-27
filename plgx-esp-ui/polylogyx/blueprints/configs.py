import datetime as dt
import json

from flask import jsonify, request
from flask_restplus import Namespace, Resource, marshal

from .utils import *
from polylogyx.utils import require_api_key
from polylogyx.dao import configs_dao as dao
from polylogyx.wrappers import parent_wrappers as parentwrapper
from polylogyx.models import DefaultQuery

ns = Namespace('configs', description='Configurations related operations')

@require_api_key
@ns.route('/', endpoint='list_configs')
@ns.doc(params={})
class ConfigList(Resource):
    '''List of all configs'''

    def get(self):
        '''returns the response of the API with list of all configs'''
        data = dao.get_all_configs()
        if not data: message = "configs data doesn't exists to show"
        return marshal(respcls("Successfully fetched the configs", 'success', data), parentwrapper.common_response_wrapper)


@require_api_key
@ns.route('/<string:platform>', endpoint='list_config_by_platform')
@ns.doc(params={'platform': 'one of ["windows", "linux", "darwin"]', 'filters': 'filters to define for the specific platform', 'queries': 'queries to define for the specific platform', 'arch':'arch of platform whether x86 or x86_64'})
class GetOrEditConfigByPlatform(Resource):
    '''Lists or edits the config by its Platform'''

    parser = requestparse(['filters', 'queries', 'arch'], [dict, dict, str],
                          ["filters to define for the specific platform", "queries to define for the specific platform", "arch of platform"], [True, True, False])

    def get(self, platform):
        status = "failure"
        if platform:
            config = dao.get_config_by_platform(platform)
            if config:
                return marshal(respcls("Successfully fetched the config through its platform name", 'success', config), parentwrapper.common_response_wrapper)
            else:
                message = "Config for this platform does not exist"
        else:
            message = "Missing platform name"
        return marshal(respcls(message, status), parentwrapper.failure_response_parent)

    @ns.expect(parser)
    def post(self, platform):
        '''modifies and returns the API response if there is any existed data for the passed platform'''
        args = self.parser.parse_args()
        status = "failure"
        config = None
        if platform:
            config = dao.get_config_by_platform(platform)
            arch = args['arch']
            if not arch:
                arch = DefaultQuery.ARCH_x64
            if config:
                try:
                    config = dao.edit_config_by_platform(platform, args['filters'], args['queries'], arch)
                    status = "success"
                    message = "Config is edited successfully for the platform given"
                except Exception as e:
                    message = 'Please check the payload and try again with correct payload'
            else:
                message = "Config for this platform name doesn't exists!"
        else:
            message = "Missing platform name"
        if not status=="success": config=None
        return marshal(respcls(message, status, config), parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/add', endpoint='add_config')
@ns.doc(params={'filters': 'filters to add to config', 'queries': 'queries to add to config', 'platform': 'platform name', 'arch':'arch of platform'})
class AddConfig(Resource):
    '''adds a new config to a specific platform'''
    parser = requestparse(['filters', 'queries', 'platform', 'arch'], [dict, dict, str, str],
                          ["filters to define for the specific platform",
                           "queries to define for the specific platform", 'platform name', 'platform arch'], [True, True, True, False])

    @ns.expect(parser)
    def post(self):
        '''adds a new config and returns the api response'''
        args = self.parser.parse_args()
        platform = args['platform']
        status = "failure"
        config = None
        if platform:
            config = dao.get_config_by_platform(platform)
            arch = args['arch']
            if not arch:
                arch = DefaultQuery.ARCH_x64
            if config:
                message = "Config for this platform name already exists!"
            else:
                try:
                    config = dao.add_config_by_platform(platform, args['filters'], args['queries'], arch)
                    status = "success"
                    message = "Config is added for this platform name given"
                except Exception as e:
                    message = 'Please check the payload and try again with correct payload'
        else:
            message = "Missing platform name"
        if not status=="success": config=None
        return marshal(respcls(message, status, config), parentwrapper.common_response_wrapper, skip_none=True)
