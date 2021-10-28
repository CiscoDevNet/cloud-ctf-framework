from os import path
import yaml
import random
from kubernetes import client as k8sclient
from kubernetes import config
import boto3

JOB_NAME = "test-"

def create_job_object():
    # Configureate Pod template container
    access_key = k8sclient.V1EnvVar(
        name="AWS_ACCESS_KEY_ID",
        value="xxxxxxxxxxxxx")
    secret_key = k8sclient.V1EnvVar(
        name="AWS_SECRET_ACCESS_KEY",
        value="xxxxxxxxxxxxx")
    image_pull_secrets = k8sclient.V1LocalObjectReference(
         name="ankushk2-pull-secret")
    container = k8sclient.V1Container(
        name="test",
        image="containers.cisco.com/ankushk2/ctf",
        env=[access_key,secret_key])
    # Create and configurate a spec section
    template = k8sclient.V1PodTemplateSpec(
        metadata=k8sclient.V1ObjectMeta(labels={"app": "pi"}),
        spec=k8sclient.V1PodSpec(restart_policy="Never", containers=[container],image_pull_secrets=[image_pull_secrets]))
    # Create the specification of deployment
    spec = k8sclient.V1JobSpec(
        template=template,
        backoff_limit=4)
    # Instantiate the job object
    job = k8sclient.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=k8sclient.V1ObjectMeta(generate_name=JOB_NAME),
        spec=spec)

    return job


def create_job(api_instance, job):
    api_response = api_instance.create_namespaced_job(
        body=job,
        namespace="default")
    print("Job created. status='%s'" % str(api_response.status))

def load(app):
    @app.route('/plugins/jgroetzi-test-1', methods=['POST', 'GET'])
    def view_plugins_jgroetzi_test1():


        client = boto3.client('ec2',aws_access_key_id="xxxxxxxxxxxxx", aws_secret_access_key="xxxxxxxxxxxxx",region_name='ap-south-1')
        a= client.describe_vpcs()
        b=a['Vpcs']
        dict={}
        #print('no of vpc is', len(b))



        session = boto3.Session(region_name="ap-south-1")
        ec2 = session.resource('ec2',aws_access_key_id="xxxxxxxxxxxxx", aws_secret_access_key="xxxxxxxxxxxxx")
        instances = ec2.instances.filter(
                Filters=[{'Name': 'instance-state-name', 'Values': ['running']},{'Name': 'tag:Name', 'Values': ['CloudCTFchall1']}])
        count=0
        for instance in instances:
            print(instance.id, instance.instance_type)
            count=count+1



        if len(b)>=5:
            return {"Note":"VPC greater than 5...In AWS, by default, only 5 VPC's are allowed. Please delete one or more VPC to get the challenge deployed"}
        elif count>=1:
            return {"Note":"Challenge Already Deployed and UP and Running"}
        else:
            config.load_kube_config()
            batch_v1 = k8sclient.BatchV1Api()
            job = create_job_object()
            create_job(batch_v1, job)

            return {"Note":"Challenge Deployed Successfully"}
