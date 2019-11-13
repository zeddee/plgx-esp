from flask_restplus import Model, fields
from .parent_wrappers import *
from .node_wrappers import nodewrapper

# ResultLog Wrapper

result_log_wrapper =  Model('result_log_wrapper', {
    'id': fields.Integer(),
    'name': fields.String(),
    'timestamp': fields.DateTime(),
    'action': fields.String(),
    'columns': fields.Raw(default = None),
    'node_id': fields.Integer()
})