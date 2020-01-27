# -*- coding: utf-8 -*
import ast
import base64
import datetime as dt
import json
import os
from io import BytesIO
from operator import itemgetter, and_

import requests
import sqlalchemy
import unicodecsv as csv
from flask import (
    Blueprint, current_app, flash, jsonify, redirect, render_template, send_from_directory,
    request, send_file, url_for)
from flask_login import login_required, current_user
from flask_paginate import Pagination
from sqlalchemy import or_, func, desc, cast,asc
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from polylogyx.database import db
from polylogyx.models import (
    DistributedQuery, DistributedQueryTask, DistributedQueryResult,
    FilePath, Node, Pack, Query, Tag, Rule, ResultLog, StatusLog, EmailRecipient, CarveSession, NodeData,
    Alerts, Options, Settings, NodeReconData, DashboardData, User,
    IOCIntel, ThreatIntelCredentials)
from polylogyx.search_rules import AndCondition, OPERATOR_MAP, BaseCondition, OrCondition

from polylogyx.constants import PolyLogyxServerDefaults, DefaultInfoQueries
from polylogyx.util.constants import DEFAULT_EVENT_STATE_QUERIES
from polylogyx.utils import (
    create_query_pack_from_upload, flash_errors, get_paginate_options,
    merge_two_dicts, get_node_health, DateTimeEncoder)
from polylogyx.util.mitre import MitreApi, TestMail

from .forms import (
    AddDistributedQueryForm,
    CreateQueryForm,
    UpdateQueryForm,
    CreateTagForm,
    UploadPackForm,
    FilePathForm,
    FilePathUpdateForm,
    CreateRuleForm,
    UpdateRuleForm,
    UpdateNodeForm,
    CreateOptionForm,
    CreateSettingForm, UploadIntelForm, CreateSearchForm)

blueprint = Blueprint('manage', __name__,
                      template_folder='../templates/manage',
                      url_prefix='/manage')
process_guid_column = 'process_guid'
parent_process_guid_column = 'parent_process_guid'


@blueprint.context_processor
def inject_models():
    return dict(Node=Node, Pack=Pack, Query=Query, Tag=Tag,
                Rule=Rule, FilePath=FilePath,
                DistributedQuery=DistributedQuery,
                DistributedQueryTask=DistributedQueryTask,
                current_app=current_app,
                db=db)

@blueprint.route('/')
@login_required
def index():
    alert_data = fetch_alert_node_query_status()
    chart_data = fetch_dashboard_data(alert_data)
    json_data = json.dumps(chart_data, ensure_ascii=False)

    return render_template('dashboard.html', chart_data=json_data)

@blueprint.route('/nodes', methods=['GET', 'POST'])
@blueprint.route('/nodes/<string:page>')
@login_required
def nodes():
    """ Display Node table content. """
    if request.method == 'POST':
        state = request.form.get('state')
        platform = request.form.get('platform')
        results = get_result_by_nodes(0, 10, state, platform)
        return jsonify(results)
    else:
        node_status = get_active_inactive_nodes_count()
        return render_template('index.html', node_status=node_status)


@blueprint.route('/changepassword', methods=['GET', 'POST'])
@login_required
def change_password():
    from polylogyx.users.forms import ChangePasswordForm

    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            username = current_user.username

        password = form.password.data
        new_password = form.new_password.data
        confirm_new_password = form.confirm_new_password.data

        if new_password != confirm_new_password:
            flash(u"Password and confirm password should match", 'danger')
        else:
            try:
                from polylogyx.extensions import bcrypt
                user = User.query.filter_by(username=username).first()
                if bcrypt.check_password_hash(user.password, password):
                    user.update(password=bcrypt.generate_password_hash(new_password))
                    user.update(
                        password=bcrypt.generate_password_hash(new_password.encode("utf-8")).decode("utf-8"))

                    flash(u"Successfully changed the password ", 'success')
                else:
                    flash(u"Invalid password ", 'danger')
            except Exception as error:
                print("Failed to create user {0} - {1}".format(username, error))
    flash_errors(form)
    return render_template('forms/change_password.html', form=form)


def get_result_by_nodes(startPage=0, perPageRecords=10, state=None, platform=None):
    """ Node Result Set  using server side render for ajax datatable. """
    results, columns, columnsDefined, searchTerm = [], [], False, None

    try:
        startPage = int(request.values['start'])
        perPageRecords = int(request.values['length'])
        if 'search[value]' in request.values and (request.values['search[value]'] != ""):
            searchTerm = (request.values['search[value]'])
        if (request.values['columns[0][data]']):
            columnsDefined = True
    except Exception as e:
        pass

    base_query = Node.query
    if platform and state:
        current_time = dt.datetime.utcnow()
        checkin_interval = current_app.config['POLYLOGYX_CHECKIN_INTERVAL']
        current_time = current_time - checkin_interval
        if 'online' == state:
            base_query = base_query.filter((Node.last_checkin > current_time))
        elif 'offline' == state:
            base_query = base_query.filter((Node.last_checkin < current_time))
        base_query = base_query.filter(get_platform_filter(platform))

    count = base_query.count()
    countFiltered = count
    if searchTerm:
        base_query = base_query.filter(
            or_(and_(Node.os_info.op('->')('name') != None, Node.os_info['name'].astext.ilike('%' + searchTerm + '%')),
                and_(Node.os_info.op('->')('name') == None, Node.platform.ilike('%' + searchTerm + '%')),
                and_(Node.node_info.op('->')('computer_name') != None,
                     Node.node_info['computer_name'].astext.ilike('%' + searchTerm + '%')),
                cast(Node.last_ip, sqlalchemy.String).ilike('%' + searchTerm + '%')
                ))
        countFiltered = base_query.count()
        record_query = base_query.order_by(desc(Node.id)).offset(startPage).limit(perPageRecords).all()
    else:
        record_query = base_query.order_by(desc(Node.id)).offset(startPage).limit(perPageRecords).all()
    for value in record_query:
        res, data = {}, value.to_dict()
        res['Host_Identifier'] = value.display_name
        if value.os_info:
            res['os'] = value.os_info['name']
        else:
            res['os'] = value.platform
        res['last_ip'] = data["last_ip"]
        res['tags'] = [tag.to_dict() for tag in value.tags]
        res['id'] = data['id']
        res['health'] = get_node_health(value)
        res['platform'] = data["platform"]

        res['activity_url'] = url_for("manage.node_activity", node_id=value.id)
        res['node_url'] = url_for("manage.get_node", node_id=value.id)
        res['tag_url'] = url_for("manage.tag_node", node_id=value.id)
        results.append(res)

    try:
        firstRecord = results[0]
        for key in firstRecord.keys():
            columns.append({'data': key, 'title': key})
    except Exception as e:
        print(e, "zero records found")

    output = {}
    try:
        output['sEcho'] = str(int(request.values['sEcho']))
    except Exception as e:
        pass  # print(e, 'error in echo')

    output['iRecordsFiltered'] = str(countFiltered)
    output['iTotalRecords'] = str(count)
    output['pageLength'] = str(perPageRecords)
    output['iTotalDisplayRecords'] = str(countFiltered)
    aaData_rows = results

    if not columnsDefined:
        output['columns'] = columns
    output['aaData'] = aaData_rows
    return output


@blueprint.route('/nodes/export', methods=['POST'])
def export_node_csv():
    """ Export Node table content. """
    record_query = Node.query.order_by(desc(Node.id)).all()
    results = []
    for value in record_query:
        res = {}
        data = value.to_dict()
        res['Host_Identifier'] = value.display_name
        if value.os_info:
            res['os'] = value.os_info['name']
        else:
            res['os'] = value.platform

        res['last_ip'] = data["last_ip"]
        res['tags'] = [tag.to_dict() for tag in value.tags]
        res['id'] = data['id']
        res['health'] = get_node_health(value)
        res['platform'] = data["platform"]

        res['activity_url'] = url_for("manage.node_activity", node_id=value.id)
        res['node_url'] = url_for("manage.get_node", node_id=value.id)
        res['tag_url'] = url_for("manage.tag_node", node_id=value.id)
        results.append(res)

    firstRecord = results[0]
    headers = []
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

    response = send_file(
        bio,
        mimetype='text/csv',
        as_attachment=True,
        attachment_filename='query_results.csv'
    )

    return response



@blueprint.route('/live_queries')
@blueprint.route('/live_queries/<int:page>')
@blueprint.route('/live_queries/<any(active, inactive):status>')
@blueprint.route('/live_queries/<any(active, inactive):status>/<int:page>')
@login_required
def live_queries(page=1, status='active'):
    form = distributed_form()
    if status == 'inactive':
        nodes = Node.query.filter_by(is_active=False)
    else:
        nodes = Node.query.filter_by(is_active=True)
    sql = None
    queryId = request.args.get('queryId')
    if queryId:
        sql = Query.query.filter(Query.id == queryId).first().sql

    nodes = get_paginate_options(
        request,
        Node,
        ('id', 'host_identifier', 'enrolled_on', 'last_checkin'),
        existing_query=nodes,
        page=page,
    )

    display_msg = 'displaying <b>{start} - {end}</b> of <b>{total}</b> {record_name} '
    display_msg += '<a href="{0}" title="Export node information to csv">'.format(
        url_for('manage.nodes_csv')
    )
    display_msg += '<i class="fa fa-download"></i></a>'

    pagination = Pagination(page=page,
                            per_page=nodes.per_page,
                            total=nodes.total,
                            alignment='center',
                            show_single_page=False,
                            display_msg=display_msg,
                            record_name='{status} nodes'.format(status=status),
                            bs_version=3)

    return render_template('nodes.html',
                           nodes=nodes.items, form=form,
                           pagination=pagination,
                           status=status, sql=sql)





def fetch_query_parameters():
    nodes = Node.query.all()

    all_args = request.args.to_dict()

    try:
        timestamp = request.args.get('timestamp')
        timestamp = dt.datetime.fromtimestamp(float(timestamp))
    except Exception:
        timestamp = dt.datetime.utcnow()
        timestamp -= dt.timedelta(days=30)
    for node in nodes:
        dqt = db.session.query(DistributedQueryTask) \
            .join(DistributedQueryResult) \
            .join(DistributedQuery) \
            .join(Node) \
            .options(
            db.lazyload('*'),
            db.contains_eager(DistributedQueryTask.results),
            db.contains_eager(DistributedQueryTask.distributed_query),
            db.contains_eager(DistributedQueryTask.node)
        ) \
            .filter(
            DistributedQueryTask.node == node,
            or_(
                DistributedQuery.timestamp >= timestamp,
                DistributedQueryTask.timestamp >= timestamp,
            )
        )
        rlq = node.result_logs.filter(ResultLog.timestamp > timestamp, ResultLog.action != 'removed')
        for key, value in all_args.items():
            rlq = rlq.filter(ResultLog.columns[key].astext.contains(str(value)))
            dqt = dqt.filter(DistributedQueryResult.columns[key].astext.contains(str(value)))
        recent = rlq.all()

        queries = dqt.all()
        setattr(node, 'recent', recent)
        setattr(node, 'query', queries)

    return render_template('node_with_filtered_results.html', nodes=nodes)


@blueprint.route('/schedule_query/export', methods=['POST'])
def export_schedule_query_csv():
    all_args = request.form.to_dict()

    query_name = all_args['query_name']
    node_id = all_args['node_id']
    record_query = db.session.query(ResultLog.columns).filter(
        and_(ResultLog.node_id == (node_id), and_(ResultLog.name == query_name, ResultLog.action != 'removed'))).all()

    results = [r for r, in record_query]
    firstRecord = results[0]
    headers = []
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

    response = send_file(
        bio,
        mimetype='text/csv',
        as_attachment=True,
        attachment_filename='query_results.csv'
    )

    return response


@blueprint.route('/alerts_source/export', methods=['POST'])
def export_alerts_source_csv():
    """ Export Alert table content. """
    source = request.form['source']
    record_query = db.session.query(Alerts).filter(
        (Alerts.source == (source))).order_by(
        desc(Alerts.id)).all()
    results = []
    for value in record_query:
        res = {}
        data = value.to_dict()
        nName = value.node.display_name
        nId = data["node_id"]
        res['Host'] = {'name': nName, 'id': nId}
        # res['Query Name'] = data["query_name"]
        res['Severity'] = data["severity"]
        res['Created At'] = data["created_at"]
        if source == 'rule':
            res['rule_name'] = value.rule.name
        elif source == 'self' or source == 'IOC' or source == 'ioc':
            pass
        else:
            res['Intel_data'] = data["source_data"]
        res['Alerted Entry'] = data["message"]
        res['Investigate'] = value.id
        results.append(res)

    firstRecord = results[0]
    headers = []
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

    response = send_file(
        bio,
        mimetype='text/csv',
        as_attachment=True,
        attachment_filename='query_results.csv'
    )

    return response


@blueprint.route('/nodes/search/export', methods=['POST'])
def export_node_search_query_csv():
    all_args = request.form.to_dict()

    name = all_args['name']
    node_id = all_args['node_id']
    searchTerm = all_args['searchTerm']
    searchColumn = all_args['searchColumn']
    type = all_args['type']

    if type == 'node_data':
        node_data_str = "SELECT obj.value as elem FROM   node_data nd JOIN   LATERAL jsonb_array_elements(nd.data) obj(value) ON obj.value->>'" + searchColumn + "' ilike '%" + searchTerm + "%' and node_id=" + node_id + " and name='" + name + "' ;"
        queryStrList = db.engine.execute(sqlalchemy.text(node_data_str))
    else:
        queryStrList = db.session.query(ResultLog.columns) \
            .filter(ResultLog.name == name) \
            .filter(ResultLog.node_id == int(node_id)) \
            .filter(
            ResultLog.columns[searchColumn].astext.ilike("%" + searchTerm + "%")
        )

    results = [r for r, in queryStrList]
    headers = []
    if results:
        firstRecord = results[0]
        headers = []
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

    response = send_file(
        bio,
        mimetype='text/csv',
        as_attachment=True,
        attachment_filename='query_results.csv'
    )

    return response


@blueprint.route('/nodes.csv')
@login_required
def nodes_csv():
    headers = [
        'Display name',
        'Host identifier',
        'Enrolled On',
        'Last Check-in',
        'Last IP Address',
        'Is Active',
    ]

    column_names = map(itemgetter(0), current_app.config['POLYLOGYX_CAPTURE_NODE_INFO'])
    labels = map(itemgetter(1), current_app.config['POLYLOGYX_CAPTURE_NODE_INFO'])
    headers.extend(labels)
    headers = list(map(str.title, headers))

    bio = BytesIO()
    writer = csv.writer(bio)
    writer.writerow(headers)

    for node in Node.query:
        row = [
            node.display_name,
            node.host_identifier,
            node.enrolled_on,
            node.last_checkin,
            node.last_ip,
            node.is_active,
        ]
        row.extend([node.node_info.get(column, '') for column in column_names])
        writer.writerow(row)

    bio.seek(0)

    response = send_file(
        bio,
        mimetype='text/csv',
        as_attachment=True,
        attachment_filename='nodes.csv'
    )

    return response


@blueprint.route('/nodes/tagged/<string:tags>')
@login_required
def nodes_by_tag(tags):
    if tags == 'null':
        nodes = Node.query.filter(Node.tags == None).all()
    else:
        tag_names = [t.strip() for t in tags.split(',')]
        nodes = Node.query.filter(Node.tags.any(Tag.value.in_(tag_names))).all()
    return render_template('nodes.html', nodes=nodes)


@blueprint.route('/node/<int:node_id>', methods=['GET', 'POST'])
@login_required
def get_node(node_id):
    node = Node.query.filter_by(id=node_id).first_or_404()
    form = UpdateNodeForm(request.form)
    if form.validate_on_submit():
        node_info = node.node_info.copy()

        if form.display_name.data:
            node_info['display_name'] = form.display_name.data
        elif 'display_name' in node_info:
            node_info.pop('display_name')

        node.node_info = node_info
        node.is_active = form.is_active.data
        node.save()

        if request.is_xhr:
            return '', 204

        return redirect(url_for('manage.get_node', node_id=node.id))

    form = UpdateNodeForm(request.form, obj=node)
    flash_errors(form)

    packs = node.packs \
        .options(
        db.joinedload(Pack.tags, innerjoin=True),
        db.joinedload(Pack.queries, innerjoin=True),
    ).order_by(Pack.name)

    queries = node.queries \
        .options(
        db.joinedload(Query.tags, innerjoin=True),
        db.joinedload(Query.packs)
    ).order_by(Query.name)

    node_data_list = NodeData.query.filter(NodeData.node_id == node.id).all()
    node_data = []
    node_default_queries = get_default_query_list(node).copy()

    for r in node_data_list:
        node_data_elem = r.to_dict_obj()
        node_data.append(node_data_elem)
        node_default_queries.pop(node_data_elem['name'], None)
    for key, value in node_default_queries.items():
        node_data_elem = {"name": key, "data": [], "updated_at": " "}
        node_data.append(node_data_elem)

    return render_template('node.html', form=form, node=node,
                           packs=packs, queries=queries, node_data=node_data,
                           node_data_json=json.dumps(node_data),
                           )


@blueprint.route('/node/<int:node_id>/activity')
@login_required
def node_activity(node_id):
    # queryResults = getQueryResults(node_id)

    node = Node.query.filter_by(id=node_id) \
        .options(db.lazyload('*')).first()
    try:
        timestamp = request.args.get('timestamp')
        timestamp = dt.datetime.fromtimestamp(float(timestamp))
    except Exception:
        timestamp = dt.datetime.utcnow()
        timestamp -= dt.timedelta(days=30)
    queries_packs = get_queries_or_packs_of_node(node_id)
    queries_packs = dict(queries_packs)
    # recent = node.result_logs.filter(ResultLog.timestamp > timestamp, ResultLog.action != 'removed').all()
    queries_packs_keys = list(queries_packs.keys())

    return render_template('activity.html', node=node, queries_packs=queries_packs,
                           queries_packs_keys=queries_packs_keys)


def get_queries_or_packs_of_node(node_id):
    return db.session.query(
        ResultLog.name, db.func.count(ResultLog.name)). \
        filter(ResultLog.node_id == (node_id)).group_by(ResultLog.name). \
        all()


@blueprint.route('/ajax/node/<int:node_id>/activity')
@login_required
def node_ajax_activity(node_id):
    node = Node.query.filter_by(id=node_id) \
        .options(db.lazyload('*')).first()
    try:
        timestamp = request.args.get('timestamp')
        timestamp = dt.datetime.fromtimestamp(float(timestamp))
    except Exception:
        timestamp = dt.datetime.utcnow()
        timestamp -= dt.timedelta(days=30)

    recent = node.result_logs.filter(ResultLog.timestamp > timestamp, ResultLog.action != 'removed').all()
    queries = db.session.query(DistributedQueryTask) \
        .join(DistributedQuery) \
        .join(Node) \
        .options(
        db.lazyload('*'),
        db.contains_eager(DistributedQueryTask.distributed_query),
        db.contains_eager(DistributedQueryTask.node)
    ) \
        .filter(
        DistributedQueryTask.node == node,
        or_(
            DistributedQuery.timestamp >= timestamp,
            DistributedQueryTask.timestamp >= timestamp,
        )
    ).all()
    return render_template('_activity.html', node=node, recent=recent, queries=queries)


@blueprint.route('/node/<int:node_id>/logs')
@blueprint.route('/node/<int:node_id>/logs/<int:page>')
@login_required
def node_logs(node_id, page=1):
    node = Node.query.filter(Node.id == node_id).first_or_404()
    status_logs = StatusLog.query.filter_by(node=node)

    status_logs = get_paginate_options(
        request,
        StatusLog,
        ('line', 'message', 'severity', 'filename'),
        existing_query=status_logs,
        page=page,
        max_pp=50,
        default_sort='desc'
    )

    pagination = Pagination(page=page,
                            per_page=status_logs.per_page,
                            total=status_logs.total,
                            alignment='center',
                            show_single_page=False,
                            record_name='status logs',
                            bs_version=3)

    return render_template('logs.html', node=node,
                           status_logs=status_logs.items,
                           pagination=pagination)


@blueprint.route('/ajax/node/<int:node_id>/status')
@login_required
def node__status_logs(node_id, page=1):
    startPage = 0
    perPageRecords = 10
    try:
        startPage = int(request.values['start'])
        perPageRecords = int(request.values['length'])
        if (request.values['columns[0][data]']):
            columnsDefined = True
    except:
        print('error in request')
    status_logs = db.session.query(StatusLog).with_entities(StatusLog.line, StatusLog.message, StatusLog.severity,
                                                            StatusLog.filename, StatusLog.created, StatusLog.version).filter(StatusLog.node_id == node_id) .order_by(
            desc(StatusLog.id))\
        .offset(startPage).limit(
        perPageRecords).all()

    data = []
    for status_log in status_logs:
        data.append({
            "line": status_log[0],
            "message": status_log[1],
            "severity": status_log[2],
            "filename": status_log[3],
            "created": status_log[4],
            "version": status_log[5],
        })

    output = {}
    try:
        output['sEcho'] = str(int(request.values['sEcho']))
    except:
        print('error in echo')
    count = db.session.query(db.func.count(StatusLog.id)).filter(StatusLog.node_id == node_id).all()[0][0]
    countFiltered = count
    output['iRecordsFiltered'] = str(countFiltered)
    output['iTotalRecords'] = str(count)
    output['pageLength'] = str(perPageRecords)

    output['iTotalDisplayRecords'] = str(countFiltered)
    aaData_rows = data

    # if not columnsDefined:
    output['columns'] = [
        {"data": "line"},
        {"data": "message"},
        {"data": "severity"},
        {"data": "filename"},

    ]
    output['aaData'] = aaData_rows

    return jsonify(output)


@blueprint.route('/node/<int:node_id>/tags', methods=['GET', 'POST'])
@login_required
def tag_node(node_id):
    node = Node.query.filter(Node.id == node_id).first_or_404()
    if request.is_xhr and request.method == 'POST':
        node.tags = create_tags(*request.get_json())
        node.save()
        return jsonify({}), 202

    return redirect(url_for('manage.get_node', node_id=node.id))


@blueprint.route('/packs', methods=['GET', 'POST'])
@login_required
def packs():
    packs = Pack.query \
        .options(
        db.joinedload(Pack.tags),
        db.joinedload(Pack.queries),
        db.joinedload(Pack.queries, Query.packs, innerjoin=True)
    ).all()

    form = UploadPackForm()
    if form.validate_on_submit():
        pack = create_query_pack_from_upload(form.pack, form.category.data)

        # Only redirect back to the pack list if everything was successful
        if pack is not None:
            return redirect(url_for('manage.packs', _anchor=pack.name))

    flash_errors(form)
    return render_template('packs.html', packs=packs, hide_query_tags=True, form=form)


@blueprint.route('/packs/add', methods=['GET', 'POST'])
@blueprint.route('/packs/upload', methods=['POST'])
@login_required
def add_pack():
    form = UploadPackForm()
    if form.validate_on_submit():
        pack = create_query_pack_from_upload(form.pack, form.category.data)

        # Only redirect back to the pack list if everything was successful
        if pack is not None:
            flash(u"Successfully created the pack", 'success')
            return redirect(url_for('manage.packs', _anchor=pack.name))

    flash_errors(form)
    return render_template('pack.html', form=form)


@blueprint.route('/pack/<string:pack_name>/tags', methods=['GET', 'POST'])
@login_required
def tag_pack(pack_name):
    pack = Pack.query.filter(Pack.name == pack_name).first_or_404()
    if request.is_xhr:
        if request.method == 'POST':
            pack.tags = create_tags(*request.get_json())
            pack.save()
        return jsonify(tags=[t.value for t in pack.tags])

    return redirect(url_for('manage.packs'))


@blueprint.route('/test', methods=['GET', 'POST'])
@login_required
def test():
    return fetch_query_parameters()



@blueprint.route('/queries')
@login_required
def queries():
    queries = Query.query \
        .options(
        db.joinedload(Query.tags),
        db.joinedload(Query.packs),
        db.joinedload(Query.packs, Pack.queries, innerjoin=True)
    ).all()

    pack_queries = Query.query \
        .options(
        db.joinedload(Query.tags),
        db.joinedload(Query.packs),
        db.joinedload(Query.packs, Pack.queries, innerjoin=True)
    ).filter(Query.packs.any()).all()

    return render_template('queries.html', queries=queries, pack_queries=pack_queries)


@blueprint.route('/queries/add', methods=['GET', 'POST'])
@login_required
def add_query():
    form = CreateQueryForm()
    form.set_choices()

    if form.validate_on_submit():
        if not form.shard.data:
            form.shard.data = 100
        if form.packs.data:
            packs = Pack.query.filter(Pack.name.in_(form.packs.data)).all()
        else:
            packs = []
        query = Query(name=form.name.data,
                      sql=form.sql.data,
                      interval=form.interval.data,
                      platform=form.platform.data,
                      version=form.version.data,
                      description=form.description.data,
                      value=form.value.data,
                      packs=packs,
                      removed=form.removed.data,
                      shard=form.shard.data,
                      snapshot=form.snapshot.data)
        query.tags = create_tags(*form.tags.data.splitlines())
        query.save()

        flash(u"Successfully Added the query", 'success')
        return redirect(url_for('manage.query', query_id=query.id))

    flash_errors(form)
    return render_template('query.html', form=form,query={})


@blueprint.route('/readme', methods=['GET'])
@login_required
def readme():
    return render_template('readme.html')


@blueprint.route('/DeploymentGuide', methods=['GET'])
@login_required
def dep_guide():
    return render_template('DeploymentGuide.html')



@blueprint.route('/carves/download/<string:host_identifier>/<string:filename>')
def carve_downloads(host_identifier, filename):
    if filename is None:
        print('Error')
        # self.Error(400)
    try:
        return send_from_directory(directory=PolyLogyxServerDefaults.BASE_URL + '/carves/' + host_identifier + '/',
                                   as_attachment=True,
                                   filename=filename)
    except Exception as e:
        current_app.logger.error(e)
        # self.log.exception(e)
        # self.Error(400)


@blueprint.route('/carves')
@blueprint.route('/carves/<int:page>')
@login_required
def carves(status=None, page=1):
    carves = CarveSession.query

    carves = get_paginate_options(
        request,
        CarveSession,
        ('id', 'status', 'timestamp'),
        existing_query=carves,
        page=page,
        default_sort='desc'
    )
    display_msg = 'displaying <b>{start} - {end}</b> of <b>{total}</b> {record_name}'

    pagination = Pagination(page=page,
                            per_page=carves.per_page,
                            total=carves.total,
                            alignment='center',
                            show_single_page=False,
                            display_msg=display_msg,
                            record_name='{0} alerts'.format(status or '').strip(),
                            bs_version=3)

    return render_template('carve.html', carves=carves.items,
                           status=status, pagination=pagination)


@blueprint.route('/queries/tagged/<string:tags>')
@login_required
def queries_by_tag(tags):
    tag_names = [t.strip() for t in tags.split(',')]
    queries = Query.query.filter(Query.tags.any(Tag.value.in_(tag_names))).all()
    return render_template('queries.html', queries=queries)


@blueprint.route('/query/<int:query_id>', methods=['GET', 'POST'])
@login_required
def query(query_id):
    query = Query.query.filter(Query.id == query_id).first_or_404()
    form = UpdateQueryForm(request.form)

    if form.validate_on_submit():
        if form.packs.data:
            query.packs = Pack.query.filter(Pack.name.in_(form.packs.data)).all()
        else:
            query.packs = []

        query.tags = create_tags(*form.tags.data.splitlines())
        if not form.shard.data:
            form.shard.data = 100
        query = query.update(name=form.name.data,
                             sql=form.sql.data,
                             interval=form.interval.data,
                             platform=form.platform.data,
                             version=form.version.data,
                             description=form.description.data,
                             value=form.value.data,
                             removed=form.removed.data,
                             shard=form.shard.data,
                             snapshot=form.snapshot.data)
        if request.method == 'POST':
            flash(u'Successfully updated', 'success')
        return redirect(url_for('manage.query', query_id=query.id))
    flash_errors(form)

    form = UpdateQueryForm(request.form, obj=query)
    return render_template('query.html', form=form, query=query)


@blueprint.route('/query/<int:query_id>/tags', methods=['GET', 'POST'])
@login_required
def tag_query(query_id):
    query = Query.query.filter(Query.id == query_id).first_or_404()
    if request.is_xhr:
        if request.method == 'POST':
            query.tags = create_tags(*request.get_json())
            query.save()
        return jsonify(tags=[t.value for t in query.tags])

    return redirect(url_for('manage.query', query_id=query.id))


@blueprint.route('/files')
@login_required
def files():
    file_paths = FilePath.query.all()
    return render_template('files.html', file_paths=file_paths)


@blueprint.route('/files/add', methods=['GET', 'POST'])
@login_required
def add_file():
    form = FilePathForm()

    if form.validate_on_submit():
        file_path = FilePath(
            category=form.category.data,
            target_paths=form.target_paths.data.splitlines()
        )
        file_path.tags = create_tags(*form.tags.data.splitlines())
        file_path.save()

        return redirect(url_for('manage.files'))

    flash_errors(form)
    return render_template('file.html', form=form)


@blueprint.route('/file/<int:file_path_id>', methods=['GET', 'POST'])
@login_required
def file_path(file_path_id):
    file_path = FilePath.query.filter(FilePath.id == file_path_id).first_or_404()
    form = FilePathUpdateForm(request.form)

    if form.validate_on_submit():
        file_path.tags = create_tags(*form.tags.data.splitlines())
        file_path.set_paths(*form.target_paths.data.splitlines())
        file_path = file_path.update(
            category=form.category.data,
        )

        return redirect(url_for('manage.files'))

    form = FilePathUpdateForm(request.form, obj=file_path)
    flash_errors(form)
    return render_template('file.html', form=form, file_path=file_path)


@blueprint.route('/file/<int:file_path_id>/tags', methods=['GET', 'POST'])
@login_required
def tag_file(file_path_id):
    file_path = FilePath.query.filter(FilePath.id == file_path_id).first_or_404()
    if request.is_xhr:
        if request.method == 'POST':
            file_path.tags = create_tags(*request.get_json())
            file_path.save()
        return jsonify(tags=[t.value for t in file_path.tags])

    return redirect(url_for('manage.files'))


@blueprint.route('/tags', methods=['GET', 'POST'])
@login_required
def tags():
    tags = dict((t.value, {}) for t in Tag.query.all())

    if request.is_xhr:
        return jsonify(tags=tags.keys())

    baseq = db.session.query(Tag.value, db.func.count(Tag.id))

    for tag, count in baseq.join(Tag.nodes).group_by(Tag.id).all():
        tags[tag]['nodes'] = count
    for tag, count in baseq.join(Tag.packs).group_by(Tag.id).all():
        tags[tag]['packs'] = count
    for tag, count in baseq.join(Tag.queries).group_by(Tag.id).all():
        tags[tag]['queries'] = count
    for tag, count in baseq.join(Tag.file_paths).group_by(Tag.id).all():
        tags[tag]['file_paths'] = count
    form = CreateTagForm()
    if form.validate_on_submit():
        create_tags(*form.value.data.splitlines())
        flash(u'Successfully added to the Tags', 'success')
        return redirect(url_for('manage.tags'))

    flash_errors(form)
    return render_template('tags.html', tags=tags, form=form)


@blueprint.route('/ajax/node/config/clear', methods=['GET', 'POST'])
@login_required
def clear_node_config():
    node_id = request.form.get('node_id')
    node = Node.query.filter_by(id=node_id).first_or_404()
    node.config_id = None
    node.update(node)

    response = {}
    response['status'] = 'success'
    return jsonify(response)


@blueprint.route('/configs', methods=['GET'])
@login_required
def configs():
    from polylogyx.models import DefaultQuery, DefaultFilters

    platforms = ["windows", "linux", "darwin"]
    config_data = {}
    for platform in platforms:
        default_platform_queries = DefaultQuery.query.filter(DefaultQuery.platform == platform).all()
        queries_data = {}
        queries_data_x86 = {}
        for default_query in default_platform_queries:
            if default_query.arch == DefaultQuery.ARCH_x86:
                queries_data_x86[default_query.name] = default_query.to_dict()
            else:
                queries_data[default_query.name] = default_query.to_dict()


        #default_filter_obj = DefaultFilters.query.filter(DefaultFilters.platform == platform).first()
        filters_data_x86_64 = DefaultFilters.query.filter(DefaultFilters.platform == platform).filter(
                DefaultFilters.arch != DefaultFilters.ARCH_x86).first()
        filters_data_x86 = DefaultFilters.query.filter(DefaultFilters.platform == platform).filter(
                DefaultFilters.arch == DefaultFilters.ARCH_x86).first()

        # if default_filter_obj:
        #     default_filter = default_filter_obj.filters
        config_data[platform] = {"queries": queries_data,
                                 "filters": filters_data_x86_64.filters}
        if queries_data_x86:
            config_data[platform + "_x86"] = {"queries": queries_data_x86,
                                              "filters": filters_data_x86.filters}

    return render_template('configs.html', configs=json.dumps(config_data))


@blueprint.route('/ajax/config/update', methods=['POST'])
@login_required
def update_platform_filter_query():
    from polylogyx.blueprints import utils
    from polylogyx.models import DefaultQuery, DefaultFilters
    form_data = utils.get_body_data(request)

    result_queries = {}
    platform = form_data.get('platform')
    queries_data = form_data.get('queries')
    filters = form_data.get('filters')
    arch = form_data.get('arch')

    # fetching the filters data to insert to the config dict
    if arch and arch == DefaultFilters.ARCH_x86:
        default_filters_obj = DefaultFilters.query.filter(DefaultFilters.platform == platform.lower()).filter(
                DefaultFilters.arch == DefaultFilters.ARCH_x86).first()
    else:
        default_filters_obj = DefaultFilters.query.filter(DefaultFilters.platform == platform.lower()).filter(
                DefaultFilters.arch != DefaultFilters.ARCH_x86).first()
    if default_filters_obj:
        default_filters_obj.update(filters=filters)

    for key in list(queries_data.keys()):
        if arch and arch == DefaultQuery.ARCH_x86:
            query = DefaultQuery.query.filter(DefaultQuery.name == key).filter(
                DefaultQuery.arch == DefaultQuery.ARCH_x86).filter(
                DefaultQuery.platform == platform.lower()).first()
        else:
            query = DefaultQuery.query.filter(DefaultQuery.name == key).filter(
                DefaultQuery.arch != DefaultQuery.ARCH_x86).filter(
                DefaultQuery.platform == platform.lower()).first()

        if query:
            query = query.update(status=queries_data[key]['status'],
                             interval=queries_data[key]['interval'])
            result_queries[key] = query
        else:
            current_app.logger.error("error for updating query : "+key+" on platform "+platform+" "+arch)

    # formatting the dict of final config
    response = {}
    response['status'] = 'success'

    return jsonify(response)


@blueprint.route('/option/add', methods=['GET', 'POST'])
@login_required
def add_option():
    print('')
    form = CreateOptionForm()
    existing_option = Options.query.filter(Options.name == PolyLogyxServerDefaults.plgx_config_all_options).first()

    if form.validate_on_submit():
        print('saving option')
        options = json.loads(form.option.data)

        # options = ast.literal_eval(form.option.data)

        for k, v in options.items():
            option = Options.query.filter(Options.name == k).first()
            if option:
                option.option = v
                option.update(option)
            else:
                Options.create(name=k, option=v)

        if existing_option:
            existing_option.option = form.option.data
            existing_option.update(option)
            flash(u"Successfully updated Options", 'success')
        else:
            Options.create(name=PolyLogyxServerDefaults.plgx_config_all_options, option=form.option.data)
            flash(u"Successfully created Options", 'success')

        # create_tags(*form.value.data.splitlines())
        return redirect(url_for('manage.add_option'))

    flash_errors(form)
    if existing_option:
        option_json = json.dumps(existing_option.option, ensure_ascii=False)[1:-1]

        return render_template('/forms/option.html', form=form, option=option_json)
    else:
        return render_template('/forms/option.html', form=form, option=None)


@blueprint.route('/setting/add', methods=['GET', 'POST'])
@login_required
def add_setting():
    print('')
    form = CreateSettingForm()
    existing_setting = Settings.query.filter(Settings.name == PolyLogyxServerDefaults.plgx_config_all_settings).first()
    if form.validate_on_submit():
        print('saving setting')
        settings = ast.literal_eval(form.setting.data)
        from flask import current_app
        for k, v in settings.items():
            setting = Settings.query.filter(Settings.name == k).first()
            if k == 'email':
                current_app.config['MAIL_USERNAME'] = v
            elif k == 'smtpPort':
                current_app.config['MAIL_PORT'] = int(v)
            elif k == 'smtpAddress':
                current_app.config['MAIL_SERVER'] = v
            elif k == 'password':
                current_app.config['MAIL_PASSWORD'] = base64.b64decode(v)
            elif k == 'emailRecipients':
                save_email_recipients(v)

            if setting:
                setting.setting = v
                setting.update(setting)
            else:
                Settings.create(name=k, setting=v)

        if existing_setting:
            existing_setting.setting = form.setting.data
            existing_setting.update(setting)
            flash(u"Successfully updated Email Configuration", 'success')
        else:
            Settings.create(name=PolyLogyxServerDefaults.plgx_config_all_settings, setting=form.setting.data)
            flash(u"Successfully created Email Configuration", 'success')

        # create_tags(*form.value.data.splitlines())
        return redirect(url_for('manage.add_setting'))

    flash_errors(form)
    if existing_setting:
        setting_json = json.dumps(existing_setting.setting, ensure_ascii=False)[1:-1]

        return render_template('/forms/setting.html', form=form, setting=setting_json,
                               )
    else:
        return render_template('/forms/setting.html', form=form, setting=None,
                               )


@blueprint.route('/ajax/test_email/send', methods=['POST'])
@login_required
def send_test_email():
    test_mail = TestMail()
    username = request.form.get('username')
    password = request.form.get('password')
    smtp = request.form.get('smtp')
    recipients = request.form.get('recipients').split(",")
    is_credntials_valid = test_mail.test(username=username, password=password, smtp=smtp, recipients=recipients)
    response_data = {}
    if is_credntials_valid:
        response_data['status'] = 'success'
    else:
        response_data['status'] = 'failure'
        response_data[
            'message'] = 'Could not validate credentials. Please enable less secure apps if using gmail and verify security alert prompt on your mail. '
    return jsonify(response_data)


@blueprint.route('/purge/update', methods=['GET', 'POST'])
@login_required
def update_purge():
    print('')
    form = CreateSettingForm()
    if form.validate_on_submit():
        purge_data_duration_obj = Settings.query.filter(Settings.name == 'purge_data_duration').first()
        purge_data_duration_obj.setting = form.setting.data
        purge_data_duration_obj.update(purge_data_duration_obj)
        # create_tags(*form.value.data.splitlines())
        print(request)
        return redirect(url_for('manage.update_purge'))
    purge_data_duration = 1
    purge_data_duration_obj = Settings.query.filter(Settings.name == 'purge_data_duration').first()
    if purge_data_duration_obj:
        purge_data_duration = purge_data_duration_obj.setting
    flash_errors(form)

    return render_template('/forms/purge.html', form=form, setting=None,
                           purge_data_duration=purge_data_duration)


@blueprint.route('/tags/add', methods=['GET', 'POST'])
@login_required
def add_tag():
    form = CreateTagForm()
    if form.validate_on_submit():
        create_tags(*form.value.data.splitlines())
        return redirect(url_for('manage.tags'))
        flash(u"Successfully created tag", 'success')

    flash_errors(form)
    return render_template('tag.html', form=form)


@blueprint.route('/tag/<string:tag_value>')
@login_required
def get_tag(tag_value):
    tag = Tag.query.filter(Tag.value == tag_value).first_or_404()
    return render_template('tag.html', tag=tag)


@blueprint.route('/tag/<string:tag_value>', methods=['DELETE'])
@login_required
def delete_tag(tag_value):
    tag = Tag.query.filter(Tag.value == tag_value).first_or_404()
    tag.delete()
    return jsonify({}), 204


def create_tags(*tags):
    values = []
    existing = []

    # create a set, because we haven't yet done our association_proxy in
    # sqlalchemy

    for value in (v.strip() for v in set(tags) if v.strip()):
        tag = Tag.query.filter(Tag.value == value).first()
        if not tag:
            values.append(Tag.create(value=value))
        else:
            existing.append(tag)
    return values + existing


def get_tags(*tags):
    values = []
    existing = []

    # create a set, because we haven't yet done our association_proxy in
    # sqlalchemy

    for value in (v.strip() for v in set(tags) if v.strip()):
        tag = Tag.query.filter(Tag.value == value).first()
        if tag:
            existing.append(tag)
    return existing


@blueprint.route('/rules')
@login_required
def rules():
    rules = Rule.query.order_by(Rule.name).all()
    return render_template('rules.html', rules=rules)


@blueprint.route('/rules/add', methods=['GET', 'POST'])
@login_required
def add_rule():
    form = CreateRuleForm()
    form.set_choices()

    if form.validate_on_submit():
        alerters = form.alerters.data
        if not 'debug' in alerters:
            alerters.append('debug')
        rule = Rule(name=form.name.data,
                    alerters=alerters,
                    description=form.description.data,
                    conditions=form.conditions.data,
                    status=form.status.data,
                    type=form.type.data,
                    tactics=form.tactics.data,
                    technique_id=form.technique_id.data,
                    updated_at=dt.datetime.utcnow(), recon_queries=form.recon_queries.data, severity=form.severity.data)
        rule.save()
        flash(u"Successfully created rule", 'success')

        return redirect(url_for('manage.rule', rule_id=rule.id))

    flash_errors(form)
    return render_template('rule.html', form=form)


@blueprint.route('/yara/list', methods=['GET', 'POST'])
@login_required
def yara_list():
    from os import walk
    from .forms import UploadYARAForm

    file_list = []
    for (dirpath, dirnames, filenames) in walk(PolyLogyxServerDefaults.BASE_URL + "/yara"):
        if 'list.txt' in filenames:
            filenames.remove("list.txt")
        file_list.extend(filenames)
        break
    form = UploadYARAForm()

    return render_template('directory_list.html', file_list=file_list, form=form)


@blueprint.route('/yara/add', methods=['DELETE', 'POST'])
@login_required
def yara_add():
    from .forms import UploadYARAForm
    form = UploadYARAForm()
    if form.validate_on_submit():
        print("form data is", form.yara.data)
        file_path = PolyLogyxServerDefaults.BASE_URL + "/yara/" + form.yara.data.filename.lower()
        if os.path.isfile(file_path):
            flash(u"This file already exists ", 'danger')
        else:
            form.yara.data.save(file_path, 1000)
            files = os.listdir(PolyLogyxServerDefaults.BASE_URL + "/yara/")
            with open(PolyLogyxServerDefaults.BASE_URL + '/yara/' + 'list.txt', 'w+') as the_file:
                for file_name in files:
                    if file_name != 'list.txt':
                        the_file.write(file_name + '\n')
            flash(u"Successfully Uploaded the file : " + form.yara.data.filename.lower(), 'success')
    else:
        flash(u"Please select a yara file for upload", 'danger')

    return redirect(url_for('manage.yara_list'))


@blueprint.route('/yara/delete', methods=['POST'])
@login_required
def yara_delete():
    file_name = request.form.get('file_name')
    response = {'status': 'failure', 'message': 'Cannot delete the file'}
    file_path = PolyLogyxServerDefaults.BASE_URL + "/yara/" + file_name.lower()
    if os.path.exists(file_path):
        os.remove(file_path)
        files = os.listdir(PolyLogyxServerDefaults.BASE_URL + "/yara/")
        with open(PolyLogyxServerDefaults.BASE_URL + '/yara/' + 'list.txt', 'w+') as the_file:
            for file_name in files:
                if file_name != 'list.txt':
                    the_file.write(file_name + '\n')
        response['status'] = 'success'
        response['message'] = "Successfully Deleted the file : " + file_name.lower()

        flash(u"Successfully Deleted the file : " + file_name.lower(), 'success')
    else:
        flash(file_name + u" file file does not exist", 'danger')
        response['message'] = "Cannot delete the file : " + file_name.lower()

    return jsonify(response)


@blueprint.route('/yara/view/<string:file_name>', methods=['GET'])
@login_required
def yara_view(file_name):
    response = {'status': 'failure', 'message': 'Cannot read the file'}
    file_path = PolyLogyxServerDefaults.BASE_URL + "/yara/" + file_name.lower()
    data = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as the_file:
            data = the_file.read()
            return data
        response['data'] = data
        response['status'] = 'success'
        response['message'] = 'Successfully read the file'

    return jsonify(response)


def prepare_intel_data():
    data = {}
    intel_feeds = db.session.query(IOCIntel.threat_name, IOCIntel.value, IOCIntel.type,
                                   IOCIntel.severity).filter(IOCIntel.intel_type == 'self').order_by(
        IOCIntel.threat_name).all()
    for r in intel_feeds:
        if not r[0] in data:
            data[r[0]] = {"values": [], "type": r[2], "severity": r[3]}
        data[r[0]]["values"].append(r[1])

    intel_data = {}
    if not data:
        data = {
            "test-intel_ipv4": {
                "type": "remote_address",
                "values": [
                    "3.30.1.15",
                    "3.30.1.16"
                ],
                "severity": "WARNING"
            },
            "test-intel_domain_name": {
                "type": "domain_name",
                "values": [
                    "unknown.com",
                    "slackabc.com"
                ],
                "severity": "WARNING"
            },
            "test-intel_md5": {
                "type": "md5",
                "values": [
                    "3h8dk0sksm0",
                    "9sd772ndd80"
                ],
                "severity": "INFO"
            }
        }
    intel_data['data'] = data
    return intel_data


@blueprint.route('/intel/add', methods=['GET', 'POST'])
@login_required
def upload_intel():
    form = UploadIntelForm()

    if form.validate_on_submit():
        try:
            intel = json.loads(form.intel.data)
            data = intel['data']
            IOCIntel.query.filter(IOCIntel.intel_type == 'self').delete()

            for intel_name, values in data.items():
                for value in values['values']:
                    IOCIntel.create(intel_type='self', type=values['type'], value=value,
                                    severity=values['severity'], threat_name=intel_name)
            flash(u"Successfully updated the intel", 'success')
        except Exception as e:
            flash('Invalid JSON format', 'danger')
            return redirect(url_for('manage.upload_intel'))

        return redirect(url_for('manage.upload_intel'))

    flash_errors(form)

    intel_data = prepare_intel_data()

    intel_data = json.dumps(intel_data)
    return render_template('upload_intel.html', form=form, intel_data=intel_data)


@blueprint.route('/downloads/<path:filename>', methods=['GET'])
def download(filename):
    if filename is None:
        current_app.logger.error('Error')
        # self.Error(400)
    try:
        return send_from_directory(directory=PolyLogyxServerDefaults.BASE_URL + '/resources/', as_attachment=True,
                                   filename=filename,
                                   cache_timeout=-1)
    except Exception as e:
        current_app.logger.error(e)


@blueprint.route('/rules/<int:rule_id>', methods=['GET', 'POST'])
@login_required
def rule(rule_id):
    rule = Rule.query.filter(Rule.id == rule_id).first_or_404()
    form = UpdateRuleForm(request.form)

    if form.validate_on_submit():
        alerters = form.alerters.data
        if not 'debug' in alerters:
            alerters.append('debug')

        rule = rule.update(name=form.name.data,
                           alerters=alerters,
                           description=form.description.data,
                           conditions=form.conditions.data,
                           status=form.status.data,
                           type=form.type.data,
                           tactics=form.tactics.data,
                           technique_id=form.technique_id.data,
                           updated_at=dt.datetime.utcnow(), recon_queries=form.recon_queries.data,
                           severity=form.severity.data)
        flash(u"Successfully updated the rule", 'success')

        return redirect(url_for('manage.rule', rule_id=rule.id))

    form = UpdateRuleForm(request.form, obj=rule)
    flash_errors(form)
    return render_template('rule.html', form=form, rule=rule)


@blueprint.route('/ajax/rule/get_tactics', methods=['GET', 'POST'])
@login_required
def get_technique_details():
    mitreApi = MitreApi()
    technique_id = request.form.get("technique_ids")
    tactics_with_description = mitreApi.get_tactics_by_technique_id(technique_id.split(","))
    data = {}
    data['status'] = 'success'
    data['data'] = tactics_with_description

    return jsonify(data)


@blueprint.route('/search', methods=['GET', 'POST'])
@blueprint.route('/search/<int:page>', methods=['GET', 'POST'])
@login_required
def search_column(page=1):
    all_columns = ['hotfix_id', 'product_name', 'product_signatures', 'product_state', 'product_type', 'target_path',
                   'hostnames',
                   'common_name', 'issuer', 'md5', 'domain_name', 'url', 'sha1', 'path', 'process_name',
                   'parent_path', 'issuer_name']
    filter_columns = {}

    for column in all_columns:
        filter_columns[column] = column

    filter_columns['kernel_version'] = 'version'
    filter_columns['chrome_identifier'] = 'identifier'
    filter_columns['program_name'] = 'name'

    return render_template('search.html', filter_columns=filter_columns, form=CreateSearchForm())


def make_condition(klass, *args, **kwargs):
    """
        Memoizing constructor for conditions.  Uses the input config as the cache key.
        """
    conditions = {}
    alert_conditions = []

    # Calculate the memoization key.  We do this by creating a 3-tuple of
    # (condition class name, args, kwargs).  There is some nuance to this,
    # though: we need to put args/kwargs in the right format.  We
    # recursively iterate through lists/dicts and convert them to tuples,
    # and extract the memoization key from instances of BaseCondition.
    def tupleify(obj):
        if isinstance(obj, BaseCondition):
            return obj.__network_memo_key
        elif isinstance(obj, tuple):
            return tuple(tupleify(x) for x in obj)
        elif isinstance(obj, list):
            return tuple(tupleify(x) for x in obj)
        elif isinstance(obj, dict):
            items = ((tupleify(k), tupleify(v)) for k, v in obj.items())
            return tuple(sorted(items))
        else:
            return obj

    args_tuple = tupleify(args)
    kwargs_tuple = tupleify(kwargs)

    key = (klass.__name__, args_tuple, kwargs_tuple)
    if key in conditions:
        return conditions[key]

    # Instantiate the condition class.  Also, save the memoization key on
    # the class, so it can be retrieved (above).
    inst = klass(*args, **kwargs)
    inst.__network_memo_key = key

    # Save the condition
    conditions[key] = inst
    return inst


def parse_query(query, alerters=None, rule_id=None):
    """
        Parse a query output from jQuery.QueryBuilder.
        """


def parse_condition(d):
    op = d['operator']
    value = d['value']

    column_name = d['field']

    klass = OPERATOR_MAP.get(op)
    if not klass:
        raise ValueError("Unsupported operator: {0}".format(op))

    inst = make_condition(klass, d['field'], value, column_name=column_name)
    return inst


def parse_group(d):
    if len(d['rules']) == 0:
        raise ValueError("A group contains no rules")

    upstreams = [parse(r) for r in d['rules']]

    condition = d['condition']
    if condition == 'AND':
        return make_condition(AndCondition, upstreams)
    elif condition == 'OR':
        return make_condition(OrCondition, upstreams)

    raise ValueError("Unknown condition: {0}".format(condition))


def parse(d):
    if 'condition' in d:
        return parse_group(d)

    return parse_condition(d)

    # The root is always a group


def get_platform_filter(platform):
    from sqlalchemy import and_
    filter = []
    if platform == 'linux':
        filter.append(~Node.platform.in_(('windows', 'darwin')))
    else:
        filter.append(Node.platform == platform)
    return and_(*filter)


def prepare_filter(data):
    from sqlalchemy import and_

    filter = []
    column_filters = data['filters']
    for key, value in column_filters.items():
        filter.append(NodeReconData.columns[key].astext.ilike("%" + value + "%"))
    return and_(*filter)


def prepare_result_log_filter(data):
    from sqlalchemy import and_

    filter = []
    column_filters = data['filters']
    for key, value in column_filters.items():
        filter.append(ResultLog.columns[key].astext.ilike("%" + value + "%"))
    return and_(*filter)


@blueprint.route('/ajax/search', methods=['GET', 'POST'])
@blueprint.route('/search/<int:page>', methods=['GET', 'POST'])
@login_required
def search(page=1):
    rules = request.form.get('conditions')

    conditions = json.loads(rules)
    root = parse_group(conditions)
    root_recon = parse_group(conditions)

    filter = root.run('', [], 'result_log')
    filter_node_recon = root_recon.run('s', [], 'node_recon_data')
    node_data_query_results = db.session.query(NodeReconData).join(
        NodeData, NodeReconData.node_data).options(
        db.lazyload('*'),
        db.contains_eager(NodeReconData.node_data),
    ).with_entities(NodeData.node_id, NodeData.name).filter(
        *filter_node_recon).group_by(NodeData.node_id, NodeData.name).all()

    results = db.session.query(ResultLog.node_id, ResultLog.name).filter(*filter).group_by(ResultLog.node_id,
                                                                                           ResultLog.name).all()
    node_search_data = {}
    for r in node_data_query_results:

        if not r[0] in node_search_data:
            node_search_data[r[0]] = {}
        if not r[1] in node_search_data[r[0]]:
            node_search_data[r[0]][r[1]] = {"type": "node_data"}

    for r in results:
        if not r[0] in node_search_data:
            node_search_data[r[0]] = {}
        if not r[1] in node_search_data[r[0]]:
            node_search_data[r[0]][r[1]] = {"type": "scheduled_data"}

    nodes = {}
    nodes_obj = Node.query.all()
    for node in nodes_obj:
        nodes[node.id] = node.display_name
    data = {}
    data['node_search_data'] = node_search_data
    data['nodes'] = nodes
    return jsonify(data)


@blueprint.route('/ajax/indicator/search', methods=['GET', 'POST'])
@login_required
def indicator_search(page=1):
    form_data = request.form.to_dict(flat=False)
    search_column = form_data.get('search_column')

    indicators = form_data.get('indicators')[0].split(',')
    print(indicators)
    results = db.session.query(ResultLog.node_id, ResultLog.name).filter(
        ResultLog.columns[search_column].astext.in_(indicators)).group_by(ResultLog.node_id,
                                                                          ResultLog.name).all()
    node_search_data = {}

    for r in results:
        if not r[0] in node_search_data:
            node_search_data[r[0]] = {}
        if not r[1] in node_search_data[r[0]]:
            node_search_data[r[0]][r[1]] = {"type": "scheduled_data"}

    nodes = {}
    nodes_obj = Node.query.all()
    for node in nodes_obj:
        nodes[node.id] = node.display_name
    data = {}
    data['node_search_data'] = node_search_data
    data['nodes'] = nodes
    return jsonify(data)


@blueprint.route('/ajax/indicator/node/query/search', methods=['GET', 'POST'])
@blueprint.route('/search/<int:page>', methods=['GET', 'POST'])
@login_required
def get_node_filtered_indicator_data():
    name = request.form.get('name')
    node_id = request.form.get('node_id')
    search_column = request.form.get('search_column')
    indicators = request.form.get('indicators').split(',')
    results = get_node_filtered_results_by_query_indicators(0, 50, node_id, name, search_column, indicators)
    return jsonify(results)


def get_node_filtered_results_by_query_indicators(startPage, perPageRecords, node_id, name, search_column, indicators):
    columns = []
    columnsDefined = False
    try:
        startPage = int(request.values['start'])
        perPageRecords = int(request.values['length'])
        if (request.values['columns[0][data]']):
            columnsDefined = True
    except:
        print('error in request')
    results = []

    countFiltered = 0

    queryCount = db.session.query(db.func.count(ResultLog.node_id)) \
        .filter(ResultLog.name == name) \
        .filter(ResultLog.node_id == int(node_id)) \
        .filter(
        ResultLog.columns[search_column].astext.in_(indicators)
    ).all()

    for r in queryCount:
        countFiltered = r[0]

    queryStrList = db.session.query(ResultLog.columns) \
        .filter(ResultLog.name == name) \
        .filter(ResultLog.node_id == int(node_id)) \
        .filter(
        ResultLog.columns[search_column].astext.in_(indicators)
    ).offset(startPage).limit(
        perPageRecords).all()

    for r in queryStrList:
        results.append(r[0])
    count = countFiltered
    firstRecord = results[0]

    for key in firstRecord.keys():
        columns.append({'data': key, 'title': key})

    output = {}
    try:
        output['sEcho'] = str(int(request.values['sEcho']))
    except:
        print('error in echo')
    output['iRecordsFiltered'] = str(countFiltered)
    output['iTotalRecords'] = str(count)
    output['pageLength'] = str(perPageRecords)

    output['iTotalDisplayRecords'] = str(countFiltered)
    aaData_rows = results

    if not columnsDefined:
        output['columns'] = columns
    output['aaData'] = aaData_rows

    return output


@blueprint.route('/ajax/node/query/search', methods=['GET', 'POST'])
@blueprint.route('/search/<int:page>', methods=['GET', 'POST'])
@login_required
def get_node_filtered_data_data():
    name = request.form.get('name')
    node_id = request.form.get('node_id')

    type = request.form.get('type')
    rules = request.form.get('conditions')
    conditions = json.loads(rules)
    results = get_node_filtered_results_by_query(0, 50, node_id, name, type, conditions)
    return jsonify(results)


def get_data_for_search_to_csv(conditions, name, node_id, type):
    root = parse_group(conditions)
    root_recon = parse_group(conditions)
    filter = root.run(root, [], 'result_log')
    filter_node_recon = root_recon.run('s', [], 'node_recon_data')

    if type == 'node_data':
        queryStrList = db.session.query(NodeReconData).join(
            NodeData, NodeReconData.node_data).options(
            db.lazyload('*'),
            db.contains_eager(NodeReconData.node_data),
        ) \
            .with_entities(NodeReconData.columns) \
            .filter(NodeData.name == name) \
            .filter(NodeData.node_id == int(node_id)) \
            .filter(
            *filter_node_recon
        ).all()
    else:
        queryStrList = db.session.query(ResultLog.columns) \
            .filter(ResultLog.name == name) \
            .filter(ResultLog.node_id == int(node_id)) \
            .filter(
            *filter
        ).all()

    return queryStrList


@blueprint.route('/ajax/search/export/csv', methods=['POST'])
def get_search_csv_data():
    name = request.form.get('name')
    node_id = request.form.get('node_id')

    rules = request.form.get('conditions')
    type = request.form.get('type')
    conditions = json.loads(rules)
    queryStrList = get_data_for_search_to_csv(conditions, name, node_id, type)

    results = [r for r, in queryStrList]
    headers = []
    if results:
        firstRecord = results[0]
        headers = []
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

    response = send_file(
        bio,
        mimetype='text/csv',
        as_attachment=True,
        attachment_filename='search_results.csv'
    )
    return response


def get_node_hunt_results_through_indicators(node_id, name, search_column, indicators):
    queryStrList = db.session.query(ResultLog.columns) \
        .filter(ResultLog.name == name) \
        .filter(ResultLog.node_id == int(node_id)) \
        .filter(
        ResultLog.columns[search_column].astext.in_(indicators)
    ).all()

    return queryStrList


@blueprint.route('/ajax/hunt/search/csv', methods=['POST'])
def get_node_hunt_filtered_indicator_data():
    name = request.form.get('name')
    node_id = request.form.get('node_id')
    search_column = request.form.get('search_column')
    indicators = request.form.get('indicators').split(',')
    queryStrList = get_node_hunt_results_through_indicators(node_id, name, search_column, indicators)

    results = [r for r, in queryStrList]
    headers = []
    if results:
        firstRecord = results[0]
        headers = []
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

    response = send_file(
        bio,
        mimetype='text/csv',
        as_attachment=True,
        attachment_filename='hunt_search_results.csv'
    )
    return response


def get_node_filtered_results_by_query(startPage, perPageRecords, node_id, name, type, conditions):
    columns = []
    columnsDefined = False
    try:
        startPage = int(request.values['start'])
        perPageRecords = int(request.values['length'])
        if (request.values['columns[0][data]']):
            columnsDefined = True
    except:
        print('error in request')
    results = []

    root = parse_group(conditions)
    root_recon = parse_group(conditions)

    filter = root.run(root, [], 'result_log')
    filter_node_recon = root_recon.run('s', [], 'node_recon_data')

    countFiltered = 0
    if type == 'node_data':

        queryCount = db.session.query(NodeReconData).join(
            NodeData, NodeReconData.node_data).options(
            db.lazyload('*'),
            db.contains_eager(NodeReconData.node_data),
        ) \
            .with_entities(db.func.count(NodeReconData.id)) \
            .filter(NodeData.name == name) \
            .filter(NodeData.node_id == int(node_id)) \
            .filter(
            *filter_node_recon
        ).all()

        for r in queryCount:
            countFiltered = r[0]
    else:
        queryCount = db.session.query(db.func.count(ResultLog.node_id)) \
            .filter(ResultLog.name == name) \
            .filter(ResultLog.node_id == int(node_id)) \
            .filter(
            *filter
        ).all()

        for r in queryCount:
            countFiltered = r[0]

    if type == 'node_data':
        queryStrList = db.session.query(NodeReconData).join(
            NodeData, NodeReconData.node_data).options(
            db.lazyload('*'),
            db.contains_eager(NodeReconData.node_data),
        ) \
            .with_entities(NodeReconData.columns) \
            .filter(NodeData.name == name) \
            .filter(NodeData.node_id == int(node_id)) \
            .filter(
            *filter_node_recon
        ).offset(startPage).limit(
            perPageRecords).all()
    else:

        queryStrList = db.session.query(ResultLog.columns) \
            .filter(ResultLog.name == name) \
            .filter(ResultLog.node_id == int(node_id)) \
            .filter(
            *filter
        ).offset(startPage).limit(
            perPageRecords).all()

    for r in queryStrList:
        results.append(r[0])
    count = countFiltered
    firstRecord = results[0]

    for key in firstRecord.keys():
        columns.append({'data': key, 'title': key})

    output = {}
    try:
        output['sEcho'] = str(int(request.values['sEcho']))
    except:
        print('error in echo')
    output['iRecordsFiltered'] = str(countFiltered)
    output['iTotalRecords'] = str(count)
    output['pageLength'] = str(perPageRecords)

    output['iTotalDisplayRecords'] = str(countFiltered)
    aaData_rows = results

    if not columnsDefined:
        output['columns'] = columns
    output['aaData'] = aaData_rows

    return output


def distributed_form():
    form = AddDistributedQueryForm()
    form.set_choices()

    if form.validate_on_submit():
        nodes = []

        if not form.nodes.data and not form.tags.data:
            # all nodes get this query
            nodes = Node.query.all()

        if form.nodes.data:
            nodes.extend(
                Node.query.filter(
                    Node.node_key.in_(form.nodes.data)
                ).all()
            )

        if form.tags.data:
            nodes.extend(
                Node.query.filter(
                    Node.tags.any(
                        Tag.value.in_(form.tags.data)
                    )
                ).all()
            )

        query = DistributedQuery.create(sql=form.sql.data,
                                        description=form.description.data,
                                        not_before=form.not_before.data)

        for node in nodes:
            task = DistributedQueryTask(node=node, distributed_query=query)
            db.session.add(task)
        else:
            db.session.commit()

        return form

    return form


@blueprint.route('/ajax/queries/distributed/add', methods=['POST'])
# @login_required
def submit_distributed():
    form = AddDistributedQueryForm()
    form.set_choices()
    onlineNodes = 0
    sql = ''

    if form.validate_on_submit():
        nodes = []

        if not form.nodes.data and not form.tags.data:
            # all nodes get this query
            form.errors['sql'] = 'No host selected'
            return jsonify(errors=form.errors)

        if form.nodes.data:
            nodes.extend(
                Node.query.filter(
                    Node.node_key.in_(form.nodes.data)
                ).all()
            )

        if form.tags.data:
            nodes.extend(
                Node.query.filter(
                    Node.tags.any(
                        Tag.value.in_(form.tags.data)
                    )
                ).all()
            )
        query = DistributedQuery.create(sql=form.sql.data,
                                        description=form.description.data,
                                        not_before=form.not_before.data)
        win_sql_query = None

        typed_query = query.sql
        query_windows_specific = False
        if ('win_file_events' in query.sql or 'win_process_events' in query.sql):
            win_sql_query = typed_query
            query_windows_specific = True

        for node in nodes:
            # send only to active nodes
            if node_is_active(node):
                onlineNodes += 1
                task = DistributedQueryTask(node=node, distributed_query=query)
                if node.platform == 'windows':
                    task.sql = win_sql_query
                if not (node.platform != 'windows' and query_windows_specific):
                    db.session.add(task)
        else:
            db.session.commit()

    # flash_errors(form)
    if bool(form.errors):
        return jsonify(errors=form.errors)
    elif onlineNodes == 0:
        form.errors['sql'] = 'No active host present'
        return jsonify(errors=form.errors)
    else:
        return jsonify(errors=form.errors, id=query.id, onlineNodes=onlineNodes, sql=sql)


@blueprint.route('/ajax/distributedquerytask/update/<string:guid>', methods=['POST'])
@login_required
def update_last_viewed_timeDQ(guid):
    task = DistributedQueryTask.query.filter(DistributedQueryTask.guid == guid).first_or_404()
    task.viewed_at = dt.datetime.utcnow()
    db.session.add(task)
    db.session.commit()


def get_active_inactive_nodes_count():
    nodes = {}

    q = get_os_count()
    get_active_inactive_os_count(nodes)
    current_time = dt.datetime.utcnow()
    checkin_interval = current_app.config['POLYLOGYX_CHECKIN_INTERVAL']
    current_time = current_time - checkin_interval
    offline_nodes = db.session.query(db.func.count(Node.id)).filter(
        Node.last_checkin < current_time).scalar()
    nodes['offline_nodes'] = offline_nodes
    online_nodes = db.session.query(db.func.count(Node.id)).filter(
        Node.last_checkin > current_time).scalar()
    nodes['online_nodes'] = online_nodes
    nodes['linux'] = 0
    for tuple in q:
        count = tuple[1]
        if tuple[0] == 'linux':
            nodes['linux'] = count
        elif tuple[0] == 'centos':
            nodes['linux'] = nodes['linux'] + count
        elif tuple[0] == 'ubuntu':
            nodes['linux'] = nodes['linux'] + count
        elif tuple[0] == 'debian':
            nodes['linux'] = nodes['linux'] + count
        elif tuple[0] == 'freebsd':
            nodes['linux'] = nodes['linux'] + count
        elif tuple[0] == 'darwin':
            nodes['darwin'] = count
        elif tuple[0] == 'windows':
            nodes['windows'] = count

    return nodes


def get_active_inactive_os_count(nodes):
    current_time = dt.datetime.utcnow()
    checkin_interval = current_app.config['POLYLOGYX_CHECKIN_INTERVAL']
    current_time = current_time - checkin_interval
    baseQuery = db.session.query(db.func.count(Node.platform))
    offline_nodes_darwin = baseQuery.filter(and_(
        Node.last_checkin < current_time, Node.platform == 'darwin')).scalar()
    online_nodes_darwin = baseQuery.filter(
        and_(
            Node.last_checkin > current_time, Node.platform == 'darwin')).scalar()
    offline_nodes_windows = baseQuery.filter(and_(
        Node.last_checkin < current_time, Node.platform == 'windows')).scalar()
    online_nodes_windows = baseQuery.filter(and_(
        Node.last_checkin > current_time, Node.platform == 'windows')).scalar()

    offline_nodes_linux = baseQuery.filter(
        Node.last_checkin < current_time).filter(Node.platform != 'windows').filter(
        Node.platform != 'darwin').scalar()
    online_nodes_linux = baseQuery.filter(
        Node.last_checkin > current_time).filter(Node.platform != 'windows').filter(
        Node.platform != 'darwin').scalar()
    nodes['darwin_online'] = online_nodes_darwin
    nodes['darwin_offline'] = offline_nodes_darwin

    nodes['windows_online'] = online_nodes_windows
    nodes['windows_offline'] = offline_nodes_windows

    nodes['linux_online'] = online_nodes_linux
    nodes['linux_offline'] = offline_nodes_linux


def get_os_count():
    return db.session.query(
        Node.platform, db.func.count(Node.platform)
    ).group_by(
        Node.platform
    ).all()


def node_is_active(node):
    checkin_interval = current_app.config['POLYLOGYX_CHECKIN_INTERVAL']
    if isinstance(checkin_interval, (int, float)):
        checkin_interval = dt.timedelta(seconds=checkin_interval)
    if (dt.datetime.utcnow() - node.last_checkin) < checkin_interval:
        return True
    return False


@blueprint.route("/ajax/<int:node_id>/queries/result", methods=['POST'])
@login_required
def get_server_data(node_id):
    name = request.form.get('name')
    results = get_results_by_query(0, 50, node_id, name)
    return jsonify(results)


@blueprint.route('/node/<int:node_id>/queryResult')
@login_required
def get_query_results(node_id):
    startPage = 1
    perPageRecords = 100
    nameResult = {}
    names = db.session.query(
        ResultLog.name).distinct(ResultLog.name). \
        filter(ResultLog.node_id == (node_id)). \
        all()
    for name in names:
        nameResult[name[0]] = get_results_by_query(startPage, perPageRecords, node_id, name[0])
    return nameResult


@blueprint.route('/alerts')
@login_required
def alerts():
    """ Display all distinct source in alerts page. """
    try:

        alert_source_tuple_list = db.session.query(Alerts).with_entities(Alerts.source).filter(
            or_(Alerts.status == None, Alerts.status != Alerts.RESOLVED)).order_by(
            Alerts.source).distinct(Alerts.source).all()
        alert_source = [alert_source_tuple[0] for alert_source_tuple in alert_source_tuple_list]

        alerts_severity = db.session.query(Alerts).with_entities(Alerts.id, Alerts.severity, Alerts.created_at).filter(
            or_(Alerts.status == None, Alerts.status != Alerts.RESOLVED)).all()

        return render_template('alertbysource.html', alert_source=alert_source)
    except Exception as e:
        print(e, 'error in request')


@blueprint.route('/ajax/alerts/update-status', methods=['POST'])
@login_required
def update_alert_status():
    """ Display all distinct source in alerts page. """
    alert_ids = request.form.get('alert_ids').split(',')
    response = {}
    source = request.form.get('source')
    for i in range(0, len(alert_ids)):
        alert_ids[i] = int(alert_ids[i])
    try:
        db.session.query(Alerts).filter(Alerts.id.in_(alert_ids)).update({Alerts.status: Alerts.RESOLVED},
                                                                         synchronize_session=False)
        results = db.session.query(db.func.count(Alerts.id)).filter(Alerts.source == source).filter(
            or_(Alerts.status == None, Alerts.status != Alerts.RESOLVED)).all()
        count = results[0][0]
        db.session.commit()
        response['status'] = 'success'
        response['data'] = {'count': count}
        return jsonify(response)

    except Exception as e:
        print(e, 'error in request')
    response['status'] = 'failure'
    return jsonify(response)


def get_results_by_alert_source(startPage, perPageRecords, source):
    filter_non_resolved_alerts = or_(Alerts.status == None, Alerts.status != Alerts.RESOLVED)
    """ Alerts by source Result Set  using server side render for ajax datatable. """
    results, columns, columnsDefined, searchTerm = [], [], False, None

    columns, searchTerm = [], None
    columnsDefined = False
    col_names = {'0': 'Alerts.node_id', '1': 'Alerts.severity', '2': 'Alerts.created_at',
                 '3': 'Alerts.source_data',
                 '4': 'Alerts.message', '5': 'Alerts.status'}
    if source == 'rule':
        col_names['3'] = 'Rule.name'

    try:
        col_name = col_names[request.values['order[0][column]']]
        col_order = request.values['order[0][dir]']
    except Exception as e:
        col_name = 'Alerts.id'
        col_order = 'desc'
        print(e)
    try:
        startPage = int(request.form["pagination[page]"])
        perPageRecords = int(request.form["pagination[perpage]"])
        search_field_name = 'query[generalSearch_' + source + ']'
        if search_field_name in request.values and (request.values[search_field_name] != ""):
            searchTerm = (request.values[search_field_name])
        if (request.values['columns[0][data]']):
            columnsDefined = True

    except:
        pass
    if startPage > 0:
        startPage = startPage - 1

    count = db.session.query(Alerts).filter(
        (Alerts.source == source)).filter(filter_non_resolved_alerts).count()
    countFiltered = count

    if searchTerm:
        countFiltered = db.session.query(Alerts, Rule, Node).filter(Alerts.source == source
                                                                    ).filter(filter_non_resolved_alerts).filter(or_(
            Alerts.severity.ilike('%' + searchTerm + '%'),
            Node.node_info['computer_name'].astext.ilike('%' + searchTerm + '%'),
            Rule.name.ilike('%' + searchTerm + '%'),
            cast(Alerts.created_at, sqlalchemy.String).ilike('%' + searchTerm + '%')
        )
        ).join(Rule, Alerts.rule_id == Rule.id).join(Node, Alerts.node_id == Node.id).count()

        record_query = db.session.query(Alerts, Rule, Node).filter(filter_non_resolved_alerts).filter(
            Alerts.source == source
        ).filter(or_(
            Alerts.severity.ilike('%' + searchTerm + '%'),
            Node.node_info['computer_name'].astext.ilike('%' + searchTerm + '%'),
            Rule.name.ilike('%' + searchTerm + '%'),
            cast(Alerts.created_at, sqlalchemy.String).ilike('%' + searchTerm + '%')
        )
        ).join(Rule, Alerts.rule_id == Rule.id).join(Node, Alerts.node_id == Node.id).order_by(
            desc(Alerts.id)).offset(startPage * perPageRecords).limit(perPageRecords).all()

        for value in record_query:
            res = {}
            nName = value.Node.display_name
            nID = value.Node.id
            res['Host'] = {'name': nName, 'id': nID}
            res['Severity'] = value.Alerts.severity
            res['Created At'] = str(value.Alerts.created_at)
            res['Investigate the alert'] = value.Alerts.id
            if source == 'rule':
                rID = value.Rule.id
                rName = value.Rule.name
                res['Rule Name'] = {'name': rName, 'id': rID}
            elif source == 'self' or (source == 'IOC' or source == 'ioc'):
                pass
            else:
                res['Intel Data'] = value.Alerts.source_data
            res['Alerted Entry'] = value.Alerts.message

            res['Status'] = value.Alerts.id

            results.append(res)
    else:
        if col_order == 'desc':
            record_query = db.session.query(Alerts).filter(filter_non_resolved_alerts).filter(
                Alerts.source == source).order_by(desc(col_name)).offset(startPage * perPageRecords).limit(
                perPageRecords).all()
        else:
            record_query = db.session.query(Alerts).filter(filter_non_resolved_alerts).filter(
                Alerts.source == source).order_by(asc(col_name)).offset(startPage * perPageRecords).limit(
                perPageRecords).all()

        for value in record_query:
            res = {}
            data = value.to_dict()
            nName = value.node.display_name
            nId = data["node_id"]
            res['Host'] = {'name': nName, 'id': nId}
            res['Severity'] = data["severity"]
            res['Created At'] = str(data["created_at"])

            if source == 'rule':
                rID = value.rule.id
                rName = value.rule.name
                res['Rule Name'] = {'name': rName, 'id': rID}
            elif source == 'self' or (source == 'IOC' or source == 'ioc'):
                pass
            else:
                res['Intel Data'] = data["source_data"]
            res['Alerted Entry'] = data["message"]

            res['Status'] = value.id

            results.append(res)

    try:
        firstRecord = results[0]
        for key in firstRecord.keys():
            columns.append({'data': key, 'title': key})
    except Exception as e:
        print(e, "No matching records found")

    output = {}
    try:
        output['sEcho'] = str(int(request.values['sEcho']))
    except:
        pass  # print('error in echo')

    meta = {}

    meta['total'] = countFiltered
    meta['perpage'] = perPageRecords
    meta['pages'] = int(count / perPageRecords)
    meta['page'] = 1
    try:
        meta['perpage'] = request.form["pagination[perpage]"]
        meta['page'] = request.form["pagination[page]"]
    except:
        pass

    output['meta'] = meta
    aaData_rows = results

    if not columnsDefined:
        output['columns'] = columns
    output['data'] = aaData_rows

    return output


@blueprint.route('/ajax/alerts', methods=['POST'])
@login_required
def alerts_source():
    """ Display Alerts by source table content. """
    source = request.form['source']

    if request.method == 'POST':
        results = get_results_by_alert_source(0, 10, source)
        return jsonify(results)
    return jsonify({'error': 'Missing data!'})


def get_results_by_query(startPage, perPageRecords, node_id, name):
    searchTerm = None
    columns = []
    columnsDefined = False
    try:
        startPage = int(request.values['start'])
        perPageRecords = int(request.values['length'])
        if 'search[value]' in request.values and (request.values['search[value]'] != ""):
            searchTerm = (request.values['search[value]'])
        if (request.values['columns[0][data]']):
            columnsDefined = True
    except:
        print('error in request')
    results = []
    count = db.session.query(ResultLog).filter(
        and_(ResultLog.name == name, and_(ResultLog.node_id == node_id, ResultLog.action != 'removed'))).count()
    countFiltered = count

    if searchTerm:
        queryCountStr = "select count(distinct id) from result_log join jsonb_each_text(result_log.columns) e on true where  node_id='" + str(
            node_id) + "' and e.value ilike " + "'%" + searchTerm + "%'" + " and name=" + "'" + name + "'" + " and action!='removed'"

        filtered_quer = db.engine.execute(sqlalchemy.text(queryCountStr))
        for r in filtered_quer:
            countFiltered = r[0]

        queryStr = "select distinct id,columns from result_log join jsonb_each_text(result_log.columns) e on true where  node_id='" + str(
            node_id) + "' and e.value ilike " + "'%" + searchTerm + "%'" + " and name=" + "'" + name + "'" + " and action!='removed' order by id desc OFFSET " + str(
            startPage) + "  LIMIT " + str(perPageRecords);
        record_query = db.engine.execute(sqlalchemy.text(queryStr))
        for r in record_query:
            r[1]['data'] = json.dumps(r[1])
            results.append(r[1])

    else:
        record_query = db.session.query(ResultLog.columns).filter(
            and_(ResultLog.node_id == (node_id), and_(ResultLog.name == name, ResultLog.action != 'removed'))).order_by(
            desc(ResultLog.id)).offset(
            startPage).limit(
            perPageRecords).all()
        for r in record_query:
            data = r[0]
            data['data'] = json.dumps(data)
            results.append(data)

        columns.append({"className": 'details-control',
                        "orderable": False,
                        'data': 'data', 'title': 'data',
                        "defaultContent": ''})

    output = {}
    try:
        output['sEcho'] = str(int(request.values['sEcho']))
    except:
        print('error in echo')
    output['iRecordsFiltered'] = str(countFiltered)
    output['iTotalRecords'] = str(count)
    output['pageLength'] = str(perPageRecords)

    output['iTotalDisplayRecords'] = str(countFiltered)
    aaData_rows = results

    # add additional rows here that are not represented in the database
    # aaData_row.append(('''''' % (str(row[ self.index ]))).replace('\\', ''))
    if not columnsDefined:
        output['columns'] = columns
    output['aaData'] = aaData_rows

    return output


@blueprint.route('/apikey/add', methods=['GET', 'POST'])
@login_required
def update_api_keys():
    print('')
    IBMxForceKey = 'IBMxForceKey'
    IBMxForcePass = 'IBMxForcePass'
    VT_KEY = 'vt_key'
    OTX_KEY = 'otx_key'

    vt_key = request.form.get(VT_KEY)
    ibm_key = request.form.get(IBMxForceKey)
    ibm_pass = request.form.get(IBMxForcePass)

    otx_key = request.form.get(OTX_KEY)

    error_message = None
    if ibm_key and ibm_pass:
        ibm_x_force_credentials = db.session.query(ThreatIntelCredentials).filter(
            ThreatIntelCredentials.intel_name == 'ibmxforce').first()

        if ibm_x_force_credentials:
            new_credentials = dict(ibm_x_force_credentials.credentials)
            new_credentials['key'] = ibm_key
            new_credentials['pass'] = ibm_pass
            ibm_x_force_credentials.credentials = new_credentials
            db.session.add(ibm_x_force_credentials)
            db.session.commit()
        else:
            credentials = {}
            credentials['key'] = ibm_key
            credentials['pass'] = ibm_pass
            ThreatIntelCredentials.create(intel_name='ibmxforce', credentials=credentials)

    if vt_key:
        vt_credentials = db.session.query(ThreatIntelCredentials).filter(
            ThreatIntelCredentials.intel_name == 'virustotal').first()

        if vt_credentials:
            new_credentials = dict(vt_credentials.credentials)
            new_credentials['key'] = vt_key
            vt_credentials.credentials = new_credentials
            db.session.add(vt_credentials)
            db.session.commit()
        else:
            credentials = {}
            credentials['key'] = vt_key
            ThreatIntelCredentials.create(intel_name='virustotal', credentials=credentials)
    if otx_key:
        alienvault_credentials = db.session.query(ThreatIntelCredentials).filter(
            ThreatIntelCredentials.intel_name == 'alienvault').first()

        if alienvault_credentials:
            new_credentials = dict(alienvault_credentials.credentials)
            new_credentials['key'] = otx_key
            alienvault_credentials.credentials = new_credentials
            db.session.add(alienvault_credentials)
            db.session.commit()
        else:
            credentials = {}
            credentials['key'] = otx_key
            ThreatIntelCredentials.create(intel_name='alienvault', credentials=credentials)
    if request.method == 'POST':
        flash(u'Successfully updated the api keys', 'success')
    API_KEYS = {}
    threat_intel_credentials = ThreatIntelCredentials.query.all()
    for threat_intel_credential in threat_intel_credentials:
        API_KEYS[threat_intel_credential.intel_name] = threat_intel_credential.credentials
    return render_template('/forms/api_keys.html', api_keys=API_KEYS)


@blueprint.route('/hunt', methods=['GET', 'POST'])
@login_required
def hunt(page=1):
    return render_template('/hunt.html', indicators={'md5': "MD5", 'sha256': "SHA256", 'domain_name': "Domain Name"})


def fetch_alert_node_query_status():
    x = 5
    rules = db.session.query(Alerts.rule_id, Rule.name, func.count(Alerts.rule_id)).filter(
        Alerts.source == Alerts.RULE).join(Alerts.rule).filter(
        or_(Alerts.status == None, Alerts.status != Alerts.RESOLVED)).group_by(
        Alerts.rule_id, Rule.name).order_by(
        func.count(Alerts.rule_id).desc()).limit(x).all()
    nodes = db.session.query(Alerts.node_id, Node.host_identifier, func.count(Alerts.node_id)).join(
        Alerts.node).group_by(Alerts.node_id, Node.host_identifier).filter(
        or_(Alerts.status == None, Alerts.status != Alerts.RESOLVED)).order_by(
        func.count(Alerts.node_id).desc()).limit(x).all()
    queries = db.session.query(Alerts.query_name, func.count(Alerts.query_name)).filter(
        or_(Alerts.status == None, Alerts.status != Alerts.RESOLVED)).group_by(
        Alerts.query_name).order_by(
        func.count(Alerts.query_name).desc()).limit(x).all()

    # fetching alerts count by severity and type
    alert_count = db.session.query(Alerts.source, Alerts.severity, db.func.count(Alerts.severity)).group_by(
        Alerts.source, Alerts.severity).all()
    alert_count_dict = {}
    for row_list in alert_count:
        if row_list[0] in alert_count_dict:
            alert_count_dict[row_list[0]][row_list[1]] = row_list[2]
        else:
            alert_count_dict[row_list[0]] = {row_list[1]: row_list[2]}

    chart_data = {}
    chart_data['alertExists'] = False
    chart_data['rules'] = rules
    chart_data['nodes'] = nodes
    chart_data['queries'] = queries
    chart_data['alert_count'] = alert_count_dict
    if len(nodes) > 0:
        chart_data['alertExists'] = True
    return chart_data


def fetch_dashboard_data(chart_data_obj):
    platform_count = db.session.query(Node.platform, db.func.count(Node.id)).group_by(Node.platform).all()
    platform_names = []
    platform_name_count = []
    for data in platform_count:
        platform_names.append(data[0])
        platform_name_count.append(data[1])

    query_names = []
    query_name_count = []
    try:
        query_count = DashboardData.query.filter(DashboardData.name == 'dashboard').first()
        if query_count:
            query_data = json.loads(query_count.data)['top_queries']
            for name, count in query_data.items():
                query_names.append(name)
                query_name_count.append(count)
    except Exception as e:
        pass

    checkin_interval = current_app.config['POLYLOGYX_CHECKIN_INTERVAL']
    current_time = dt.datetime.utcnow() - checkin_interval
    online_nodes = db.session.query(db.func.count(Node.id)).filter((
            Node.last_checkin > current_time)).scalar()
    offline_nodes = db.session.query(db.func.count(Node.id)).filter((
            Node.last_checkin < current_time)).scalar()
    source_alert_count = db.session.query(Alerts.source, db.func.count(Alerts.id)).filter(
        or_(Alerts.status == None, Alerts.status != Alerts.RESOLVED)).group_by(Alerts.source).all()
    chart_data = dict(chart_data_obj.items())
    chart_data.update(dict((x, y) for x, y in source_alert_count).items())
    chart_data['platform_count'] = {"name_array": platform_names, "count_array": platform_name_count}
    chart_data['query_count'] = {"name_array": query_names, "count_array": query_name_count}

    chart_data['online_offline'] = {"name_array": ["Online", "Offline"], "count_array": [online_nodes, offline_nodes]}

    return chart_data


def save_email_recipients(emailRecipientStr):
    emailRecipients = []
    emailListStr = None
    db.session.query(EmailRecipient).update({EmailRecipient.status: 'inactive'})
    emails = emailRecipientStr.replace(' ', '').split(',')
    for email in emails:
        if email:
            emailRecipients.append(email)

            try:
                emailRecipient = db.session.query(EmailRecipient).filter(EmailRecipient.recipient == email).one()
            except MultipleResultsFound:
                emailRecipient = None
            except NoResultFound:
                emailRecipient = None

            if (emailRecipient):
                emailRecipient.status = 'active'
                emailRecipient.updated_at = dt.datetime.utcnow()
                # EmailRecipient.update(emailRecipient)

            else:
                emailRecipient = EmailRecipient()
                emailRecipient.status = 'active'
                emailRecipient.created_at = dt.datetime.now()
                emailRecipient.recipient = email
                emailRecipient.updated_at = dt.datetime.utcnow()
                # EmailRecipient.create(emailRecipient)
            db.session.add(emailRecipient)
            if emailListStr:
                emailListStr = emailListStr + ',' + email
            else:
                emailListStr = email
    db.session.commit()
    alerter_plugins = current_app.config.get('POLYLOGYX_ALERTER_PLUGINS', {})
    if 'email' in alerter_plugins:
        emailAlerter = alerter_plugins['email']
        emailAlerter[1]['recipients'] = [
            emailListStr,
        ]
        alerter_plugins['email'] = emailAlerter

    current_app.config['POLYLOGYX_ALERTER_PLUGINS'] = alerter_plugins

    current_app.config['EMAIL_RECIPIENTS'] = emailRecipients


def format_records(results):
    result_list = []
    keys = results.keys()

    data_list = results.fetchall()
    for data in data_list:
        result = {}
        for index, key in enumerate(keys):
            result[key] = data[index]
        result_list.append(result)
    return result_list


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        import decimal
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


def get_default_query_list(node):
    queries = {}
    if node.platform == 'windows':
        queries = merge_two_dicts(DefaultInfoQueries.DEFAULT_INFO_QUERIES, DefaultInfoQueries.DEFAULT_HASHES_QUERY)
    elif node.platform == 'darwin':
        queries = DefaultInfoQueries.DEFAULT_INFO_QUERIES_MACOS

    elif node.platform == 'linux':
        queries = DefaultInfoQueries.DEFAULT_INFO_QUERIES_LINUX

    elif node.platform == 'freebsd':
        queries = DefaultInfoQueries.DEFAULT_INFO_QUERIES_FREEBSD
    elif node.platform:
        queries = DefaultInfoQueries.DEFAULT_INFO_QUERIES_LINUX
    return queries
