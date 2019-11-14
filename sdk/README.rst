
polylogyx-api
==============




Installation
------------

.. code-block:: bash

    $ pip install polylogyx-api


Usage
-----
.. code-block:: python

    from __future__ import print_function
    import json
    from polylogyx_apis import PolylogyxApi

    polylogyx_api = PolylogyxApi(domain='<IP/DOMAIN>', username='<USERNAME>',password='<PASSWORD>')
    response = polylogyx_api.get_nodes()
    print(json.dumps(response, sort_keys=False, indent=4))



Documentation
-------------

You're looking at it.

Issues
------

Find a bug? Want more features? Find something missing in the documentation? Let me know! Please don't hesitate to `file an issue <https://github.com/polylogyx/polylogyx-api/issues/new>`_ and I'll get right on it.

License
-------

MIT Copyright (c) 2019 **polylogyx**
