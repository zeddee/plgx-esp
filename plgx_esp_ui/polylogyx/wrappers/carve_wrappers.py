from flask_restplus import Model, fields
from .parent_wrappers import *
from .node_wrappers import nodewrapper

# Carves Wrapper

carves_wrapper =  Model('carves_wrapper', {
    'id': fields.Integer(),
    'node_id': fields.Integer(),
    'session_id': fields.String(),
    'carve_guid': fields.String(),
    'carve_size': fields.Integer(),
    'block_size': fields.Integer(),
    'block_count': fields.Integer(),
    'archive': fields.String(default = None),
    'created_at': fields.DateTime(),
    'node': fields.Nested(nodewrapper, default=None)
})