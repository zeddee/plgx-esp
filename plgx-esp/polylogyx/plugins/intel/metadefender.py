# -*- coding: utf-8 -*-
import logging

from flask import current_app

from .base import AbstractIntelPlugin
import requests, json
import argparse
import hashlib
import os, sys


class MetaDefenderIntel(AbstractIntelPlugin):
    LEVEL_MAPPINGS = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warn': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL,
    }

    def __init__(self, config):
        levelname = config.get('level', 'debug')
        self.level = self.LEVEL_MAPPINGS.get(levelname, logging.DEBUG)

    def analyse_hash(self, value,type, node):
        # TODO(andrew-d): better message?
        current_app.logger.log(self.level, 'Triggered alert: ')
    def analyse_domain(self, value,type, node):
        # TODO(andrew-d): better message?
        current_app.logger.log(self.level, 'Triggered alert: ')

def scan_file(api_key, file, filename=None, archive_pwd=None,sharing=None, user_agent=None):
    '''
    Summary: Scan a file. It supports http multipart and binary uploads.
    input:
        api_key: unique API token (string)
        file: file to be scanned (string)
        filename: name of files to preserve extension and metadata during scan (string)
        archive_pwd: if submitted file is password-protected archive (string)
        sharing: allow file scans to be shared or not (bool)
        dwn_link: link to download file (string)
        user_agent: active workflows (string)
    return:
        output_data: response dictionary containing dataid, rest_ip, status, in_queue, queue_priority (dic)
    '''

    url = "https://api.metadefender.com/v2/file"
    headers = {'apikey': api_key, 'archivepwd':archive_pwd, 'samplesharing':sharing,
                'user_agent':user_agent, 'Content-Type':"www-url-encode"}
    try:
        #print("Attempting to scan file...")
        response = requests.post(url=url,data=file,headers=headers)
        output_data = response.json()
    except requests.exceptions.RequestException as err_req:
        print ("Request Error:",err_req)
        sys.exit(0)
    except requests.exceptions.HTTPError as err_http:
        print ("Http Error:",err_http)
        sys.exit(0)
    except requests.exceptions.ConnectionError as err_conn:
        print ("Error Connecting:",err_conn)
        sys.exit(0)
    except requests.exceptions.Timeout as err_to:
        print ("Timeout Error:",err_to)
        sys.exit(0)
    except:
        print ("Unable to scan file.")
        sys.exit(0)
    #print("Scanning complete.")
    return output_data['data_id']

def retrieve_scan(url,api_key, datatype, metadata='0'):
    '''
    Summary: Retrieve scan status and results after uploading a file or hash
    input:
        data: data ID recieved on upload (string)
        api_key: unique API token (string)
        file_metadata: Retrieve file metadata and hash_results (int)
    '''
    headers = {'apikey': api_key, 'file-metadata': metadata}
    try:
        response = requests.get(url=url,headers=headers)
        output_data = response.json()
    except requests.exceptions.RequestException as err_req:
        print ("Request Error:",err_req)
        sys.exit(0)
    except requests.exceptions.HTTPError as err_http:
        print ("Http Error:",err_http)
        sys.exit(0)
    except requests.exceptions.ConnectionError as err_conn:
        print ("Error Connecting:",err_conn)
        sys.exit(0)
    except requests.exceptions.Timeout as err_to:
        print ("Timeout Error:",err_to)
        sys.exit(0)
    except:
        print ("Unable to scan {0}".format(datatype))
        sys.exit(0)

    return output_data

def calculate_hash(hash_type, file_name, chunk_size=65536):
    '''
    Calculate hash of a given file
    input:
        hash_type: type of hash function to use (string)
        file_name: name of file to hash (string)
    return:
        hash of input file (string)
    '''
    try:
        if hash_type == "md5":
            hash = hashlib.md5()
        elif hash_type == "sha1":
            hash = hashlib.sha1()
        elif hash_type == "sha256":
            hash = hashlib.sha256()
        with open(file_name, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hash.update(chunk)
    except:
        print("Unable to hash file...")
        sys.exit(0)
    return hash.hexdigest()

def display_results(results):
    print("filename: {file_name}".format(file_name=results['file_info']['display_name']))
    print("overall_status: {status}".format(status=results['scan_results']['scan_all_result_a']))

    for k,v in results['scan_results']['scan_details'].items():
        print("\nengine: {engine}".format(engine=k))
        print("thread_found: {thread}".format(thread=v['threat_found'] if v['threat_found'] else 'clean'))
        print("scan_result: {result}".format(result=v['scan_result_i']))
        print("def_time: {time}".format(time=v['def_time']))


def parse_arguments():
    parser = argparse.ArgumentParser()

    #Required Arguments
    parser.add_argument("-f", "--file", dest="file", required=True,
                        help="Specify a file that should be scanned")

    parser.add_argument("-k", "--key", dest="key", required=True,
                        help="Unique API token to give rights to use endpoint")

    parser.add_argument("-hash", "--hash", dest="hash",  required=False, default="sha256",
                        help="Specify the hash function (type) to be used for the given file; default md5")

    #Optional Arguments
    parser.add_argument("-m", "--meta", dest="metadata", required=False, default=None,
                        help="Specify file metadata, 0 (don't add) or 1 (add)")


    #file_name
    parser.add_argument("-n", "--name", dest="preserve", action="store_true", required=False, default=None,
                        help="flag to preserve file name in scan")
    #archivepwd
    parser.add_argument("-p", "--password", dest="pwd", required=False, default=None,
                        help="password if submitted file is password protected")
    #samplesharing (0 or 1)
    parser.add_argument("-s", "--share", dest="share", action="store_true", default=None, required=False,
                        help="allows file scans to be shared or not (only working for paid users): allowed values 0/1")
    #downloadfrom
    # parser.add_argument("-u", "--url", dest="link", default=None,
    #                     help="link to download file")
    #active workflows (mcl-metadefender-rest-sanitize-disabled-unarchive)
    parser.add_argument("-w", "--workflow", dest="workflow", default=None,
                        help="active workflows, allowed values: mcl-metadefender-rest-sanitize-disabled-unarchive")

    args = parser.parse_args()
    # if args.link:
    #     args.file = download_file(args.link)
        #print(args.file)
    if args.preserve:
        args.preserve = args.file
    validate(args)
    return args

def validate(args):
    '''
    validate given args based on arg criteria
    input:
        args: inputted arguments
    '''
    # if not args.file and not args.link:
    #     print("No file or link to check")
    #     sys.exit()

    workflow_values = ['mcl', 'metadefender', 'rest', 'sanitize', 'disabled', 'unarchive']
    if args.workflow and args.workflow not in workflow_values:
        print("Invalid workflow variable given, allowed values: mcl-metadefender-rest-sanitize-disabled-unarchive")
        sys.exit(0)

if __name__ == '__main__':
    args = parse_arguments()

    #Steps:
    #1: Calulate hash of given file
    file_hash = calculate_hash(args.hash, args.file).upper()

    #2: perform hash lookup for cached results
    url = "https://api.metadefender.com/v2/hash/{0}".format(file_hash)
    scan_result = retrieve_scan(url=url, api_key = args.key, metadata=args.metadata, datatype="hash")

    #3: if cached, skip to 6
    if "Not Found" not in scan_result.values():
        #print("Hash Found.")
        display_results(scan_result)
        sys.exit(0)

    #4: if no cached results, get data_id
    #print("No cached results")
    with open(args.file, 'rb') as f:
        file = f.read()
    data_id = scan_file(api_key=args.key, file=file, filename=args.preserve, archive_pwd=args.pwd,sharing=args.share, user_agent=args.workflow)

    #5: repeatedly pull data_id to retrieve results
    url = "https://api.metadefender.com/v2/file/{0}".format(data_id)
    scan_result = retrieve_scan(url=url, api_key=args.key, metadata=args.metadata, datatype="dataId")
    while scan_result['scan_results']['progress_percentage'] != 100:
            scan_result = retrieve_scan(url=url, api_key=args.key, metadata=args.metadata, datatype="dataId")

    #6: display results in given format
    display_results(scan_result)