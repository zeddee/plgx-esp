from flask_restplus import Model, fields
from .parent_wrappers import *
import datetime

rule_wrapper = Model('rule_info', {
    'id': fields.Integer(),
    'alerters': fields.List(fields.String(default = None)),
    'conditions': fields.String(default = None),
    'description': fields.String(default = None),
    'name': fields.String(default = None),
    'status': fields.String(default = None),
    'updated_at': fields.DateTime(default = datetime.datetime.now()),
    'type': fields.String(default = None),
    'tactics': fields.Raw(),
    'technique_id': fields.String(default = None)
})

response_rulelist = response_parent.inherit('rule_list_wrapper', {
    'data': fields.Nested(rule_wrapper),
    'message': fields.String(default = "successfully fetched the rules info")
})

response_add_rule = Model('rule_add_wrapper', {
    'status': fields.String(default="success"),
    'rule_id': fields.Integer(),
    'message': fields.String(default='rule is added successfully')
})