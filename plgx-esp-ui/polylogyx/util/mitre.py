from stix2 import TAXIICollectionSource, Filter
from taxii2client import Collection
# Initialize dictionary to hold Enterprise ATT&CK content
attack = {}
# Establish TAXII2 Collection instance for Enterprise ATT&CK
collection = Collection("https://cti-taxii.mitre.org/stix/collections/95ecc380-afe9-11e4-9b6c-751b66dd541e/")

class MitreApi:
    def get_tactics_by_technique_id(self,technique_ids):

        # Supply the collection to TAXIICollection
        tc_source = TAXIICollectionSource(collection)
        # Create filters to retrieve content from Enterprise ATT&CK
        filter_objs = {
            "techniques": [
            Filter('type', '=', "attack-pattern"),
            Filter('external_references.external_id', 'in', technique_ids)]
        }
        for key in filter_objs:
            attack[key] = tc_source.query(filter_objs[key])
        # For visual purposes, print the first technique received
        tactics=[]
        response_data={}
        description=""
        response_data['tactics']={}
        if len( attack["techniques"])>0:
            for technique in attack["techniques"]:
                for tactic in technique["kill_chain_phases"]:
                    tactics.append(tactic['phase_name'])
                description=description+"\n"+technique['description']
        response_data['tactics']=tactics
        response_data['description']=description
        return response_data


class TestMail:
    def test(self ,smtp=None,username=None,password=None,recipients=[]):
        is_credentials_valid=True
        import sys

        from smtplib import SMTP_SSL as SMTP  # this invokes the secure SMTP protocol (port 465, uses SSL)

        from email.mime.text import MIMEText
        SMTPserver = smtp
        sender ='username'
        destination =recipients

        USERNAME =username
        PASSWORD =password

        # typical values for text_subtype are plain, html, xml
        text_subtype = 'plain'

        content = """\
        Test message
        """

        subject = "Sent from PolyLogyx"



        try:
            msg = MIMEText(content, text_subtype)
            msg['Subject'] = subject
            msg['From'] = sender  # some SMTP servers will do this automatically, not all

            conn = SMTP(SMTPserver)
            conn.set_debuglevel(False)
            conn.login(USERNAME, PASSWORD)
            try:
                conn.sendmail(sender, destination, msg.as_string())
            except:
                is_credentials_valid=False
            finally:
                conn.quit()

        except Exception as e:
            print(e)
            is_credentials_valid = False
        return is_credentials_valid