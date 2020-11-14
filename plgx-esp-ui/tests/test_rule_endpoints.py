"""
All Test-Case required client, url_prefix and token,
and these all we need to just pass as parameters in the function.
"""

from flask_restplus import marshal

from polylogyx.dao import rules_dao
from polylogyx.wrappers import rule_wrappers
import json

conditions = {
            "rules":[
                {
                    "id": "column",
                    "type": "stringÃ¢â‚¬Â¨",
                    "field": "column",
                    "input": "text",
                    "value": [
                        "targÃ¢â‚¬Â¨et_name", "\\\\services\\\\NetlogÃ¢â‚¬Â¨on\\\\Parameters\\\\DisablePasswordChangÃ¢â‚¬Â¨e"
                    ],
                    "operator": "column_contains"
                },
                {
                    "id": "column",
                    "type": "stringÃ¢â‚¬Â¨",
                    "field": "column",
                    "input": "text",
                    "value": [
                        "action", "REG_SETVALUE"
                    ],
                    "operator": "column_equal"
                }
            ],
            "valid": True,
            "condition": "AND"
        }


class TestGetRuleList:
    """
    Test-case inside this block where these payloads are used,
    both payloads value are optional and value should be integer type.
    """
    payload = {'start': None, 'limit': None}

    def test_rule_list_without_payload(self,client, url_prefix, token):
        """
        Test-case without payloads and without existing rule data,
        expected output:- status is success, and
        count of rule i.e., 0 and resultant data is empty list in this case
        """
        resp = client.post(url_prefix + '/rules', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 0
        assert response_dict['data']['results'] == []

    def test_rule_list_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload is empty dictionary and without existing rule data,
        expected output:- status is success, and
        count of rule i.e., 0 and resultant data is empty list in this case
        """
        resp = client.post(url_prefix + '/rules', headers={'x-access-token': token}, json={})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 0
        assert response_dict['data']['results'] == []

    def test_rule_list_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with payload value is none and without existing rule data,
        expected output:- status is success, and
        count of rule i.e., 0 and resultant data is empty list in this case
        """
        resp = client.post(url_prefix + '/rules', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 0
        assert response_dict['data']['results'] == []

    def test_rule_list_with_payload(self, client, url_prefix, token):
        """
        Test-case with valid payload value and without existing rule data,
        expected output:- status is success, and
        count of rule i.e., 0 and resultant data is empty list in this case
        """
        self.payload['start'] = 0
        self.payload['limit'] = 5
        resp = client.post(url_prefix + '/rules', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 0
        assert response_dict['data']['results'] == []

    def test_rule_list_with_invalid_method(self, client, url_prefix, token, rule):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.put(url_prefix + '/rules', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

    def test_rule_list_without_payloads(self,client, url_prefix, token, rule):
        """
        Test-case without payloads and with existing rule data,
        expected output:- status is success, and
        count of rule i.e., 1 in this case and resultant data
        """
        resp = client.post(url_prefix + '/rules', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        data = marshal(rules_dao.get_all_rules().offset(None).limit(None).all(), rule_wrappers.rule_wrapper)
        assert response_dict['data']['results'] == data

    def test_rule_list_with_payloads_empty_dict(self, client, url_prefix, token, rule):
        """
        Test-case with payload is empty dictionary and with existing rule data,
        expected output:- status is success, and
        count of rule i.e., 1 in this case and resultant data
        """
        resp = client.post(url_prefix + '/rules', headers={'x-access-token': token}, json={})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        data = marshal(rules_dao.get_all_rules().offset(None).limit(None).all(), rule_wrappers.rule_wrapper)
        assert response_dict['data']['results'] == data

    def test_rule_list_with_payloads_value_none(self, client, url_prefix, token, rule):
        """
        Test-case with payload value is None and with existing rule data,
        expected output:- status is success, and
        count of rule i.e., 1 in this case and resultant data
        """
        resp = client.post(url_prefix + '/rules', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        data = marshal(rules_dao.get_all_rules().offset(None).limit(None).all(), rule_wrappers.rule_wrapper)
        assert response_dict['data']['results'] == data

    def test_rule_list_with_payloads(self, client, url_prefix, token, rule):
        """
        Test-case with valid payload value and with existing rule data,
        expected output:- status is success, and
        count of rule i.e., 1 in this case and resultant data
        """
        self.payload['start'] = 0
        self.payload['limit'] = 5
        resp = client.post(url_prefix + '/rules', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['count'] == 1
        data = marshal(rules_dao.get_all_rules().offset(None).limit(None).all(), rule_wrappers.rule_wrapper)
        assert response_dict['data']['results'] == data


class TestAddRuleList:
    """
    Test-case inside this block where these payloads are used,
    out of all payload values only name and conditions value are compulsory values,
    remaining all are optional values, so if name and conditions are not passed,
    it will return 400 i.e., bad request, and
    some of the payloads value have default value like, severity values(
    INFO/CRITICAL/WARNING), status values(ACTIVE/INACTIVE), type values(
    DEFAULT/MITRE), tactics values(initial-access/execution/persistence/privilege-escalation/
    defense-evasion/credential-access/discovery/lateral-movement/collection/
    command-and-control/exfiltration) we have to choose any one of these
    """
    payloads = {
        'alerters': None, 'name': None, 'description': None, 'conditions': None,
        'recon_queries': None, 'severity': None, 'status': None, 'type': None,
        'tactics': None, 'technique_id': None
    }

    def test_add_rule_list_without_payload(self, client, url_prefix, token):
        """
        Test-case without payloads and without existing rule data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/rules/add', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_add_rule_list_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload is empty dictionary and without existing rule data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/rules/add', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_add_rule_list_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with payload value is none and without existing rule data,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/rules/add', headers={'x-access-token': token}, json=self.payloads)
        assert resp.status_code == 400

    def test_add_rule_list_with_compulsory_payload_value(self, client, url_prefix, token):
        """
        Test-case with only payload value of name and
        conditions and without existing rule data,
        expected output:- status is success, and rule_id
        """
        payload = {'name': 'test', 'conditions': conditions}
        resp = client.post(url_prefix + '/rules/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['rule_id'] == 1

    def test_add_rule_list_with_compulsory_payload_value_and_with_valid_choices(self, client, url_prefix, token):
        """
        Test-case with payloads values are name, conditions, status(ACTIVE/INACTIVE),
        type tactics, and technique_id without existing rule data,
        expected output:- status is success, and rule_id i.e., 1 in this case
        """
        payload = {
            'name': 'test', 'conditions': conditions, 'type': 'MITRE', 'status': 'ACTIVE',
            'tactics': 'execution', 'technique_id': 'T1051'
        }
        resp = client.post(url_prefix + '/rules/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['rule_id'] == 1

    def test_add_rule_list_with_all_payload_values(self, client, url_prefix, token):
        """
        Test-case with all payloads values without existing rule data,
        expected output:- status is success, and rule_id i.e., 1 in this case
        """
        payload = {
            'alerters': ['tset', 'test12'], 'name': 'test', 'description': 'tseting descriptions',
            'conditions': conditions, 'recon_queries': [''], 'severity':'WARNING', 'type': 'MITRE',
            'status': 'ACTIVE', 'tactics': 'execution', 'technique_id': 'T1055'
        }
        resp = client.post(url_prefix + '/rules/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['rule_id'] == 1

    def test_rule_list_with_invalid_method(self, client, url_prefix, token, rule):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.put(url_prefix + '/rules/add', headers={'x-access-token': token}, json=self.payloads)
        assert resp.status_code == 405

    def test_add_rule_lists_with_compulsory_payload_value(self, client, url_prefix, token, rule):
        """
        Test-case with only payload value of name and
        conditions and with existing rule data with payload rule_name,
        expected output:- status is failure
        """
        payload = {'name': 'testrule', 'conditions': conditions}
        resp = client.post(url_prefix + '/rules/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_add_rules_lists_with_compulsory_payload_value(self, client, url_prefix, token, rule):
        """
        Test-case with only payload value of name and
        conditions and with existing rule data without payload rule_name,
        expected output:- status is success, and rule_id
        """
        payload = {'name': 'test', 'conditions': conditions}
        resp = client.post(url_prefix + '/rules/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['rule_id'] == 2

    def test_add_rule_lists_with_compulsory_payload_value_and_with_valid_choices(self, client, url_prefix, token, rule):
        """
        Test-case with payloads values are name, conditions, status(ACTIVE/INACTIVE),
        type tactics, and technique_id with existing rule data,
        expected output:- status is failure
        """
        payload = {
            'name': 'testrule', 'conditions': conditions, 'type': 'MITRE', 'status': 'ACTIVE',
            'tactics': 'execution', 'technique_id': 'T105'
        }
        resp = client.post(url_prefix + '/rules/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_add_rules_lists_with_compulsory_payload_value_and_with_valid_choices(self, client, url_prefix, token, rule):
        """
        Test-case with payloads values are name, conditions, status(ACTIVE/INACTIVE),
        type tactics, and technique_id with existing rule data but not same payload value of name,
        expected output:- status is success, and rule_id i.e., 2 in this case
        """
        payload = {
            'name': 'test', 'conditions': conditions, 'type': 'MITRE', 'status': 'ACTIVE',
            'tactics': 'execution', 'technique_id': 'T1052'
        }
        resp = client.post(url_prefix + '/rules/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['rule_id'] == 2

    def test_add_rule_list_with_all_payloads_values(self, client, url_prefix, token, rule):
        """
        Test-case with all payloads values with existing rule data,
        expected output:- status is failure
        """
        payload = {
            'alerters': ['tset', 'test12'], 'name': 'testrule', 'description': 'tseting descriptions',
            'conditions': conditions, 'recon_queries': [''], 'severity':'WARNING', 'type': 'MITRE',
            'status': 'ACTIVE', 'tactics': 'execution', 'technique_id': 'T105'
        }
        resp = client.post(url_prefix + '/rules/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_add_rule_lists_with_all_payloads_values(self, client, url_prefix, token, rule):
        """
        Test-case with all payloads values with existing rule data but rule_name is different,
        expected output:- status is success, and rule_id i.e., 2 in this case
        """
        payload = {
            'alerters': ['tset', 'test12'], 'name': 'test', 'description': 'tseting descriptions',
            'conditions': conditions, 'recon_queries': [''], 'severity':'WARNING', 'type': 'MITRE',
            'status': 'ACTIVE', 'tactics': 'execution', 'technique_id': 'T1057'
        }
        resp = client.post(url_prefix + '/rules/add', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['rule_id'] == 2


class TestGetRuleById:

    def test_get_rule_by_invalid_id_without_existing_rule(self, client, url_prefix, token):
        """
        Test-case with invalid rule-id which is passing through url,
        and without existing rule data,
        expected output:- status is failure
        """
        resp = client.get(url_prefix + '/rules/5', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_rule_by_valid_id_without_existing_rule(self, client, url_prefix, token):
        """
        Test-case with valid rule-id which is passing through url,
        and without existing rule data,
        expected output:- status is failure
        """
        resp = client.get(url_prefix + '/rules/1', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_rule_by_id_with_invalid_method(self, client, url_prefix, token, rule):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.put(url_prefix + '/rules/1', headers={'x-access-token': token})
        assert resp.status_code == 405

    def test_get_rule_by_invalid_id_with_existing_rule(self, client, url_prefix, token, rule):
        """
        Test-case with invalid rule-id which is passing through url,
        and without existing rule data,
        expected output:- status is failure
        """
        resp = client.get(url_prefix + '/rules/5', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_get_rule_by_valid_id_with_existing_rule(self, client, url_prefix, token, rule):
        """
        Test-case with valid rule-id which is passing through url,
        and without existing rule data,
        expected output:- status is success, and
        resultant rule data
        """
        resp = client.get(url_prefix + '/rules/1', headers={'x-access-token': token})
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == marshal(rules_dao.get_rule_by_id(1), rule_wrappers.rule_wrapper)


class TestUpdateRuleById:
    """
        Test-case inside this block where these payloads are used,
        out of all payload values only name and conditions value are compulsory values,
        remaining all are optional values, so if name and conditions are not passed,
        it will return 400 i.e., bad request, and
        some of the payloads value have default value like, severity values(
        INFO/CRITICAL/WARNING), status values(ACTIVE/INACTIVE), type values(
        DEFAULT/MITRE), tactics values(initial-access/execution/persistence/privilege-escalation/
        defense-evasion/credential-access/discovery/lateral-movement/collection/
        command-and-control/exfiltration) we have to choose any one of these
        """
    payloads = {
        'alerters': None, 'name': None, 'description': None, 'conditions': None,
        'recon_queries': None, 'severity': None, 'status': None, 'type': None,
        'tactics': None, 'technique_id': None
    }

    def test_update_rule_list_without_payload(self, client, url_prefix, token):
        """
        Test-case without payloads and without existing rule data,
        and valid/invalid rule_id which is passing through url,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/rules/1', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_update_rule_list_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-case with payload is empty dictionary and without existing rule data,
        and valid/invalid rule_id which is passing through url,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/rules/2', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_update_rule_list_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-case with payload value is none and without existing rule data,
        and valid/invalid rule_id which is passing through url,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/rules/1', headers={'x-access-token': token}, json=self.payloads)
        assert resp.status_code == 400

    def test_update_rule_list_with_compulsory_payload_value(self, client, url_prefix, token):
        """
        Test-case with only payload value of name and
        conditions and without existing rule data,
        and valid/invalid rule_id which is passing through url,
        expected output:- status is failure
        """
        payload = {'name': 'test', 'conditions': conditions}
        resp = client.post(url_prefix + '/rules/1', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_update_rule_list_with_compulsory_payload_value_and_with_valid_choices(self, client, url_prefix, token):
        """
        Test-case with payloads values are name, conditions, status(ACTIVE/INACTIVE),
        type tactics, and technique_id without existing rule data,
        and valid/invalid rule_id which is passing through url,
        expected output:- status is failure
        """
        payload = {
            'name': 'test', 'conditions': conditions, 'type': 'MITRE', 'status': 'ACTIVE',
            'tactics': 'execution', 'technique_id': 'T105'
        }
        resp = client.post(url_prefix + '/rules/2', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_update_rule_list_with_all_payload_values(self, client, url_prefix, token):
        """
        Test-case with all payloads values without existing rule data,
        and valid/invalid rule_id which is passing through url,
        expected output:- status is failure
        """
        payload = {
            'alerters': ['tset', 'test12'], 'name': 'test', 'description': 'tseting descriptions',
            'conditions': conditions, 'recon_queries': [''], 'severity': 'WARNING', 'type': 'MITRE',
            'status': 'ACTIVE', 'tactics': 'execution', 'technique_id': 'T105'
        }
        resp = client.post(url_prefix + '/rules/1', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'

    def test_update_rule_list_with_invalid_method(self, client, url_prefix, token, rule):
        """
        Test-case with invalid request method,
        expected output:- status code is 405
        """
        resp = client.delete(url_prefix + '/rules/1', headers={'x-access-token': token}, json=self.payloads)
        assert resp.status_code == 405

    def test_update_rule_lists_with_compulsory_payload_value(self, client, url_prefix, token, rule):
        """
        Test-case with only payload value of name and
        conditions and with existing rule data with payload rule_name,
        and valid rule_id which is passing through url,
        expected output:- status is success, and
        resultant rule data
        """
        payload = {'name': 'testrule', 'conditions': conditions}
        resp = client.post(url_prefix + '/rules/1', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == marshal(rules_dao.get_rule_by_id(1), rule_wrappers.rule_wrapper)

    def test_update_rules_lists_with_compulsory_payload_value(self, client, url_prefix, token, rule):
        """
        Test-case with only payload value of name and
        conditions and with existing rule data without payload rule_name,
        and valid rule_id which is passing through url,
        expected output:- status is success, and
        resultant rule data
        """
        payload = {'name': 'test', 'conditions': conditions}
        resp = client.post(url_prefix + '/rules/1', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == marshal(rules_dao.get_rule_by_id(1), rule_wrappers.rule_wrapper)

    def test_update_rules_lists_with_compulsory_payload_value_and_with_valid_choices(self, client, url_prefix, token,
                                                                                  rule):
        """
        Test-case with payloads values are name, conditions, status(ACTIVE/INACTIVE),
        type tactics, and technique_id with existing rule data but not same payload value of name,
        and valid rule_id which is passing through url,
        expected output:- status is success, and
        resultant rule data
        """
        payload = {
            'name': 'test', 'conditions': conditions, 'type': 'MITRE', 'status': 'ACTIVE',
            'tactics': 'execution', 'technique_id': 'T1067'
        }
        resp = client.post(url_prefix + '/rules/1', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == marshal(rules_dao.get_rule_by_id(1), rule_wrappers.rule_wrapper)

    def test_update_rule_list_with_all_payloads_values(self, client, url_prefix, token, rule):
        """
        Test-case with all payloads values with existing rule data,
        and valid rule_id which is passing through url,
        expected output:- status is success, and
        resultant rule data
        """
        payload = {
            'alerters': ['tset', 'test12'], 'name': 'testrule', 'description': 'tseting descriptions',
            'conditions': conditions, 'recon_queries': [''], 'severity': 'WARNING', 'type': 'MITRE',
            'status': 'ACTIVE', 'tactics': 'execution', 'technique_id': 'T1038'
        }
        resp = client.post(url_prefix + '/rules/1', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == marshal(rules_dao.get_rule_by_id(1), rule_wrappers.rule_wrapper)

    def test_add_rule_lists_with_all_payloads_values(self, client, url_prefix, token, rule):
        """
        Test-case with all payloads values with existing rule data but rule_name is different,
        and valid rule_id which is passing through url,
        expected output:- status is success, and
        resultant rule data
        """
        payload = {
            'alerters': ['tset', 'test12'], 'name': 'test', 'description': 'tseting descriptions',
            'conditions': conditions, 'recon_queries': [''], 'severity': 'WARNING', 'type': 'MITRE',
            'status': 'ACTIVE', 'tactics': 'execution', 'technique_id': 'T1047'
        }
        resp = client.post(url_prefix + '/rules/1', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data'] == marshal(rules_dao.get_rule_by_id(1), rule_wrappers.rule_wrapper)

    def test_add_rule_lists_with_invalid_rule_id(self, client, url_prefix, token, rule):
        """
        Test-case with all payloads values with existing rule data but rule_name is different,
        and invalid rule_id which is passing through url,
        expected output:- status is failure,
        """
        payload = {
            'alerters': ['tset', 'test12'], 'name': 'test', 'description': 'tseting descriptions',
            'conditions': conditions, 'recon_queries': [''], 'severity': 'WARNING', 'type': 'MITRE',
            'status': 'ACTIVE', 'tactics': 'execution', 'technique_id': 'T105'
        }
        resp = client.post(url_prefix + '/rules/12', headers={'x-access-token': token}, json=payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'failure'


class TestGetTactics:
    """
    test-case inside this block where this payloads value is used,
    this is compulsory payload value of string type, so if this value is not passed
    or passing none value or any other value than string, it will return 400 i.e., bad request.
    Note:- This test-cases required internet connection
    """
    payload = {'technique_ids': None}

    def test_get_tactics_without_payload(self, client, url_prefix, token):
        """
        Test-Case without payloads,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/rules/tactics', headers={'x-access-token': token})
        assert resp.status_code == 400

    def test_get_tactics_with_payload_empty_dict(self, client, url_prefix, token):
        """
        Test-Case with payload is empty dictionary,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/rules/tactics', headers={'x-access-token': token}, json={})
        assert resp.status_code == 400

    def test_get_tactics_with_payload_value_none(self, client, url_prefix, token):
        """
        Test-Case with payload value is none,
        expected output:- status_code is 400
        """
        resp = client.post(url_prefix + '/rules/tactics', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 400

    def test_get_tactics_with_payload_value_empty_str(self, client, url_prefix, token):
        """
        Test-Case with payload value is empty str,
        expected output:- status is success, and
        tactics is empty list and description is empty str in this case
        """
        self.payload['technique_ids'] = ''
        resp = client.post(url_prefix + '/rules/tactics', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['tactics'] == []
        assert response_dict['data']['description'] == ''

    def test_get_tactics_with_invalid_technique_id(self, client, url_prefix, token):
        """
        Test-Case with invalid technique id,
        expected output:- status is success, and
        tactics is empty list and description is empty str in this case
        """
        self.payload['technique_ids'] = 'foobar'
        resp = client.post(url_prefix + '/rules/tactics', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['tactics'] == []
        assert response_dict['data']['description'] == ''

    def test_get_tactics_with_valid_technique_id(self, client, url_prefix, token):
        """
        Test-Case with valid payloads value of technique_ids,
        expected output:- status is success,  and
        tactics is empty list and description is empty str in this case
        """
        self.payload['technique_ids'] = 'T108'
        resp = client.post(url_prefix + '/rules/tactics', headers={'x-access-token': token}, data=self.payload)
        assert resp.status_code == 200
        response_dict = json.loads(resp.data)
        assert response_dict['status'] == 'success'
        assert response_dict['data']['tactics'] == []
        assert response_dict['data']['description'] == ''

    def test_get_tactics_with_invalid_method(self, client, url_prefix, token):
        """
       Test-case with invalid request method,
       expected output:- status code is 405
       """
        resp = client.delete(url_prefix + '/rules/tactics', headers={'x-access-token': token}, json=self.payload)
        assert resp.status_code == 405

