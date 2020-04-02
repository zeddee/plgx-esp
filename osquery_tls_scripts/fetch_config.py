#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Script to fetch the config of a host.
:copyright: (c) 2019 by PolyLogyx.
:license: MIT, see LICENSE for more details.

Usage : python fetch_config.py --domain=127.0.0.1 --node_key=<Node key>
"""

import argparse
import json

import requests


def main(domain, port, node_key):
    url = "https://" + domain + ":" + str(port) + "/config"
    headers={'Content-Type':'application/json'}
    response = requests.post(url,headers=headers, data=json.dumps({"node_key": node_key}), verify=False)
    print(json.dumps(response.json(), sort_keys=False, indent=4))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Config.')

    parser.add_argument('--domain',

                        help='Domain/Ip of the server', required=True)
    parser.add_argument('--port',

                        help='Port', required=False, default=9000)
    parser.add_argument('--node_key',

                        help='Node Key', required=True)
    args = parser.parse_args()

    main(args.domain, args.port, args.node_key)
