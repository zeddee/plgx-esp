"""
All Test-Case required client, url_prefix and token,
and these all we need to just pass as parameters in the function.
"""

import json
from polylogyx.dao import configs_dao, hosts_dao, packs_dao, queries_dao


class TestConfigList:

    def test_get_config_list_without_data(self, client, url_prefix, token):
        """
        Test-case without existing dafault query and default filter data,
        expected output:- status is success, and
        response data is empty dictionary in this case
        """
        resp = client.get(url_prefix + '/configs/all', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == {}

    def test_get_config_list_with_invalid_method(self, client, url_prefix, token, default_query, default_filter):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.delete(url_prefix + '/configs/all', headers={'x-access-token': token})
        assert resp.status_code == 405

    def test_get_config_list_with_data(self, client, url_prefix, token, default_query, default_filter):
        """
        Test-case with existing dafault query and default filter data,
        expected output:- status is success, and
        response data of config platform and arch wise
        """
        resp = client.get(url_prefix + '/configs/all', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        data = configs_dao.get_all_configs()
        assert response_dict['data']['windows']['x86']['0'] == data['windows']['x86'][0]
        assert response_dict['data']['windows']['x86_64']['0'] == data['windows']['x86_64'][0]
        assert response_dict['data']['linux']['x86_64']['0'] == data['linux']['x86_64'][0]
        assert response_dict['data']['darwin']['x86_64']['0'] == data['darwin']['x86_64'][0]


class TestEditOrUpdateConfigList:
    """
    Test-case inside this block where these payloads are used,
    except arch and type all values are compulsory payload value,
    and filters, queries are of dict type and remainings all are
    of str type, so if compulsory value is not passed or if type of value
    not matched with the specified type of value, then it will return 400 i.e., bad request
    """
    payload = {'filters': None, 'queries': None, 'platform': None, 'arch': None, 'type': None}

    def test_edit_config_list_without_payload(self, client, url_prefix, token):
        """
        Test-case without payload,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/configs/update', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_edit_config_list_empty_payload(self, client, url_prefix, token):
        """
        Test-case without payload,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/configs/update', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_edit_config_list_with_none_value_of_payload(self, client, url_prefix, token):
        """
        Test-case without payload,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/configs/update', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_edit_config_list_with_darwin_pltform_and_valid_mandatory_payload(self, client, url_prefix, token):
        """
        Test-case platform value is darwin, arch values (x86/x86_64), and
        type values (shallow/deep/default) and with filters and queries,
        expected output:- status is failure
        """
        payload = {}
        payload['filters'] = {
        "file_pasths": {
            "binaries": ["/usr/bin/%%", "/usr/sbin/%%", "/bin/%%", "/sbin/%%", "/usr/local/bin/%%",
                         "/usr/local/sbin/%%", "/opt/bin/%%", "/opt/sbin/%%"],
            "configuration": ["/etc/%%"]
        }
    }
        payload['queries'] = {
            "platform_info": {
                "interval": 15,
                "status": True,
                "query": "SELECT * FROM platform_info;"

            }
        }
        payload['platform'] = 'darwin'
        resp = client.post(url_prefix + '/configs/update', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_edit_config_list_with_linux_pltform_and_valid_mandatory_payload(self, client, url_prefix, token):
        """
        Test-case platform value is linux, arch values (x86/x86_64), and
        type values (shallow/deep/default) and with filters and queries,
        expected output:- status is failure
        """
        payload = {}
        payload['filters'] = {
        "events1": {
            "disable_subscribers": ["user_events"]
        },
        "file_paths": {
            "binaries": [
                "/usr/bin/%%", "/usr/sbin/%%", "/bin/%%", "/sbin/%%", "/usr/local/bin/%%",
                "/usr/local/sbin/%%", "%%/Downloads/%%"
            ],
            "configuration": [
                "/etc/passwd", "/etc/shadow", "/etc/ld.so.conf", "/etc/ld.so.conf.d/%%",
                "/etc/pam.d/%%", "/etc/resolv.conf", "/etc/rc%/%%", "/etc/my.cnf", "/etc/hosts",
                "/etc/hostname", "/etc/fstab", "/etc/crontab", "/etc/cron%/%%", "/etc/init/%%",
                "/etc/rsyslog.conf"
            ]
        }
    }
        payload['queries'] = {
            "platform_info": {
                "interval": 15,
                "status": True,
                "query": "SELECT * FROM file_events;"

            }
        }
        payload['platform'] = 'linux'
        resp = client.post(url_prefix + '/configs/update', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_edit_config_list_with_winx86_64_pltform_and_valid_mandatory_payload(self, client, url_prefix, token):
        """
        Test-case platform value is windows, arch values x86_64, and
        type values (shallow/deep/default) and with filters and queries,
        expected output:- status is failure
        """
        payload = {}
        payload['filters'] = {
        "win_include_paths": {"all_files": ["*"]},
        "plgx_event_filters": {
            "win_ssl_events": {
                "process_name": {
                    "exclude": {
                        "values": [
                            "*\\Program Files\\osquery\\osqueryd\\osqueryd.exe",
                            "*\\Program Files\\osquery\\plgx_win_extension.ext.exe",
                            "*\\Program Files\\osquery\\plgx_cpt.exe"
                        ]
                    }
                }
            },
            "win_file_events": {
                "target_path": {
                    "exclude": {
                        "values": [
                            "C:\\Windows\\system32\\DriverStore\\Temp\\*",
                            "C:\\Windows\\system32\\wbem\\Performance*",
                            "C:\\$WINDOWS.~BT\\Sources\\*",
                            "C:\\Windows\\Installer\\*", "*WRITABLE.TST",
                            "C:\\Windows\\System32\\Tasks\\Adobe Acrobat Update Task*",
                            "C:\\Windows\\System32\\Tasks\\Adobe Flash Player Updater*",
                            "C:\\Windows\\System32\\Tasks\\OfficeSoftwareProtectionPlatform\\SvcRestartTask*"
                        ]
                    },
                    "include": {
                        "values": [
                            "*\\Start Menu*", "*\\Startup\\*", "*\\Content.Outlook\\*",
                            "*\\Downloads\\*", "*.application", "*.appref-ms", "*.bat", "*.chm",
                            "*.cmd", "*.cmdline", "*.docm", "*.exe", "*.jar", "*.jnlp", "*.jse",
                            "*.hta", "*.pptm", "*.ps1", "*.sys", "*.scr", "*.vbe", "*.vbs", "*.xlsm",
                            "*.proj", "*.sln", "C:\\Users\\Default*", "C:\\Windows\\system32\\Drivers*",
                            "C:\\Windows\\SysWOW64\\Drivers*",
                            "C:\\Windows\\system32\\GroupPolicy\\Machine\\Scripts*",
                            "C:\\Windows\\system32\\GroupPolicy\\User\\Scripts*",
                            "C:\\Windows\\system32\\Wbem*", "C:\\Windows\\SysWOW64\\Wbem*",
                            "C:\\Windows\\system32\\WindowsPowerShell*",
                            "C:\\Windows\\SysWOW64\\WindowsPowerShell*",
                            "C:\\Windows\\Tasks\\*",
                            "C:\\Windows\\system32\\Tasks*", "C:\\Windows\\AppPatch\\Custom*",
                            "*VirtualStore*", "*.xls", "*.ppt", "*.rtf"
                        ]
                    }
                },
                "process_name": {
                    "exclude": {
                        "values": [
                            "C:\\Program Files (x86)\\EMET 5.5\\EMET_Service.exe",
                            "C:\\Program Files\\Common Files\\Microsoft Shared\\ClickToRun\\OfficeC2RClient.exe",
                            "C:\\Windows\\system32\\smss.exe", "C:\\Windows\\system32\\CompatTelRunner.exe",
                            "\\\\?\\C:\\Windows\\system32\\wbem\\WMIADAP.EXE",
                            "C:\\Windows\\system32\\wbem\\WMIADAP.EXE",
                            "C:\\Windows\\system32\\mobsync.exe",
                            "C:\\Program Files (x86)\\Dell\\CommandUpdate\\InvColPC.exe",
                            "C:\\Windows\\system32\\igfxCUIService.exe"
                        ]
                    }
                }
            },
            "feature_vecsSASators": {
                "character_frequencies": [
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.00045, 0.01798, 0, 0.03111, 0.00063,
                    0.00027, 0, 0.01336, 0.0133, 0.00128, 0.0027, 0.00035, 0.00092, 0.027875,
                    0.007465, 0.016265, 0.013995,  0.00737, 0.025615, 0.001725,
                    0.002265, 0.017875, 0.016005, 0.02533, 0.025295, 0.014375, 0.00109, 0.02732,
                    0.02658, 0.037355, 0.011575, 0.00451, 0.005865, 0.003255, 0.005965, 0.00077,
                    0.00771, 0.002379, 0.00766, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                ]
            }
        }
    }
        payload['queries'] = {
            "platform_info": {
                "interval": 10,
                "status": True,
                "query": "select * from win_socket_events;"

            }
        }
        payload['platform'] = 'windows'
        resp = client.post(url_prefix + '/configs/update', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_edit_config_list_with_winx86_pltform_and_valid_mandatory_payload(self, client, url_prefix, token):
        """
        Test-case platform value is windows, arch values x86, and
        type values (shallow/deep/default) and with filters and queries,
        expected output:- status is failure
        """
        payload = {}
        payload['filters'] = {}
        payload['queries'] = {
            "platform_info": {
                "interval": 10,
                "status": True,
                "query": "select * from drivers;"

            }
        }
        payload['platform'] = 'windows'
        payload['arch'] = 'x86'
        resp = client.post(url_prefix + '/configs/update', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_edit_config_list_with_invalid_queries_keys_payload(self, client, url_prefix, token):
        """
       Test-case platform value is darwin and with filters and queries,
       expected output:- status is success
       """
        payload = {}
        payload['filters'] = {
        "file_pasths": {
            "binaries": ["/usr/bin/%%", "/usr/sbin/%%", "/bin/%%", "/sbin/%%", "/usr/local/bin/%%",
                         "/usr/local/sbin/%%", "/opt/bin/%%", "/opt/sbin/%%"],
            "configuration": ["/etc/%%"]
        }
    }
        payload['queries'] = {
            "platform_info": {
                "interval": 15,
                "query": "SELECT * FROM platform_info;"

            }
        }
        payload['platform'] = 'darwin'
        resp = client.post(url_prefix + '/configs/update', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_edit_config_list_with_all_payload(self, client, url_prefix, token):
        """
        Test-case with all paylods value
        expected output:- status is failure
        """
        self.payload['filters'] = {
        "file_pasths": {
            "binaries": ["/usr/bin/%%", "/usr/sbin/%%", "/bin/%%", "/sbin/%%", "/usr/local/bin/%%",
                         "/usr/local/sbin/%%", "/opt/bin/%%", "/opt/sbin/%%"],
            "configuration": ["/etc/%%"]
        }
    }
        self.payload['queries'] = {
            "platform_info": {
                "interval": 15,
                "status": True,
                "query": "SELECT * FROM platform_info;"

            }
        }
        self.payload['platform'] = 'darwin'
        self.payload['arch'] = 'x86_64'
        self.payload['type'] = 'shallow'
        resp = client.post(url_prefix + '/configs/update', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_edit_config_list_with_invalid_method(self, client, url_prefix, token, default_query, default_filter):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.delete(url_prefix + '/configs/update', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_edit_configs_list_with_darwin_pltform_and_valid_mandatory_payload(self, client, url_prefix, token, default_query, default_filter):
        """
        Test-case platform value is darwin, arch values (x86/x86_64), and
        type values (shallow/deep/default) and with filters and queries,
        expected output:- status is success, and
        response_data with query_name, status, interval and filters value
        """
        payload = {}
        payload['filters'] = {
        "file_pasths": {
            "binaries": ["/usr/bin/%%", "/usr/sbin/%%", "/bin/%%", "/sbin/%%", "/usr/local/bin/%%",
                         "/usr/local/sbin/%%", "/opt/bin/%%", "/opt/sbin/%%"],
            "configuration": ["/etc/%%"]
        }
    }
        payload['queries'] = {
            "platform_info": {
                "interval": 15,
                "status": True,
                "query": "SELECT * FROM platform_info;"

            }
        }
        payload['platform'] = 'darwin'
        resp = client.post(url_prefix + '/configs/update', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['queries']['platform_info']['status'] == True
        assert response_dict['data']['queries']['platform_info']['interval'] == 15
        assert response_dict['data']['filters'] == payload['filters']

    def test_edit_configs_list_with_linux_pltform_and_valid_mandatory_payload(self, client, url_prefix, token, default_query, default_filter, node):
        """
        Test-case platform value is linux, arch values (x86/x86_64), and
        type values (shallow/deep/default) and with filters and queries,
        expected output:- status is success, and
         response_data with query_name, status, interval and filters value
        """
        payload = {}
        payload['filters'] = {
        "events1": {
            "disable_subscribers": ["user_events"]
        },
        "file_paths": {
            "binaries": [
                "/usr/bin/%%", "/usr/sbin/%%", "/bin/%%", "/sbin/%%", "/usr/local/bin/%%",
                "/usr/local/sbin/%%", "%%/Downloads/%%"
            ],
            "configuration": [
                "/etc/passwd", "/etc/shadow", "/etc/ld.so.conf", "/etc/ld.so.conf.d/%%",
                "/etc/pam.d/%%", "/etc/resolv.conf", "/etc/rc%/%%", "/etc/my.cnf", "/etc/hosts",
                "/etc/hostname", "/etc/fstab", "/etc/crontab", "/etc/cron%/%%", "/etc/init/%%",
                "/etc/rsyslog.conf"
            ]
        }
    }
        payload['queries'] = {
            "file_events": {
                "interval": 15,
                "status": True,
                "query": "SELECT * FROM file_events;"

            }
        }
        payload['platform'] = 'linux'
        resp = client.post(url_prefix + '/configs/update', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['queries']['file_events']['status'] == True
        assert response_dict['data']['queries']['file_events']['interval'] == 15
        assert response_dict['data']['filters'] == payload['filters']

    def test_edit_configs_list_with_winx86_64_pltform_and_valid_mandatory_payload(self, client, url_prefix, token, default_query, default_filter):
        """
        Test-case platform value is windows, arch values x86_64, and
        type values (shallow/deep/default) and with filters and queries,
        expected output:- status is failure
        """
        payload = {}
        payload['filters'] = {
        "win_include_paths": {"all_files": ["*"]},
        "plgx_event_filters": {
            "win_ssl_events": {
                "process_name": {
                    "exclude": {
                        "values": [
                            "*\\Program Files\\osquery\\osqueryd\\osqueryd.exe",
                            "*\\Program Files\\osquery\\plgx_win_extension.ext.exe",
                            "*\\Program Files\\osquery\\plgx_cpt.exe"
                        ]
                    }
                }
            },
            "win_file_events": {
                "target_path": {
                    "exclude": {
                        "values": [
                            "C:\\Windows\\system32\\DriverStore\\Temp\\*",
                            "C:\\Windows\\system32\\wbem\\Performance*",
                            "C:\\$WINDOWS.~BT\\Sources\\*",
                            "C:\\Windows\\Installer\\*", "*WRITABLE.TST",
                            "C:\\Windows\\System32\\Tasks\\Adobe Acrobat Update Task*",
                            "C:\\Windows\\System32\\Tasks\\Adobe Flash Player Updater*",
                            "C:\\Windows\\System32\\Tasks\\OfficeSoftwareProtectionPlatform\\SvcRestartTask*"
                        ]
                    },
                    "include": {
                        "values": [
                            "*\\Start Menu*", "*\\Startup\\*", "*\\Content.Outlook\\*",
                            "*\\Downloads\\*", "*.application", "*.appref-ms", "*.bat", "*.chm",
                            "*.cmd", "*.cmdline", "*.docm", "*.exe", "*.jar", "*.jnlp", "*.jse",
                            "*.hta", "*.pptm", "*.ps1", "*.sys", "*.scr", "*.vbe", "*.vbs", "*.xlsm",
                            "*.proj", "*.sln", "C:\\Users\\Default*", "C:\\Windows\\system32\\Drivers*",
                            "C:\\Windows\\SysWOW64\\Drivers*",
                            "C:\\Windows\\system32\\GroupPolicy\\Machine\\Scripts*",
                            "C:\\Windows\\system32\\GroupPolicy\\User\\Scripts*",
                            "C:\\Windows\\system32\\Wbem*", "C:\\Windows\\SysWOW64\\Wbem*",
                            "C:\\Windows\\system32\\WindowsPowerShell*",
                            "C:\\Windows\\SysWOW64\\WindowsPowerShell*",
                            "C:\\Windows\\Tasks\\*",
                            "C:\\Windows\\system32\\Tasks*", "C:\\Windows\\AppPatch\\Custom*",
                            "*VirtualStore*", "*.xls", "*.ppt", "*.rtf"
                        ]
                    }
                },
                "process_name": {
                    "exclude": {
                        "values": [
                            "C:\\Program Files (x86)\\EMET 5.5\\EMET_Service.exe",
                            "C:\\Program Files\\Common Files\\Microsoft Shared\\ClickToRun\\OfficeC2RClient.exe",
                            "C:\\Windows\\system32\\smss.exe", "C:\\Windows\\system32\\CompatTelRunner.exe",
                            "\\\\?\\C:\\Windows\\system32\\wbem\\WMIADAP.EXE",
                            "C:\\Windows\\system32\\wbem\\WMIADAP.EXE",
                            "C:\\Windows\\system32\\mobsync.exe",
                            "C:\\Program Files (x86)\\Dell\\CommandUpdate\\InvColPC.exe",
                            "C:\\Windows\\system32\\igfxCUIService.exe"
                        ]
                    }
                }
            },
            "feature_vecsSASators": {
                "character_frequencies": [
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.00045, 0.01798, 0, 0.03111, 0.00063,
                    0.00027, 0, 0.01336, 0.0133, 0.00128, 0.0027, 0.00035, 0.00092, 0.027875,
                    0.007465, 0.016265, 0.013995,  0.00737, 0.025615, 0.001725,
                    0.002265, 0.017875, 0.016005, 0.02533, 0.025295, 0.014375, 0.00109, 0.02732,
                    0.02658, 0.037355, 0.011575, 0.00451, 0.005865, 0.003255, 0.005965, 0.00077,
                    0.00771, 0.002379, 0.00766, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                ]
            }
        }
    }
        payload['queries'] = {
            "platform_info": {
                "interval": 10,
                "status": True,
                "query": "select * from win_socket_events;"

            }
        }
        payload['platform'] = 'windows'
        resp = client.post(url_prefix + '/configs/update', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_edit_configs_list_with_winx86_pltform_and_valid_mandatory_payload(self, client, url_prefix, token, default_query, default_filter):
        """
        Test-case platform value is windows, arch values x86, and
        type values (shallow/deep/default) and with filters and queries,
        expected output:- status is success, and
        response_data with query_name, status, interval and filters value
        """
        payload = {}
        payload['filters'] = {}
        payload['queries'] = {
            "drivers": {
                "interval": 10,
                "status": True,
                "query": "select * from drivers;"

            }
        }
        payload['platform'] = 'windows'
        payload['arch'] = 'x86'
        resp = client.post(url_prefix + '/configs/update', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['queries']['drivers']['status'] == True
        assert response_dict['data']['queries']['drivers']['interval'] == 10
        assert response_dict['data']['filters'] == payload['filters']

    def test_edit_configs_list_with_invalid_queries_keys_payload(self, client, url_prefix, token, default_query, default_filter):
        """
       Test-case platform value is darwin and with filters and queries,
       expected output:- status_code is 400
       """
        payload = {}
        payload['filters'] = {
        "file_pasths": {
            "binaries": ["/usr/bin/%%", "/usr/sbin/%%", "/bin/%%", "/sbin/%%", "/usr/local/bin/%%",
                         "/usr/local/sbin/%%", "/opt/bin/%%", "/opt/sbin/%%"],
            "configuration": ["/etc/%%"]
        }
    }
        payload['queries'] = {
            "platform_info": {
                "interval": 15,
                "query": "SELECT * FROM platform_info;"

            }
        }
        payload['platform'] = 'darwin'
        resp = client.post(url_prefix + '/configs/update', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 400
        response_dict = json.loads(resp.data)

    def test_edit_configs_list_with_all_payload(self, client, url_prefix, token, default_query, default_filter):
        """
        Test-case with all paylods value
        expected output:- status is success, and
         response_data with query_name, status, interval and filters value
        """
        self.payload['filters'] = {
        "file_pasths": {
            "binaries": ["/usr/bin/%%", "/usr/sbin/%%", "/bin/%%", "/sbin/%%", "/usr/local/bin/%%",
                         "/usr/local/sbin/%%", "/opt/bin/%%", "/opt/sbin/%%"],
            "configuration": ["/etc/%%"]
        }
    }
        self.payload['queries'] = {
            "drivers": {
                "interval": 15,
                "status": True,
                "query": "select * from drivers;"

            }
        }
        self.payload['platform'] = 'windows'
        self.payload['arch'] = 'x86'
        self.payload['type'] = 'default'
        resp = client.post(url_prefix + '/configs/update', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['queries']['drivers']['status'] == True
        assert response_dict['data']['queries']['drivers']['interval'] == 15
        assert response_dict['data']['filters'] == self.payload['filters']


class TestGetConfigByPlatformOrNode:
    """
    Test-case inside this block where these payloads are used,
    all are optional values and of str type, and some values are
    already present to choose, like for platform, we have linux/windows/darwin, and
    for arch we have x86/x86_64, so if type of value is not matched or passed any other
    value for platform and arch then it will return 400 i.e., bad request
    """
    payload = {'platform': None, 'arch': None, 'host_identifier': None}

    def test_get_config_without_payload(self, client, url_prefix, token):
        """
        Test-case without payloads and without existing node and config data,
        expected output:- status is failure
        """
        resp = client.post(url_prefix + '/configs/view', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_config_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload is empty dictionary and without existing node and config data,
        expected output:- status is failure
        """
        resp = client.post(url_prefix + '/configs/view', headers={'x-access-token': token}, json={})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_config_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with payload value is none and without existing node and config data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/configs/view', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_get_config_with_only_host_identifier(self, client, url_prefix, token):
        """
        Test-case with only valid/invalid payload value of host_identifier
        and without existing node and config data,
        expected output:- status is failure
        """
        payload = {'host_identifier': 'foobar'}
        resp = client.post(url_prefix + '/configs/view', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_config_with_only_invalid_platform_value(self, client, url_prefix, token):
        """
        Test-case with only payload value of platform and without existing node and config data,
        expected output:- status_code is 400
        """
        payload = {'platform': 'foobar'}
        resp = client.post(url_prefix + '/configs/view', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 400

    def test_get_config_with_only_valid_platform_value(self, client, url_prefix, token):
        """
        Test-case with only payload value of platform and without existing node and config data,
        expected output:- status is failure
        """
        payload = {'platform': 'darwin'}
        resp = client.post(url_prefix + '/configs/view', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_config_with_only_invalid_arch_value(self, client, url_prefix, token):
        """
        Test-case with only invalid payload value of arch and without existing node and config data,
        expected output:- status_code is 400
        """
        payload = {'arch': 'foobar'}
        resp = client.post(url_prefix + '/configs/view', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 400

    def test_get_config_with_only_valid_arch_value(self, client, url_prefix, token):
        """
        Test-case with only valid payload value of arch and without existing node and config data,
        expected output:- status is failure
        """
        payload = {'arch': 'x86'}
        resp = client.post(url_prefix + '/configs/view', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_config_with_platform_and_arch_value(self, client, url_prefix, token):
        """
        Test-case with all valid payload value and without existing node and config data,
        expected output:- status is failure
        """
        payload = {}
        payload['platform'] = 'windows'
        payload['arch'] = 'x86'
        resp = client.post(url_prefix + '/configs/view', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_config_with_all_valid_payload_value(self, client, url_prefix, token):
        """
        Test-case with all valid payload value and without existing node and config data,
        expected output:- status is failure
        """
        self.payload['platform'] = 'windows'
        self.payload['arch'] = 'x86'
        self.payload['host_identifier'] = 'foobar'
        resp = client.post(url_prefix + '/configs/view', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_config_with_invalid_method(self, client, url_prefix, token, node, options, default_filter, default_query):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.get(url_prefix + '/configs/view', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_get_configs_with_only_invalid_host_identifier(self, client, url_prefix, token, node, options, default_filter, default_query):
        """
        Test-case with only invalid payload value of host_identifier
        and without existing node and config data,
        expected output:- status is failure
        """
        payload = {'host_identifier': 'foo'}
        resp = client.post(url_prefix + '/configs/view', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_configs_with_only_valid_host_identifier(self, client, url_prefix, token, node, options, default_filter, default_query, packs, queries):
        """
        Test-case with only valid payload value of host_identifier
        and without existing node and config data,
        expected output:- status is success, and
        a response dict data with key values are options, queries, packs, filters and file_paths
        """
        payload = {'host_identifier': 'foobar'}
        p = packs_dao.get_pack_by_name('pytest_pack')
        q = queries_dao.get_query_by_name('test_query')
        q.packs.append(p)
        resp = client.post(url_prefix + '/configs/view', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        nod = hosts_dao.get_node_by_host_identifier('foobar')
        data = nod.get_config()
        assert response_dict['data']['options'] == data['options']
        assert response_dict['data']['queries'] == data['queries']
        assert response_dict['data']['packs'] == data['packs']
        assert response_dict['data']['filters'] == data['filters']
        assert response_dict['data']['file_paths'] == {}

    def test_gets_config_with_only_invalid_platform_value(self, client, url_prefix, token, options, node, default_query, default_filter, packs, queries):
        """
        Test-case with only payload value of platform and without existing node and config data,
        expected output:- status_code is 400
        """
        payload = {'platform': 'foobar'}
        resp = client.post(url_prefix + '/configs/view', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 400

    def test_get_configs_with_only_valid_platform_value(self, client, url_prefix, token, options, node, default_query, default_filter, packs, queries):
        """
        Test-case with only payload value of platform and without existing node and config data,
        expected output:- status is failure
        """
        payload = {'platform': 'darwin'}
        resp = client.post(url_prefix + '/configs/view', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_configs_with_only_invalid_arch_value(self, client, url_prefix, token, options, node, default_query, default_filter, packs, queries):
        """
        Test-case with only invalid payload value of arch and without existing node and config data,
        expected output:- status_code is 400
        """
        payload = {'arch': 'foobar'}
        resp = client.post(url_prefix + '/configs/view', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 400

    def test_get_configs_with_only_valid_arch_value(self, client, url_prefix, token, options, node, default_query, default_filter, packs, queries):
        """
        Test-case with only valid payload value of arch and without existing node and config data,
        expected output:- status is failure
        """
        payload = {'arch': 'x86'}
        resp = client.post(url_prefix + '/configs/view', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_configs_with_platform_and_arch_value(self, client, url_prefix, token, options, node, default_query, default_filter, packs, queries):
        """
        Test-case with all valid payload value and without existing node and config data,
        expected output:- status is success, and
        a response dict data with key values are queries, filters and type
        """
        payload = {}
        payload['platform'] = 'windows'
        payload['arch'] = 'x86'
        resp = client.post(url_prefix + '/configs/view', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        config_data = configs_dao.get_config('windows', 'x86')
        data = configs_dao.get_config_by_platform(config_data)
        assert response_dict['data']['queries'] == data['queries']
        assert response_dict['data']['filters'] == data['filters']
        assert response_dict['data']['type'] == 'default'

    def test_get_configs_with_all_valid_payload_value(self, client, url_prefix, token, options, node, default_query, default_filter, packs, queries):
        """
        Test-case with all valid payload value and without existing node and config data,
        expected output:- status is success, and
        a response dict data with key values are options, queries, packs, filters and file_paths
        """
        self.payload['platform'] = 'windows'
        self.payload['arch'] = 'x86'
        self.payload['host_identifier'] = 'foobar'
        resp = client.post(url_prefix + '/configs/view', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        nod = hosts_dao.get_node_by_host_identifier('foobar')
        data = nod.get_config()
        assert response_dict['data']['options'] == data['options']
        assert response_dict['data']['queries'] == data['queries']
        assert response_dict['data']['packs'] == data['packs']
        assert response_dict['data']['filters'] == data['filters']
        assert response_dict['data']['file_paths'] == {}


class TestToggleConfigByPlatform:
    """
    test-case inside this block where these payloads values are used,
    all are compulsory payload value and of str type as well as for values
    we have some choices like for paltform we have windows/linux/darwin",
    for arch we have x86/x86_64 and for type we have default/shallow/deep,
    so if value is not passed or passed any other value which is not
    matched with the given choices values, then it will return 400 i.e., bad request
    """
    payload = {'platform': None, 'arch': None, 'type': None}

    def test_toggle_config_without_payload(self, client, url_prefix, token):
        """
        Test-case without payload and without existing config data
        expected output:- status_code is 400
        """
        resp = client.put(url_prefix + '/configs/toggle', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_toggle_config_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload is empty dictionary and without existing config data
        expected output:- status_code is 400
        """
        resp = client.put(url_prefix + '/configs/toggle', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_toggle_config_with_payloads_value_none(self, client, url_prefix, token):
        """
        Test-case with payload values are none and without existing config data
        expected output:- status_code is 400
        """
        resp = client.put(url_prefix + '/configs/toggle', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_toggle_config_with_payloads_value_empty_str(self, client, url_prefix, token):
        """
        Test-case with payload values are empty str and without existing config data
        expected output:- status_code is 400
        """
        self.payload['platform'] = ''
        self.payload['arch'] = ''
        self.payload['type'] = ''
        resp = client.put(url_prefix + '/configs/toggle', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 400

    def test_toggle_config_with_payload_values(self, client, url_prefix, token):
        """
        Test-case with all payload values and without existing config data
        expected output:- status is success
        """
        self.payload['platform'] = 'windows'
        self.payload['arch'] = 'x86'
        self.payload['type'] = 'shallow'
        resp = client.put(url_prefix + '/configs/toggle', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'

    def test_toggle_config_with_invalid_method(self, client, url_prefix, token, config):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.get(url_prefix + '/configs/toggle', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_toggle_configs_with_payload_values(self, client, url_prefix, token, config):
        """
        Test-case with all payload values and without existing config data
        expected output:- status is success
        """
        self.payload['platform'] = 'windows'
        self.payload['arch'] = 'x86'
        self.payload['type'] = 'shallow'
        resp = client.put(url_prefix + '/configs/toggle', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
