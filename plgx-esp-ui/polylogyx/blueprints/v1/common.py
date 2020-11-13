from flask_restplus import Namespace, Resource

from polylogyx.dao.v1 import common_dao as dao
from polylogyx.blueprints.v1.utils import *
from polylogyx.utils import require_api_key
from polylogyx.constants import PolyLogyxServerDefaults
from polylogyx.wrappers.v1 import parent_wrappers as parentwrapper

ns = Namespace('common_api', description='all general purpose apis operations', path = '/')


@require_api_key
@ns.doc(params={'file':"hunt file", 'type':"(md5/sha256)", 'host_identifier':"host id of the node", 'query_name':"query name to hunt for", 'start':"start value for pagination", 'limit':"end value for pagination"})
@ns.route('/hunt-upload', endpoint="hunt_file_upload")
class HuntFileUpload(Resource):
    '''Hunting through the file uploaded'''

    from werkzeug import datastructures
    parser = requestparse(['file', 'type', 'host_identifier', "query_name", "start", "limit"],
                          [datastructures.FileStorage, str, str, str, int, int],

                          ['Threat file', 'type of hunt (md5/sha256/domain name)', 'host_identifier of the node', "query_name", "start", "limit"],
                          [True, True, False, False, False, False],
                          [None, PolyLogyxServerDefaults.search_supporting_columns, None, None, None, None],
                          [None, None, None, None, 0, 100])

    @ns.expect(parser)
    def post(self):
        args = self.parser.parse_args()
        data = None
        message = None
        status = "failure"
        lines = None

        type = args['type']
        file = args['file']
        query_name = args['query_name']
        host_identifier = args['host_identifier']
        start = args['start']
        limit = args['limit']

        try:
            lines = [line.decode('utf-8').replace('\n', '').replace('\r', '') for line in file.readlines()]
        except Exception as e:
            message = "We are unable to read this file with this format!"
        if lines is not None:
            results = hunt_through_indicators(lines, type, host_identifier, query_name, start, limit)
        else:
            results = [message, status, data]
        return marshal(respcls(results[0], results[1], results[2]), parentwrapper.common_response_wrapper, skip_none=True)


def hunt_through_indicators(lines, type, host_identifier, query_name, start, limit):
    # method to hunt recent activity through indicators
    status = "failure"
    data = None
    if not host_identifier:
        output_list_data = []
        hunt_search_results = dao.result_log_query_count(lines, type)
        for search_result in hunt_search_results:
            data_dict = node_dao.get_host_id_and_name_by_node_id(search_result[0])
            query_count_pair = {"query_name": search_result[1], "count": search_result[2]}
            is_matched = False
            for host_result_log_item in output_list_data:
                if data_dict['host_identifier'] == host_result_log_item['host_identifier']:
                    is_matched = True
                    if 'queries' in host_result_log_item:
                        host_result_log_item['queries'].append(query_count_pair)
                    else:
                        host_result_log_item['queries'] = []
            if not is_matched:
                data_dict['queries'] = [query_count_pair]
                output_list_data.append(data_dict)

        message = "Successfully fetched the results through the hunt"
        status = "success"
        data = output_list_data
        if not output_list_data:
            data = []

    else:
        nodes = get_nodes_for_host_id(host_identifier)
        if not nodes:
            message = "Please provide correct host identifier!"
        elif not query_name:
            message = "Please provide the query name!"
        else:
            try:
                qs = dao.result_log_query(lines, type, [node.id for node in nodes], query_name, start, limit)
                results = qs['results']
                results = [result[2] for result in results]
                count = qs['count']
                data = {'count': count, 'results': results}
                message = "Successfully fetched the results through the hunt"
                status = "success"
            except Exception as e:
                data = None
                message = str(e)
    return [message, status, data]


@require_api_key
@ns.doc(params={'indicators': "list of comma separated indicators", 'type': "(md5/sha256)",
                'host_identifier': "host id of the node", 'query_name': "query name to hunt for",
                'start': "start value for pagination", 'limit': "end value for pagination"})
@ns.route('/indicators/hunt', endpoint="hunt_indicators")
class IndicatorHunt(Resource):
    """ Hunting through the indicators given """

    parser = requestparse(['indicators', 'type', 'host_identifier', "query_name", "start", "limit"],
                          [str, str, str, str, int, int],
                          ['Hashed Threat indicators', 'type of threat (md5/sha256)', 'host_identifier of the node', "query_name", "start", "limit"],
                          [True, True, False, False, False, False],
                          [None, PolyLogyxServerDefaults.search_supporting_columns, None, None, None, None],
                          [None, None, None, None, 0, 100])

    @ns.expect(parser)
    def post(self):
        args = self.parser.parse_args()
        data = None
        message = None
        status = "failure"

        type = args['type']
        indicators = args['indicators'].split(',')
        query_name = args['query_name']
        host_identifier = args['host_identifier']
        start = args['start']
        limit = args['limit']

        results = hunt_through_indicators(indicators, type, host_identifier, query_name, start, limit)

        return marshal(respcls(results[0], results[1], results[2]), parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.doc(params={'file':"hunt file", 'type':"(md5/sha256)", 'host_identifier':"host id of the node", 'query_name': "query name to hunt for"})
@ns.route('/hunt-upload/export', endpoint="export_hunt_file_upload")
class ExportHuntFileUpload(Resource):
    '''Export Hunt results through the file uploaded'''

    from werkzeug import datastructures
    parser = requestparse(['file', 'type', 'host_identifier', "query_name"],
                          [datastructures.FileStorage, str, str, str],
                          ['Threat file', 'type of hunt (md5/sha256/domain name)', 'host_identifier of the node', "query_name"],
                          [True, True, True, True],
                          [None, PolyLogyxServerDefaults.search_supporting_columns, None, None],
                          [None, None, None, None])

    @ns.expect(parser)
    def post(self):
        args = self.parser.parse_args()
        data = None
        message = None
        status = "failure"
        lines = None

        type = args['type']
        file = args['file']
        query_name = args['query_name']
        host_identifier = args['host_identifier']
        nodes = get_nodes_for_host_id(host_identifier)

        try:
            lines = [line.decode('utf-8').replace('\n', '').replace('\r', '') for line in file.readlines()]
        except Exception as e:
            message = "We are unable to read this file with this format!"
        if lines is not None:
            if nodes:
                try:
                    results = dao.result_log_query_for_export(lines, type, [node.id for node in nodes], query_name)
                    results = [r for r, in results]
                    headers = []
                    if not len(results) == 0:
                        firstRecord = results[0]
                        for key in firstRecord.keys():
                            headers.append(key)

                    bio = BytesIO()
                    writer = csv.writer(bio)
                    writer.writerow(headers)

                    for data in results:
                        row = []
                        row.extend([data.get(column, '') for column in headers])
                        writer.writerow(row)

                    bio.seek(0)

                    file_data = send_file(
                      bio,
                      mimetype='text/csv',
                      as_attachment=True,
                      attachment_filename='hunt_query_results.csv'
                    )
                    return file_data
                except Exception as e:
                    data = []
                    message = str(e)

            else:
                message = "Host identifier given is wrong!"

        return marshal(respcls(message, status, data), parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/search', endpoint="search")
@ns.doc(params={'conditions':"conditions to filter activity", 'host_identifier':"host id of the node", 'query_name':"query name to hunt for", 'start':"start value for pagination", 'limit':"end value for pagination"})
class Search(Resource):
    ''' Searches in result log table for the payload given '''

    parser = requestparse(['conditions', 'host_identifier', 'query_name', 'start', 'limit'],
                          [dict, str, str, int, int],
                          ["conditions to search for", 'host_identifier of the node', 'query name', 'start', 'limit'],
                          [True, False, False, False, False])

    @ns.expect(parser)
    def post(self):
        from polylogyx.blueprints.utils import SearchParser as SearchConditionsParser
        args = self.parser.parse_args()
        host_identifier = args['host_identifier']
        query_name = args['query_name']
        start = args['start']
        limit = args['limit']
        conditions = args['conditions']
        if not start:
            start = 0
        if not limit:
            limit = 100

        data = None
        message = None
        status = "failure"
        try:
            search_rules = SearchConditionsParser()
            root = search_rules.parse_group(conditions)
        except Exception as e:
            message = str(e)
            return marshal(respcls(message, status),
                           parentwrapper.common_response_wrapper, skip_none=True)

        try:
            filter = root.run('', [], 'result_log')
        except Exception:
            return marshal(respcls("Conditions passed are not correct! Please check once and try again!", status),
                           parentwrapper.common_response_wrapper, skip_none=True)
        output_dict_data = {}

        if not host_identifier:
            search_results = dao.result_log_search_results_count(filter)
            output_list_data = []
            for search_result in search_results:
                data_dict = node_dao.get_host_id_and_name_by_node_id(search_result[0])
                query_count_pair = {"query_name": search_result[1], "count": search_result[2]}
                is_matched = False
                for host_result_log_item in output_list_data:
                    if data_dict['host_identifier'] == host_result_log_item['host_identifier']:
                        is_matched = True
                        if 'queries' in host_result_log_item:
                            host_result_log_item['queries'].append(query_count_pair)
                        else:
                            host_result_log_item['queries'] = []
                if not is_matched:
                    data_dict['queries'] = [query_count_pair]
                    output_list_data.append(data_dict)

            message = "Successfully fetched the data through the payload given"
            status = "success"
            data = output_list_data
            if not data:
                data={}

        else:
            if not query_name:
                message = "Please provide the query name"
            else:
                qs = dao.result_log_search_results(filter, [node.id for node in get_nodes_for_host_id(host_identifier)], query_name, start, limit)
                data = {'count':qs['count'], 'results':[data_elem[0] for data_elem in qs['results']]}
                message = "Successfully fetched the data through the payload given"
                status = "success"

        return marshal(respcls(message, status, data), parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/indicators/upload', endpoint="indicators_file_upload")
class IndicatorsUpload(Resource):
    '''Hunting Indicators uploaded'''

    from werkzeug import datastructures
    parser = requestparse(['file', 'indicator_type', 'host_identifier', "query_name", "start", "limit", 'duration', 'type', 'date'],
                          [datastructures.FileStorage, str, str, str, int, int, int, int, str],
                          ['Threat file', 'type of indicator (md5/sha256/domain name)', 'host_identifier of the node', "query_name", "start", "limit", 'duration', 'type', 'date'],
                          [True, True, False, False, False, False, False, False, False],
                          [None, PolyLogyxServerDefaults.search_supporting_columns, None, None, None, None, [1, 2, 3, 4], [1, 2], None],
                          [None, None, None, None, 0, 100, 3, 2, dt.datetime.utcnow().strftime('%Y-%m-%d')])

    @ns.expect(parser)
    def post(self):
        args = self.parser.parse_args()
        data = None
        message = None
        status = "failure"
        lines = None

        type = args['indicator_type']
        file = args['file']
        query_name = args['query_name']
        host_identifier = args['host_identifier']
        start = args['start']
        limit = args['limit']

        start_date, end_date = get_start_dat_end_date(args)

        try:
            lines = [line.decode('utf-8').replace('\n', '').replace('\r', '') for line in file.readlines()]
        except Exception as e:
            message = "We are unable to read this file with this format!"
        if lines is not None:
            results = filter_results_through_indicators(lines, type, host_identifier, query_name, start, limit, start_date, end_date)
        else:
            results = {"message": message, "status": status, "data": data}
        return marshal(results, parentwrapper.common_response_wrapper, skip_none=True)


def filter_results_through_indicators(lines, type, host_identifier, query_name, start, limit, start_date, end_date):
    status = "failure"
    data = None
    nodes = []
    if host_identifier:
        nodes = get_nodes_for_host_id(host_identifier)
    try:
        data = dao.results_with_indicators_filtered(lines, type, [node.id for node in nodes], query_name, start, limit, start_date, end_date)
        message = "Successfully fetched the results through the hunt"
        status = "success"
    except Exception as e:
        message = str(e)

    return {"message": message, "status": status, "data": data}


@require_api_key
@ns.route('/indicators/upload/export', endpoint="export_result_for_indicators_uploaded")
class ExportIndicatorsUpload(Resource):
    '''Exports results of Hunting Indicators uploaded'''

    from werkzeug import datastructures
    parser = requestparse(['file', 'indicator_type', 'host_identifier', "query_name", 'duration', 'type', 'date'],
                          [datastructures.FileStorage, str, str, str, int, int, str],
                          ['Threat file', 'type of indicator (md5/sha256/domain name)', 'host_identifier of the node', "query_name", 'duration', 'type', 'date'],
                          [True, True, False, False, False, False, False],
                          [None, PolyLogyxServerDefaults.search_supporting_columns, None, None, [1, 2, 3, 4], [1, 2], None],
                          [None, None, None, None, 3, 2, dt.datetime.utcnow().strftime('%Y-%m-%d')])

    @ns.expect(parser)
    def post(self):
        args = self.parser.parse_args()
        data = None
        message = None
        status = "failure"
        lines = None

        type = args['indicator_type']
        file = args['file']
        query_name = args['query_name']
        host_identifier = args['host_identifier']
        nodes = get_nodes_for_host_id(host_identifier)
        start_date, end_date = get_start_dat_end_date(args)
        try:
            lines = [line.decode('utf-8').replace('\n', '').replace('\r', '') for line in file.readlines()]
        except Exception as e:
            message = "We are unable to read this file with this format!"
        if lines is not None:
            try:
                results = dao.results_with_indicators_filtered_to_export(lines, type, [node.id for node in nodes], query_name, start_date, end_date)
                results = [r for r, in results]
                headers = []
                if not len(results) == 0:
                    firstRecord = results[0]
                    for key in firstRecord.keys():
                        headers.append(key)

                bio = BytesIO()
                writer = csv.writer(bio)
                writer.writerow(headers)

                for data in results:
                    row = []
                    row.extend([data.get(column, '') for column in headers])
                    writer.writerow(row)

                bio.seek(0)

                file_data = send_file(
                  bio,
                  mimetype='text/csv',
                  as_attachment=True,
                  attachment_filename='hunt_query_results.csv'
                )
                return file_data
            except Exception as e:
                data = []
                message = str(e)

        return marshal(respcls(message, status, data), parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/activity/search', endpoint="results_search")
@ns.doc(params={'conditions':"conditions to filter activity", 'host_identifier':"host id of the node", 'query_name':"query name to hunt for", 'start':"start value for pagination", 'limit':"end value for pagination"})
class ActivitySearch(Resource):
    ''' Searches in result log table for the payload given '''
    parser = requestparse(['conditions', 'host_identifier', 'query_name', 'start', 'limit', 'duration', 'type', 'date'],
                          [dict, str, str, int, int, int, int, str],
                          ["conditions to search for", 'host_identifier of the node', 'query name', 'start', 'limit', 'duration', 'type', 'date'],
                          [True, False, False, False, False, False, False, False],
                          [None, None, None, None, None, [1, 2, 3, 4], [1, 2], None],
                          [None, None, None, 0, 100, 3, 2, dt.datetime.utcnow().strftime('%Y-%m-%d')])

    @ns.expect(parser)
    def post(self):
        args = self.parser.parse_args()
        host_identifier = args['host_identifier']
        query_name = args['query_name']
        start = args['start']
        limit = args['limit']
        conditions = args['conditions']

        status = "failure"

        start_date, end_date = get_start_dat_end_date(args)

        try:
            search_rules = SearchParser()
            root = search_rules.parse_group(conditions)
        except UnSupportedSeachColumn as e:
            return marshal(respcls(str(e), status),
                           parentwrapper.common_response_wrapper, skip_none=True)
        except Exception as e:
            message = str(e)
            return marshal(respcls(message, status),
                           parentwrapper.common_response_wrapper, skip_none=True)

        try:
            filter = root.run('', [], 'result_log')
        except Exception:
            return marshal(respcls("Conditions passed are not correct! Please check once and try again!", status),
                           parentwrapper.common_response_wrapper, skip_none=True)

        data = dao.result_log_search_query(filter, [node.id for node in get_nodes_for_host_id(host_identifier)], query_name, start, limit, start_date, end_date)
        message = "Successfully fetched the data through the payload given"
        status = "success"

        return marshal(respcls(message, status, data), parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/queryresult/delete', endpoint = "delete_queryresult")
@ns.doc(params = {'days_of_data':"no.of days of data to delete"})
class DeleteQueryResult(Resource):
    '''Deleting the scheduled query result for the no.of days given will be done here'''
    parser = requestparse(['days_of_data'],[int],["no.of days of data to delete"],[True])

    def func(self):
        args = self.parser.parse_args()
        if args['days_of_data']>0:
            since = dt.datetime.now() - dt.timedelta(hours=24 * int(args['days_of_data']))
            dao.del_result_log_obj(since)
            db.session.commit()
            message = "Query result data is deleted successfully"
            status = "success"
        else:
            message = "days of data should be a positive number!"
            status = "failure"
        return marshal(respcls(message,status),parentwrapper.common_response_wrapper,skip_none=True)

    @ns.expect(parser)
    def post(self):
        return self.func()


@require_api_key
@ns.route('/schedule_query/export', endpoint="schedule_query_export")
@ns.doc(params = {'query_name':"query name", 'host_identifier':"host identifier of the node"})
class ExportScheduleQueryCSV(Resource):
    '''Exports schedule query results into a csv file'''
    parser = requestparse(['query_name', 'host_identifier'], [str, str], ["name of the query", "host identifier of the node"], [True, True])

    @ns.expect(parser)
    def post(self):
        all_args = self.parser.parse_args()

        query_name = all_args['query_name']
        host_identifier = all_args['host_identifier']
        node_id = get_node_id_by_host_id(host_identifier)
        if not node_id:
            message = "Node doesnot exists for the id given"
        else:
            record_query = dao.record_query(node_id,query_name)
            results = [r for r, in record_query]
            if not results:
                message = "Results can't be retrieved for the Payload given! May be data is empty"
            else:
                headers = []
                if not len(results)==0:
                    firstRecord = results[0]
                    for key in firstRecord.keys():
                        headers.append(key)

                bio = BytesIO()
                writer = csv.writer(bio)
                writer.writerow(headers)

                for data in results:
                    row = []
                    row.extend([data.get(column, '') for column in headers])
                    writer.writerow(row)

                bio.seek(0)

                file_data = send_file(
                    bio,
                    mimetype='text/csv',
                    as_attachment=True,
                    attachment_filename='query_results.csv'
                )
                return file_data
        return marshal(respcls(message, "failure"),
                       parentwrapper.common_response_wrapper, skip_none=True)


@require_api_key
@ns.route('/options/add', endpoint = "add_options")
@ns.doc(params = {'option':"option data", 'name':"name for the option"})
class AddOption(Resource):
    '''Add Options Used by PolyLogyx server'''
    parser = requestparse(['option'],[dict],["option data"],[True])

    @ns.expect(parser)
    def post(self):
        args = self.parser.parse_args()
        data = {}
        existing_option = dao.options_query()
        options = args['option']

        for k, v in options.items():
            option = dao.options_filter_by_key(k)
            if option:
                option.option = v
                option.update(option)
            else:
                dao.create_option(k,v)
        if existing_option:
            existing_option.option = json.dumps(args['option'])
            existing_option.update(options)
            data = json.loads(existing_option.option)
        else:
            data = dao.create_option_by_option(json.dumps(args['option'])).option
        current_app.logger.info("Options are added/updated")
        message = "Options are updated successfully"
        status = "success"
        return marshal(respcls(message,status,data),parentwrapper.common_response_wrapper,skip_none=True)


@require_api_key
@ns.route('/options', endpoint = "_options")
class GetOption(Resource):
    '''Get Options Used by PolyLogyx server'''

    def get(self):
        existing_option = json.loads(dao.options_query().option)
        message = "Options are fetched successfully"
        status = "success"
        return marshal(respcls(message,status,existing_option),parentwrapper.common_response_wrapper,skip_none=True)
