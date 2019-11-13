from flask_restplus import Model, fields
from .parent_wrappers import *
from polylogyx.wrappers import pack_wrappers

query_wrapper = Model('queries_list',{
    'id':fields.Integer(),
    'name' : fields.String(),
    'sql' : fields.String(default = None),
    'interval' : fields.Integer(default = None),
    'platform' : fields.String(default = None),
    'version' : fields.String(default = None),
    'description' : fields.String(default = None),
    'value' : fields.String(default = None),
    'snapshot' : fields.Boolean(default = None),
    'shard' : fields.Integer(default = None),
    # 'packs' : fields.Nested(pack_wrappers.pack_list_wrapper)
})

response_querylist = response_parent.inherit('queries_list_wrapper', {
    'data': fields.Nested(query_wrapper),
    'message': fields.String(default = "successfully fetched the query info")
})

add_query_wrapper = response_parent.inherit('queries_list_wrapper', {
    'query_id': fields.Integer(),
    'message': fields.String(default = "Successfully added the query for the data given")
})

query_tag_wrapper = Model('query_list_tag',{
    'name' : fields.String(),
    'sql' : fields.String(default = None)
})