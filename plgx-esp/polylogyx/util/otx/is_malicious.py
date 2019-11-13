# This script tells if a File, IP, Domain or URL may be malicious according to the data in OTX

import hashlib


from polylogyx.util.otx import get_malicious


def is_ip_malicious(ip,otx):
    alerts = get_malicious.ip(otx, ip)
    if len(alerts) > 0:
        print('Identified as potentially malicious')
        print(str(alerts))
    else:
        print('Unknown or not identified as malicious')

def is_host_malicious(host,otx):
    alerts = get_malicious.hostname(otx, host)
    if len(alerts) > 0:
        print('Identified as potentially malicious')
        print(str(alerts))
    else:
        print('Unknown or not identified as malicious')


def is_url_malicious(url,otx):
    alerts = get_malicious.url(otx, url)
    if len(alerts) > 0:
        print('Identified as potentially malicious')
        print(str(alerts))
    else:
        print('Unknown or not identified as malicious')

def is_hash_malicious(hash,otx):
    alerts = get_malicious.file(otx, hash)
    return alerts
    if len(alerts) > 0:
        print('Identified as potentially malicious')
        print(str(alerts))
    else:
        print('Unknown or not identified as malicious')

def is_file_malicious(file_path,otx):
    hash = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
    alerts =  get_malicious.file(otx, hash)

    if len(alerts) > 0:
        print('Identified as potentially malicious')
        print(str(alerts))
    else:
        print('Unknown or not identified as malicious')



