from flask_restplus import Model, fields
from .parent_wrappers import *


alerts_wrapper =  Model('alert_wrapper', {
	'query_name': fields.String(default = None),
	'message': fields.Raw(default = None),
	'node_id': fields.Integer(default = None),
	'rule_id': fields.Integer(default = None),
	'severity': fields.String(default = None),
	'rule': fields.String(default = None),
	'created_at': fields.DateTime(default = None),
	'type': fields.String(default = None),
	'source': fields.String(default = None),
	'recon_queries': fields.Raw(default=None),
	'status': fields.String(default=None)
})


alerts_data_wrapper =  Model('alert_data_wrapper', {
	'query_name': fields.String(default=None),
	'message': fields.Raw(default=None),
	'node_id': fields.Integer(default=None),
	'rule_id': fields.Integer(default=None),
	'severity': fields.String(default=None),
	'rule': fields.String(default=None),
	'created_at': fields.DateTime(default=None),
	'type': fields.String(default=None),
	'source': fields.String(default=None),
	'recon_queries': fields.Raw(default=None),
	'status': fields.String(default=None),
	'source_data': fields.Raw(default = None)
})