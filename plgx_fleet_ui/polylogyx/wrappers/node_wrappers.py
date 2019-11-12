from flask_restplus import Model, fields
from .parent_wrappers import *

# Node Wrappers
node_info_wrapper = Model('node_info', {
    'computer_name': fields.String(),
    'hardware_model': fields.String(),
    'hardware_serial': fields.String(),
    'hardware_vendor': fields.String(),
    'physical_memory': fields.String(),
    'cpu_physical_cores': fields.String()
})

network_info_wrapper = Model('network_info', {
    'mac_address': fields.String()
})

nodewrapper = Model('node', {
    'id':fields.Integer(),
    'host_identifier': fields.String(),
    'os_info': fields.Raw(),
    'node_info': fields.Nested(node_info_wrapper, default=None),
    'network_info': fields.Raw(),
    'last_checkin': fields.DateTime(default = None),
    'enrolled_on': fields.DateTime(default = None),
})

nodebyid_data = Model('node_by_id_data', {
    'name': fields.String(),
    'path': fields.String(),
    'status': fields.String()
})

system_data_wrapper = Model('system_data', {
    'name': fields.String(),
    'data': fields.Nested(nodebyid_data),
    'updated_at': fields.DateTime()
})

nodebyid_wrapper = nodewrapper.inherit('node_by_id', {
    'system_data': fields.Nested(system_data_wrapper)
})


node_tag_wrapper = Model('node_tag_wrapper', {
    'host_identifier': fields.String(),
    'node_key': fields.String()
})
