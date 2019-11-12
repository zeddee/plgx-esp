from flask_restplus import Model, fields
from .parent_wrappers import *
from .pack_wrappers import pack_tag_wrapper
from .query_wrappers import query_tag_wrapper
from polylogyx.wrappers import node_wrappers as nodewrapper


tag_name_wrapper = Model('tag_name_wrapper', {
    'id': fields.Integer(),
    'value': fields.String(),
})

tag_wrapper = Model('tags_list', {
    'value' : fields.Raw(),
    'nodes' : fields.Raw(),
    'packs' : fields.Raw(),
    'queries' : fields.Raw(),
    'file_paths' : fields.Raw(),
})

response_taglist = response_parent.inherit('tag_list_wrapper', {
    'data': fields.Nested(tag_wrapper),
    'message': fields.String(default='Successfully fetched the tags info'),
})

