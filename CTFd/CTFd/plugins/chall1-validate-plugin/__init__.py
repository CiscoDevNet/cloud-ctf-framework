from os import path
import yaml
import random
from kubernetes import client as k8sclient
from kubernetes import config
import boto3
import requests

def validate_chal1():
    return "testing return chal1"


def load(app):
    @app.route('/plugins/chall1-validate-plugin', methods=['POST', 'GET'])
    def view_plugins_chall1_validate():

        #My IP validation
        client = boto3.client('ec2', aws_access_key_id="xxxxxxxxxxxxxxxxxxx", aws_secret_access_key="xxxxxxxxxxxxxxxxxxx",
                              region_name="ap-south-1" )
        response = client.describe_instances(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']},{'Name': 'tag:Name', 'Values': ['CloudCTFchall1']}]
        )
        url=response['Reservations'][0]['Instances'][0]['PublicIpAddress']
        url= 'http://' + url
        try:
            resp = requests.get(url, timeout=3) #3 seconds
        except Exception:
            return {"Note":"Challenge Failed, Please try again"}
        
        
        #My External IP validation
        url= 'https://emlxxz79gg.execute-api.ap-south-1.amazonaws.com/dev'

        extresp = requests.request("GET", url)


        if resp.status_code == 200:
            if 'timed' in extresp.text:
                return {"Note":"Challenge Validated Successfully --- flag{Cloud_security_Infra_important}"}
            else:
                return {"Note":"Challenge Failed, Please try again"}
        else:
            return {"Note":"Challenge Failed, Please try again"}
