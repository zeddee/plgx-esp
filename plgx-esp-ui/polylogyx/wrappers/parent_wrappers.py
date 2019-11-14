from flask_restplus import Model, fields

#common response wrapper
response_parent = Model('response', {
    'status': fields.String(default='success'),
})

failure_response_parent = Model('node_list_wrapper', {
    'status': fields.String(default='failure'),
    'message': fields.String(default='some error has occured')
})

common_response_wrapper = Model('common_wrapper', {'status': fields.String(description=u'status'),
                                                   'message': fields.String(description=u'message about the status'),
                                                   'data': fields.Raw(description=u'data if present')
                                                   })

file_wrapper = Model('filewrapper', {
    'file': fields.Raw()
})