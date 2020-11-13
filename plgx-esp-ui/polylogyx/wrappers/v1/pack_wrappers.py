from flask_restplus import fields
from .parent_wrappers import response_parent
from polylogyx.blueprints.v1.external_api import api
from polylogyx.wrappers.v1.query_wrappers import query_wrapper

pack_wrapper = api.model('pack_wrapper',{
    'id': fields.Integer(),
    'name' :fields.String(),
    'platform' : fields.String(default = None),
    'version' :fields.String(default = None),
    'description' : fields.String(default = None),
    'shard' : fields.Integer(default = None),
    'category' : fields.String(default = 'General'),
})


response_add_pack = response_parent.inherit('add_pack_wrapper', {
    'pack_id': fields.Integer(),
    'message' : fields.String(default = "Imported query pack and pack is added/uploaded successfully")
})
