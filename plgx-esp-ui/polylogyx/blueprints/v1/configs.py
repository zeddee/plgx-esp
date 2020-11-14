from flask_restplus import Namespace, Resource

from polylogyx.blueprints.v1.utils import *
from polylogyx.dao.v1 import hosts_dao, configs_dao as dao
from polylogyx.wrappers.v1 import parent_wrappers as parentwrapper

ns = Namespace('configs', description='Configurations resources blueprint')


@ns.route('/all', endpoint='list_configs')
@ns.doc(params={})
class ConfigList(Resource):
    '''Lists out all configs'''

    def get(self):
        data = dao.get_all_configs()
        message = "Successfully fetched the config data"
        status = "success"
        if not data:
            data = {}
        return marshal(respcls(message, status, data), parentwrapper.common_response_wrapper)


@ns.route('/view', endpoint='list_config_by_platform')
@ns.doc(params={'platform': 'one of ["windows", "linux", "darwin"]','arch':'arch of platform whether x86 or x86_64'})
class GetConfigByPlatformOrNode(Resource):
    '''Lists the config by its Platform or host_identifier'''

    parser = requestparse(['platform', 'arch', 'host_identifier'], [str, str, str],
                          ["platform name(linux/windows/darwin)", "arch of platform(x86/x86_64)", "host identifer of the node to get config for"], [False, False, False], [["linux", "windows", "darwin"],["x86","x86_64"], None])

    @ns.expect(parser)
    def post(self):
        status = "failure"
        config = {}
        args = self.parser.parse_args()
        if args['host_identifier']:
            node = hosts_dao.get_node_by_host_identifier(args['host_identifier'])
            if node:
                config = node.get_config()
                message = "Successfully fetched the config through host identifier passed"
            else:
                message = "Host identifier passed is not valid!"
        else:
            config = dao.get_config(args['platform'], args['arch'])
            if config:
                config = dao.get_config_by_platform(config)
                status = "success"
                message = "Config is fetched successfully for the platform given"
            else:
                message = "Requested config is not present for the platform, arch, type given!"
        if config:
            status="success"
        return marshal(respcls(message, status, config), parentwrapper.common_response_wrapper, skip_none=True)


@ns.route('/update', endpoint='update_config_by_platform')
@ns.doc(params={'platform': 'one of ["windows", "linux", "darwin"]', 'filters': 'filters to define for the specific platform', 'queries': 'queries to define for the specific platform', 'arch':'arch of platform whether x86 or x86_64'})
class EditConfigByPlatform(Resource):
    '''Lists or edits the config by its Platform'''

    parser = requestparse(['filters', 'queries', 'arch', 'platform', 'type'], [dict, dict, str, str, str],
                          ["filters to define for the specific platform", "queries to define for the specific platform", "arch of platform(x86/x86_64)", "platform name(windows/linux/darwin)", "type of the config(default/shallow/config)"], [True, True, False, True, False],[None,None,["x86","x86_64"],["linux", "windows", "darwin"], ["default", "shallow", "deep"]],[None, None, "x86_64", None, "default"])

    @ns.doc(body=parser)
    @ns.expect(parser)
    def post(self):
        '''Modifies and returns the API response if there is any existed data for the passed platform'''
        args = self.parser.parse_args()
        status = "failure"
        platform = args['platform']
        arch = args['arch']
        type = args['type']
        if platform=="windows" and arch=="x86_64" and type=="default":
            type="shallow"
        type_mapping = {'default':0, 'shallow': 1, 'deep': 2}
        config = dao.get_config(platform, arch, type_mapping[type])
        queries = args['queries']
        filters = args['filters']
        if config:
            for query in queries:
                if 'status' not in queries[query] or 'interval' not in queries[query]:
                    abort(400, "Please provide both interval and status for all queries!")

            config_data = dao.edit_config_by_platform(config, filters, queries)
            current_app.logger.info("Config is updated for {0} platform {1} arch {2} type".format(platform, arch, type_mapping[type]))
            status = "success"
            message = "Config is updated successfully for the platform given"
        else:
            config_data = None
            message = "Requested config is not present for the platform, arch, type given!"
        return marshal(respcls(message, status, config_data), parentwrapper.common_response_wrapper, skip_none=True)


@ns.route('/toggle', endpoint='toggle_config')
class ToggleConfigByPlatform(Resource):
    parser = requestparse(['platform', 'arch', 'type'], [str, str, str],
                              ["platform", "arch of platform(x86/x86_64)", "type of the config(default/shallow/config)"], [True, True, True],
                              [["windows", "linux", "darwin"], ["x86", "x86_64"], ["default", "shallow", "deep"]], [None, "x86_64", "default"])

    @ns.expect(parser)
    def put(self):
        args = self.parser.parse_args()
        arch = args['arch']
        type = args['type']
        platform = args['platform']

        if platform == "windows" and arch == "x86_64" and type == "default":
            type = "shallow"
        type_mapping = {'default': 0, 'shallow': 1, 'deep': 2}
        config = dao.make_default_config(platform, arch, type_mapping[type])
        current_app.logger.info(
            "Config is toggled for {0} platform {1} arch to {2} type".format(platform, arch, type_mapping[type]))
        status = "success"
        message = "Default config for the platform and arch given is changed successfully"
        return marshal(respcls(message, status), parentwrapper.common_response_wrapper, skip_none=True)

