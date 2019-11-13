# -*- coding: utf-8 -*-
import json
import re

from flask import current_app
from flask_wtf import Form
from flask_wtf.file import FileField, FileRequired

from wtforms.fields import (
    BooleanField,
    DateTimeField,
    Field,
    IntegerField,
    SelectField,
    SelectMultipleField,
    StringField,
    TextAreaField
)
from wtforms.validators import DataRequired, Optional, ValidationError
from wtforms.widgets import HiddenInput

from polylogyx.models import Rule, Pack
from polylogyx.utils import validate_osquery_query


class ValidSQL(object):
    def __init__(self, message=None):
        if not message:
            message = u'Field must contain valid SQL to be run against osquery tables'
        self.message = message

    def __call__(self, form, field):
        if not validate_osquery_query(field.data):
            raise ValidationError(self.message)


class HiddenJSONField(Field):
    widget = HiddenInput()

    def _value(self):
        if self.data:
            return json.dumps(self.data)
        else:
            return u''

    def process_formdata(self, incoming):
        if incoming:
            self.data = json.loads(incoming[0])
        else:
            self.data = None


class UploadPackForm(Form):
    category =  platform = SelectField('Category', default=Pack.GENERAL, choices=[
        (Pack.MONITORING, Pack.MONITORING),
        (Pack.GENERAL, Pack.GENERAL),
        (Pack.FORENSICS_IR, Pack.FORENSICS_IR),
        (Pack.COMPLIANCE_MANAGEMENT, Pack.COMPLIANCE_MANAGEMENT),
        (Pack.INTRUSION_DETECTION, Pack.INTRUSION_DETECTION),
        (Pack.OTHERS, Pack.OTHERS),
    ])

    pack = FileField(u'Pack configuration', validators=[FileRequired()])


class UploadIntelForm(Form):
    intel = StringField(u'Intel', validators=[DataRequired()])

class UploadYARAForm(Form):
    yara = FileField(u'Yara', validators=[DataRequired()])

class DeleteResultForm(Form):
    days = SelectField('Name', validators=[DataRequired()])


class QueryForm(Form):
    name = StringField('Name', validators=[DataRequired()])
    sql = TextAreaField("Query", validators=[DataRequired(), ValidSQL()])
    interval = IntegerField('Interval', default=3600, validators=[DataRequired()])
    platform = SelectField('Platform', default='all', choices=[
        ('all', 'All'),
        ('darwin', 'Darwin'),
        ('linux', 'Linux'),
        ('freebsd', 'FreeBSD'),
        ('posix', 'POSIX Compatible'),
        ('windows', 'Windows'),
    ])
    version = StringField('Version')
    description = TextAreaField('Description')
    value = TextAreaField('Value')
    removed = BooleanField('Log Removed?', default=False)
    packs = SelectMultipleField('Packs', default=None, choices=[
    ])
    tags = TextAreaField("Tags")
    shard = IntegerField('Shard')
    snapshot = BooleanField('Snapshot', default=False)

    def set_choices(self):
        from polylogyx.models import Pack
        self.packs.choices = Pack.query.with_entities(Pack.name, Pack.name).all()


class UpdateQueryForm(QueryForm):
    def __init__(self, *args, **kwargs):
        super(UpdateQueryForm, self).__init__(*args, **kwargs)
        self.set_choices()
        query = kwargs.pop('obj', None)
        if query:
            self.packs.process_data([p.name for p in query.packs])
            self.tags.process_data('\n'.join(t.value for t in query.tags))


class CreateQueryForm(QueryForm):
    def validate(self):
        from polylogyx.models import Query
        initial_validation = super(CreateQueryForm, self).validate()
        if not initial_validation:
            return False

        query = Query.query.filter(Query.name == self.name.data).first()
        if query:
            self.name.errors.append(
                u"Query with the name {0} already exists!".format(
                    self.name.data)
            )
            return False

        # TODO could do some validation of the sql query
        return True


class CreateDeleteQueryResultForm(DeleteResultForm):
    def validate(self):
        from polylogyx.models import Query

        return True


class AddDistributedQueryForm(Form):
    sql = TextAreaField('Query', validators=[DataRequired(), ValidSQL()])
    description = TextAreaField('Description', validators=[Optional()])
    not_before = DateTimeField('Not Before', format="%Y-%m-%d %H:%M:%S",
                               validators=[Optional()])
    nodes = SelectMultipleField('Nodes', choices=[])
    tags = SelectMultipleField('Tags', choices=[])

    def set_choices(self):
        self.nodes.choices = []
        from polylogyx.models import Node, Tag

        import datetime as dt
        checkin_interval = current_app.config['POLYLOGYX_CHECKIN_INTERVAL']
        if isinstance(checkin_interval, (int, float)):
            checkin_interval = dt.timedelta(seconds=checkin_interval)

        choices_nodes = Node.query.filter(Node.is_active == True).filter(dt.datetime.utcnow() - Node.last_checkin < checkin_interval).with_entities(Node.node_key, Node.node_info['computer_name'].astext, Node.host_identifier).all();
        for choice_node in choices_nodes:
            display_name = choice_node[1]
            if (not display_name or display_name == ''):
                display_name = choice_node[2]
            filttered_choice_node = (choice_node[0], display_name)
            self.nodes.choices.append(filttered_choice_node)

        self.tags.choices = Tag.query.with_entities(Tag.value, Tag.value).all()


class CreateTagForm(Form):
    value = TextAreaField('Tag', validators=[DataRequired()])


class FilePathForm(Form):
    category = StringField('category', validators=[DataRequired()])
    target_paths = TextAreaField('files', validators=[DataRequired()])
    tags = TextAreaField("Tags")


class FilePathUpdateForm(FilePathForm):
    def __init__(self, *args, **kwargs):
        super(FilePathUpdateForm, self).__init__(*args, **kwargs)
        # self.set_choices()
        file_path = kwargs.pop('obj', None)
        if file_path:
            self.target_paths.process_data('\n'.join(file_path.get_paths()))
            self.tags.process_data('\n'.join(t.value for t in file_path.tags))


class RuleForm(Form):
    name = StringField('Rule Name', validators=[DataRequired()])
    alerters = SelectMultipleField('Alerters', default=None, choices=[
    ])
    description = TextAreaField('Description', validators=[Optional()])
    status = SelectField('Status', default='ACTIVE', choices=[('ACTIVE', 'ACTIVE'), ('INACTIVE', 'INACTIVE')])
    severity = SelectField('Severity', default=Rule.INFO, choices=[(Rule.INFO, Rule.INFO), (Rule.WARNING, Rule.WARNING), (Rule.CRITICAL, Rule.CRITICAL)])

    recon_queries = StringField('Recon Queries')

    conditions = HiddenJSONField('Conditions')
    type = SelectField('Type', default=Rule.DEFAULT, choices=[(Rule.DEFAULT, Rule.DEFAULT), (Rule.MITRE, Rule.MITRE)])
    technique_id= StringField('Technique Id')
    tactics = SelectMultipleField('Tactics', choices=[('initial-access', 'Initial Access'), ('execution', 'Execution'), ('persistence', 'Persistence'),
                                                      ('privilege-escalation', 'Privilege Escalation'), ('defense-evasion', 'Defense Evasion'), ('credential-access', 'Credential Access'),
                                                      ('discovery', 'Discovery'), ('lateral-movement', 'Lateral Movement'), ('collection', 'Collection'),
                                                      ('command-and-control', 'Command and Control'), ('exfiltration', 'Exfiltration'), ('impact', 'Impact')])

    def set_choices(self):
        self.alerters.choices = []
        alerter_ids = list(current_app.config.get('POLYLOGYX_ALERTER_PLUGINS', {}).keys())
        for a in alerter_ids:
            if a != 'debug':
                self.alerters.choices.append([a, a.title()])


class CreateRuleForm(RuleForm):
    def validate(self):
        from polylogyx.models import Rule

        initial_validation = super(CreateRuleForm, self).validate()
        if not initial_validation:
            return False

        query = Rule.query.filter(Rule.name == self.name.data).first()
        if query:
            self.name.errors.append(
                u"Rule with the name {0} already exists!".format(
                    self.name.data)
            )
            return False

        return True


class UpdateRuleForm(RuleForm):
    def __init__(self, *args, **kwargs):
        super(UpdateRuleForm, self).__init__(*args, **kwargs)
        self.set_choices()


class UpdateNodeForm(Form):
    display_name = StringField('Name', validators=[Optional()])
    is_active = BooleanField('Active', validators=[Optional()])


class ConfigForm(Form):
    config = StringField('Config')
    name = StringField('name')
    platform = SelectField('Platform', default='windows', choices=[
        ('darwin', 'Darwin'),
        ('linux', 'Linux'),
        ('windows', 'Windows'),
    ])


class CreateConfigForm(ConfigForm):
    def validate(self):
        initial_validation = super(ConfigForm, self).validate()
        if not initial_validation:
            return False
        return True


class UpdateConfigForm(ConfigForm):
    def __init__(self, *args, **kwargs):
        super(UpdateConfigForm, self).__init__(*args, **kwargs)


class OptionForm(Form):
    option = StringField('Option')
    name = StringField('name')


class CreateOptionForm(OptionForm):
    def validate(self):
        initial_validation = super(OptionForm, self).validate()
        if not initial_validation:
            return False
        return True


class UpdateOptionForm(OptionForm):
    def __init__(self, *args, **kwargs):
        super(UpdateOptionForm, self).__init__(*args, **kwargs)


class SettingForm(Form):
    setting = StringField('Setting')
    name = StringField('name')


class CreateSettingForm(SettingForm):
    def validate(self):
        initial_validation = super(SettingForm, self).validate()
        if not initial_validation:
            return False
        return True


class UpdateSettingForm(SettingForm):
    def __init__(self, *args, **kwargs):
        super(UpdateSettingForm, self).__init__(*args, **kwargs)


class SearchForm(Form):
    conditions = HiddenJSONField('Conditions')


class CreateSearchForm(SearchForm):
    def validate(self):
        return True
