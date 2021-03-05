import requests
from requests.auth import HTTPBasicAuth


class ApiValidator:
    resource = '44d88612fea8a8f36de82e1278abb02f'

    def validate_threat_intel_key(self, intel_name, payload):
        if intel_name == 'virustotal':
            return self.is_valid_api_virustotal(payload)
        elif intel_name == 'ibmxforce':
            return self.is_valid_api_ibmxforce(payload)
        elif intel_name == 'alienvault':
            return self.is_valid_api_otx(payload)
        else:
            return

    def is_valid_api_virustotal(self, payload):
        vt_api_url = 'https://www.virustotal.com/vtapi/v2/file/report'
        vt_params = {'apikey': payload['key'], 'resource': self.resource}
        vt_response = requests.get(vt_api_url, params=vt_params)
        if vt_response.status_code == 200:
            return True, None
        elif vt_response.status_code == 401 or vt_response.status_code == 403:
            return False, None
        else:
            return True, vt_response

    def is_valid_api_ibmxforce(self, payload):
        ibm_api_url = 'https://api.xforce.ibmcloud.com:443/malware/' + self.resource
        auth = HTTPBasicAuth(payload['key'], payload['pass'])
        ibm_response = requests.get(ibm_api_url, params='', auth=auth, timeout=30)
        if ibm_response.status_code == 200:
            return True, None
        elif ibm_response.status_code == 401 or ibm_response.status_code == 403:
            return False, None
        else:
            return True, ibm_response

    def is_valid_api_otx(self, payload):
        otx_api_url = 'https://otx.alienvault.com/api/v1/pulses/subscribed?page=1'
        otx_params = {'X-OTX-API-KEY': payload['key'].strip()}
        otx_response = requests.get(otx_api_url, headers=otx_params)
        if otx_response.status_code == 200:
            return True, None
        elif otx_response.status_code == 401 or otx_response.status_code == 403:
            return False, None
        else:
            return True, otx_response

