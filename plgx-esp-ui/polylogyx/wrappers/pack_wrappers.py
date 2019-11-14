from flask_restplus import Model, fields
from .parent_wrappers import *
from .query_wrappers import query_tag_wrapper

pack_wrapper = Model('packs_list',{
    'id': fields.Integer(),
    'name' :fields.String(),
    'platform' : fields.String(default = None),
    'version' :fields.String(default = None),
    'description' : fields.String(default = None),
    'shard' : fields.Integer(default = None),
})

pack_list_wrapper = Model('packs_list',{
    'id': fields.Integer(),
    'name' :fields.String()
})

response_packlist = response_parent.inherit('pack_list_wrapper', {
    'data': fields.Nested(pack_wrapper),
    'message' : fields.String(default = "successfully fetched the pack info")
})

response_add_pack = response_parent.inherit('add_pack_wrapper', {
    'pack_id': fields.Integer(),
    'message' : fields.String(default = "Imported query pack and pack is added successfully")
})

pack_tag_wrapper = Model('pack_list_tag',{
    'name' :fields.String(),
    'queries' : fields.List(fields.Nested(query_tag_wrapper,default = None)),
})