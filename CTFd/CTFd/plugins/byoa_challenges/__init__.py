import collections
import json
import os
import pprint

import boto3
from attr import dataclass
from flask import Blueprint, render_template, Response, request
from kubernetes.client import V1Job, ApiException
from sqlalchemy.orm.attributes import flag_modified

from CTFd.models import Challenges, db, TeamFieldEntries
# from CTFd.schemas.fields import TeamFieldEntriesSchema
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES, BaseChallenge
from CTFd.models import Teams
from CTFd.utils.user import get_current_team, is_admin, authed
from CTFd.schemas.teams import TeamSchema
from CTFd.utils.logging import log
from typing import Union, List, Dict, Optional
from kubernetes import client as k8sclient
from kubernetes import config
from .byoa_exception import ByoaException
from functools import wraps
from .challenge1 import validate_chalenge as validate_chalenge1
from .challenge2 import validate_chalenge as validate_chalenge2
from .challenge5 import validate_chalenge as validate_chalenge5
from .challenge8 import validate_chalenge as validate_chalenge8
from .challenge9 import validate_chalenge as validate_chalenge9
from .challenge11 import validate_chalenge as validate_chalenge11
from .challenge12 import validate_chalenge as validate_chalenge12
from .challenge13 import validate_chalenge as validate_chalenge13
from .challenge3 import validate_chalenge as validate_chalenge3
from .challenge14 import validate_chalenge as validate_chalenge14
@dataclass
class ByoaTeamAwsInfo:
    AWS_REGION: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str

@dataclass
class ByoaMetadata:
    admin_job_url_deploy: Optional[str] = None
    admin_job_url_destroy: Optional[str] = None
    is_admin: bool = False

@dataclass
class ByoaChallengeValidationReturn:
    message: str
    result: bool
    flag: Optional[str] = None


class ByoaChallengeEntry(Challenges):
    '''
    challenge model for storing challenges
    '''
    __mapper_args__ = {'polymorphic_identity': 'byoa'}
    challenge_id = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"), primary_key=True
    )
    # Stores the base uri for where validate/deploy/destroy
    api_base_uri = db.Column(db.String(128))

    def __init__(self, api_base_uri, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_base_uri = api_base_uri

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class ByoaChallengeDeploys(db.Model):
    '''
    This model is for tracking byoa deployments and statuses
    '''
    id = db.Column(
        db.Integer, autoincrement=True, primary_key=True
    )
    challenge_id = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE")
    )
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id', ondelete="CASCADE"))
    # NOT_DEPLOYED, DEPLOYING, DEPLOYED, FAILED_DEPLOY, SOLVED, FAILED_DESTROY, DESTROYED
    deploy_status = db.Column(db.String(64), default="NOT_DEPLOYED")
    # stores random schemaless info, like messages from the deploy, or variables from the deploy, etc.
    ctf_metadata = db.Column(db.JSON, default=None)

    k8s_api = None
    byoa_metadata: ByoaMetadata = None

    def __init__(self, challenge_id, team_id, ctf_metadata=None, k8s_api=None, byoa_metadata=None):
        self.challenge_id = challenge_id
        self.team_id = team_id
        self.ctf_metadata = ctf_metadata
        self.k8s_api = k8s_api
        if byoa_metadata is None:
            self.get_byoa_metadata()
        else:
            self.byoa_metadata = byoa_metadata

    def get_byoa_metadata(self):
        if not self.byoa_metadata:
            self.byoa_metadata = ByoaMetadata(is_admin=is_admin())

        return self.byoa_metadata

    def get_byoa_team_aws_info(self) -> ByoaTeamAwsInfo:
        # AWS_REGION
        team: Teams = get_current_team()

        for f in team.field_entries:
            if f.name == "AWS_SECRET_ACCESS_KEY":
                aws_secret_access_key = f.value
            elif f.name == "AWS_ACCESS_KEY_ID":
                aws_access_key_id = f.value
            elif f.name == "AWS_REGION":
                aws_region = f.value

        #field_entry = TeamFieldEntries.query.join(Teams).filter(Teams.id == self.team_id, TeamFieldEntries.name =='AWS_REGION').first()
        #aws_region = field_entry.value

        # AWS_ACCESS_KEY_ID
        #field_entry = TeamFieldEntries.query.filter_by(name='AWS_ACCESS_KEY_ID').first()
        #aws_access_key_id = field_entry.value

        # AWS_SECRET_ACCESS_KEY
        #field_entry = TeamFieldEntries.query.filter_by(name='AWS_SECRET_ACCESS_KEY').first()
        #aws_secret_access_key = field_entry.value
        return ByoaTeamAwsInfo(AWS_REGION=aws_region, AWS_ACCESS_KEY_ID=aws_access_key_id,
                               AWS_SECRET_ACCESS_KEY=aws_secret_access_key)

    def fail_deploy(self, fail_msg, status_code=500):
        self.deploy_status = "FAILED_DEPLOY"
        self.set_deploy_status_summary(fail_msg)
        raise ByoaException(fail_msg, [fail_msg], status_code, self)

    def set_deploy_status_summary(self, summary_message: str):
        md = self.ctf_metadata
        if not md:
            md = {}
        log("CiscoCTF", "ctf_metadata currently: {md}", md=md)
        md["status_summary"] = summary_message
        log("CiscoCTF", "setting summary_message to: {message}", message=summary_message)
        self.ctf_metadata = md
        flag_modified(self, "ctf_metadata")
        db.session.commit()
        log("CiscoCTF", "ctf_metadata after update status_summary: {md}", md=self.ctf_metadata)

    def destroy_challenge(self):
        if self.deploy_status not in ['DEPLOYED', 'FAILED_DEPLOY', 'FAILED_DESTROY']:
            err = "You can only destroy challenge when the deploy_status is DEPLOYED, FAILED_DEPLOY, or FAILED_DESTROY! It is currently "+self.deploy_status
            raise ByoaException(err, [err], 400, self)


        k8s_api = self.get_k8s_api()
        d_info = self.get_byoa_team_aws_info()
        bchal = ByoaChallengeEntry.query.filter_by(challenge_id=self.challenge_id).first()
        job_name=self.get_k8s_job_name('destroy', bchal.api_base_uri)
        log("CiscoCTF", "job_name is "+job_name)
        try:
            self.set_deploy_status_summary("I r destroying thangs")
            self.deploy_status = 'DESTROYING'
            db.session.commit()
            k8s_job = create_k8s_job_object(d_info, job_name, self.get_ccc_image_name('destroy', bchal.api_base_uri),
                                            {"type": "challenge-destroy", "ctf-challenge-id": str(self.challenge_id),
                                             "ctf-team-id": str(self.team_id)}, self.team_id, bchal.api_base_uri)
            job = run_k8s_job(k8s_api, k8s_job, get_k8s_namespace())
            self.set_deploy_status_summary("Destroy Job Queued Successfully")
            # log("K8s Job created. status='%s'" % str(job.status))

        except ApiException as ae:
            log("CiscoCTF", "K8s exception: {body}", body=ae.body)
            ae_dict = json.loads(ae.body)
            err = "Failed to deploy! Error (likely need to report to admin): " + ae_dict["message"]
            self.set_deploy_status_summary("I failed to destroy! Please reach out to admins for help :(")
            self.deploy_status = 'FAILED_DESTROY'
            self.set_deploy_status_summary("Failed to queue Destroy Job")
            raise ByoaException(err, [err], 500, self)

    def validate_challenge(self):
        if self.deploy_status != 'DEPLOYED':
            err = "You can only validate challenge if deploy_status is DEPLOYED! It is currently "+self.deploy_status
            raise ByoaException(err, [err], 400, self)

        challenge = self.get_challenge()
        bcd = get_or_create_byoa_cd(self.challenge_id, self.team_id)
        if challenge.api_base_uri == "challenge1":
            return validate_chalenge1(bcd)
        elif challenge.api_base_uri == "challenge2":
            return validate_chalenge2(bcd)
        elif challenge.api_base_uri == "challenge5":
            return validate_chalenge5(bcd)
        elif challenge.api_base_uri == "challenge8":
            return validate_chalenge8(bcd)
        elif challenge.api_base_uri == "challenge9":
            return validate_chalenge9(bcd)
        elif challenge.api_base_uri == "challenge11":
            return validate_chalenge11(bcd)
        elif challenge.api_base_uri == "challenge12":
            return validate_chalenge12(bcd)
        elif challenge.api_base_uri == "challenge13":
            return validate_chalenge13(bcd)
        elif challenge.api_base_uri == "challenge3":
            return validate_chalenge3(bcd)
        elif challenge.api_base_uri == "challenge14":
            return validate_chalenge14(bcd)

    def get_challenge(self) -> ByoaChallengeEntry:
        return ByoaChallengeEntry.query.filter_by(challenge_id=self.challenge_id).first()

    def get_challenge_vpc(self):
        '''

        :return: returns the VPC instance if it is able to find 1 vpc for this challenge. Returns None if no vpc found
        '''
        aws_info = self.get_byoa_team_aws_info()
        session = boto3.Session(region_name=aws_info.AWS_REGION)
        ec2 = session.resource('ec2', aws_access_key_id=aws_info.AWS_ACCESS_KEY_ID,
                               aws_secret_access_key=aws_info.AWS_SECRET_ACCESS_KEY)
        challenge_vpc_label = self.get_aws_challenge_vpc_label_name()
        instances = ec2.instances.filter(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']},
                     {'Name': 'tag:Name', 'Values': [challenge_vpc_label]}])
        # count=0
        # for instance in instances:
        #     print(instance.id, instance.instance_type)
        #     count=count+1
        if len(instances) == 1:
            return instances[0]
        if len(instances) > 1:
            # This likely means we have a bug...somewhere.
            raise Exception("Found more than 1 VPC for this challenge! This should not be possible, please ask admins for assistance.")
        return None


    def reset_challenge_deploy(self, force=False):
        if not force and self.deploy_status not in ['FAILED_DEPLOY', 'FAILED_DESTROY', 'DESTROYED']:
            err = "You can only reset a challenge deployment when it is in status FAILED_DEPLOY! It is currently "+self.deploy_status
            raise ByoaException(err, [err], 400, self)
        self.deploy_status = 'NOT_DEPLOYED'
        self.set_deploy_status_summary("I Reset thangs")

    def deploy_challenge(self):
        if self.deploy_status != 'NOT_DEPLOYED':
            err = "call to deploy_challenge and the deploy_status was not currently set to NOT_DEPLOYED! It is currently "+self.deploy_status
            raise ByoaException(err, [err], 400, self)
        self.deploy_status = 'DEPLOYING'
        self.set_deploy_status_summary("Queueing Deploy Job")
        db.session.commit()

        # Check VPC count
        try:
            vpcs = self.get_all_aws_vpcs()
        except Exception as e:
            log("CiscoCTF", "Exception when deploying: {e}", e=e)
            self.deploy_status = 'NOT_DEPLOYED'
            self.set_deploy_status_summary("Failed to start deploy. Unable to list VPCs for this account, make sure team AWS credentials are valid.")
            db.session.commit()
            raise e

        if len(vpcs)>=5:
            self.deploy_status = 'NOT_DEPLOYED'
            self.set_deploy_status_summary("Account has 5 or more VPCs. Could not deploy on last attempt. please destroy a VPC (another challege) in your account and try again.")
            db.session.commit()
        # Do the deploy
        # aws_info = self.get_byoa_team_aws_info()
        config.load_kube_config()
        batch_v1 = k8sclient.BatchV1Api()
        d_info = self.get_byoa_team_aws_info()
        chal_ref = self.get_chal_ref()
        job_name=self.get_k8s_job_name('deploy', chal_ref)
        log("CiscoCTF", "job_name is "+job_name)
        try:
            k8s_job = create_k8s_job_object(d_info, job_name, self.get_ccc_image_name('deploy', chal_ref),
                                            {"type": "challenge-deploy", "ctf-challenge-id": str(self.challenge_id),
                                            "ctf-team-id": str(self.team_id)}, self.team_id, chal_ref)
            job = run_k8s_job(batch_v1, k8s_job, get_k8s_namespace())
            # log("K8s Job created. status='%s'" % str(job.status))
            self.set_deploy_status_summary("Job Deploy Queued Successfully")

        except ApiException as ae:
            log("CiscoCTF", "K8s exception: {body}", body=ae.body)
            ae_dict = json.loads(ae.body)
            err = "Failed to deploy! Error (likely need to report to admin): " + ae_dict["message"]
            raise ByoaException(err, [err], 500, self)

        # TODO NEXT: figure out what we need to return here and how to rely info to end user inside of challenge

    def get_chal_ref(self):
        bchal = ByoaChallengeEntry.query.filter_by(challenge_id=self.challenge_id).first()
        return bchal.api_base_uri

    def get_aws_challenge_vpc_label_name(self):
        return "cisco-cloud-ctf-challenge-"+str(self.challenge_id)

    def get_all_aws_vpcs(self):
        aws_info = self.get_byoa_team_aws_info()
        # print(aws_info)
        try:
            client = boto3.client('ec2', aws_access_key_id=aws_info.AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=aws_info.AWS_SECRET_ACCESS_KEY, region_name=aws_info.AWS_REGION)

            describeVpc = client.describe_vpcs()
            return describeVpc['Vpcs']
        except Exception as e:
            err = "Failed to deploy! Make sure the AWS credentials your team provided are valid, and reach out to an admin for assistance."
            raise ByoaException(err, [err], 500, self)

    def get_k8s_job_name(self, job_type: str, chal_ref: str):
        '''
        Gets the K8s job name to be used for a K8s job.
        :param chal_ref:
        :param job_type: should be one of: deploy, destroy, validate
        :return str: string with job name. i.e. challenge1-team1-deploy
        '''
        if job_type not in ['deploy', 'destroy', 'validate']:
            raise Exception("Unknown job_type " + job_type)
        return chal_ref + '-team' + str(self.team_id) + '-' + job_type

    def get_ccc_image_name(self, job_type: str, chal_ref: str):
        '''
        Gets the containers.cisco.com image name to be used for a K8s job.
        :param job_type: should be one of: deploy, destroy, validate
        :return str: string with image name. i.e. containers.cisco.com/cloud-ctf/challenge1-deploy
        '''
        if job_type not in ['deploy', 'destroy', 'validate']:
            raise Exception("Unknown job_type " + job_type)
        return 'containers.cisco.com/cloud-ctf/' + chal_ref + '-' + job_type

    def get_k8s_job(self, job_type: str, chal_ref: str):
        job_name = self.get_k8s_job_name(job_type, chal_ref)
        namespace = get_k8s_namespace()
        config.load_kube_config()
        batch_v1 = k8sclient.BatchV1Api()
        try:
            job = batch_v1.read_namespaced_job(job_name, namespace)
        except ApiException as ae:
            log("CiscoCTF", "K8s exception: {body}", body=ae.body)
            ae_dict = json.loads(ae.body)
            if ae.reason == "NotFound":
            # if ae_dict.code == 404:
                err = "Failed get deploy job, it was unable to be found! You will need an admin to assist. Error (likely need to report to admin): " + ae_dict["message"]
                raise ByoaException(err, [err], 404, self)
            err = "Failed get deploy job! Error (likely need to report to admin): " + ae_dict["message"]
            raise ByoaException(err, [err], 500, self)

        # log("CiscoCTF", "Job fetched: {job}", job=job)
        return job

    def get_k8s_api(self) -> k8sclient.BatchV1Api:
        if not self.k8s_api:
            config.load_kube_config()
            self.k8s_api = k8sclient.BatchV1Api()
        return self.k8s_api

    def get_terraform_path(self):
        challenge = self.get_challenge()
        return get_base_terraform_path() + f"/team{self.team_id}/{challenge.api_base_uri}/terraform.tfstate"

    def get_terraform_state_dict(self):
        with open(self.get_terraform_path()) as json_file:
            data = json.load(json_file)
        return data

    def check_k8s_job(self, job_type: str):
        '''
        This function just checks the k8s jub for deploy/destroy and if it finds it is successfully finished, it will update the deploy_status
        This does not return anything, you will just use the self object (i.e. self.deploy_status will be updated after calling this if job is done)
        :param job_type:
        :return:
        '''
        # if self.deploy_status in ['NOT_DEPLOYED', 'DESTROYED', 'DEPLOYED', 'FAILED_DEPLOY', 'FAILED_DESTROY']:
        # only need to update if one of these statuses
        if self.deploy_status not in ['DEPLOYING', 'DESTROYING']:
            return
        # handle deploy
        if job_type == 'deploy':
            if self.deploy_status != 'DEPLOYING':
                err = f"Can only check deploy job when deploy_status is 'DEPLOYING', but it is currently '{self.deploy_status}'"
                raise ByoaException(err, [err], 500, self)

            job = self.get_k8s_job(job_type, self.get_chal_ref())
            orig_deploy_status = self.deploy_status
            if job._status.succeeded:
                # job is done, change to DEPLOYED
                self.deploy_status = 'DEPLOYED'
                self.set_deploy_status_summary("Job Deployed Successfully. You can now use the Validate button.")
                # db.session.commit()
                log("CiscoCTF", f"changed deploy_status from {orig_deploy_status} to {self.deploy_status}")
                return

            elif job._status.failed and job._status.failed >= 5:
                # job is done, change to DEPLOYED
                self.deploy_status = 'FAILED_DEPLOY'
                self.set_deploy_status_summary("Job Failed to run! Please contact an admin for assistance.")
                db.session.commit()
                log("CiscoCTF", f"changed deploy_status from {orig_deploy_status} to {self.deploy_status}")
                return

        elif job_type == 'destroy':
            # check current status
            if self.deploy_status != 'DESTROYING':
                err = f"Can only check destory job when deploy_status is 'DESTROYING', but it is currently '{self.deploy_status}'"
                raise ByoaException(err, [err], 500, self)

            job = self.get_k8s_job(job_type, self.get_chal_ref())
            orig_deploy_status = self.deploy_status
            if job._status.succeeded:
                # job is done, change to DEPLOYED
                batch_v1 = k8sclient.BatchV1Api()
                delete_k8s_job(batch_v1, self.get_k8s_job_name("deploy", self.get_chal_ref()), get_k8s_namespace())
                delete_k8s_job(batch_v1, self.get_k8s_job_name("destroy", self.get_chal_ref()), get_k8s_namespace())
                self.deploy_status = 'DESTROYED'
                self.set_deploy_status_summary("Successfully Destroyed this challenge. If you need to re-deploy, you can click the reset button.")
                db.session.commit()
                log("CiscoCTF", f"changed deploy_status from {orig_deploy_status} to {self.deploy_status}")
                return
            elif job._status.failed and job._status.failed >= 5:
                # job is done, change to DEPLOYED
                self.deploy_status = 'FAILED_DESTROY'
                db.session.commit()
                log("CiscoCTF", f"changed deploy_status from {orig_deploy_status} to {self.deploy_status}")
                return


class ByoaChallenge(BaseChallenge):
    id = "byoa"  # Unique identifier used to register challenges
    name = "byoa"  # Name of a challenge type
    templates = {  # Handlebars templates used for each aspect of challenge editing & viewing
        "create": "/plugins/byoa_challenges/assets/create.html",
        "update": "/plugins/byoa_challenges/assets/update.html",
        "view": "/plugins/byoa_challenges/assets/view.html",
    }
    scripts = {  # Scripts that are loaded when a template is loaded
        "create": "/plugins/byoa_challenges/assets/create.js",
        "update": "/plugins/byoa_challenges/assets/update.js",
        "view": "/plugins/byoa_challenges/assets/view.js",
    }
    # Route at which files are accessible. This must be registered using register_plugin_assets_directory()
    route = "/plugins/byoa_challenges/assets/"
    # Blueprint used to access the static_folder directory.
    blueprint = Blueprint(
        "byoa_challenges",
        __name__,
        template_folder="templates",
        static_folder="assets",
    )
    challenge_model = ByoaChallengeEntry

    @classmethod
    def read(cls, challenge):
        """
        This method is in used to access the data of a challenge in a format processable by the front end.

        :param challenge:
        :return: Challenge object, data dictionary to be returned to the user
        """
        import logging
        log("ciscoCTF", f"challenge_id is '{challenge.id}'.")
        byoac = ByoaChallengeEntry.query.filter_by(challenge_id=challenge.id).first()
        #ByoaChallengeEntry.query.with_polymorphic('*').filter_by(challenge_id=challenge.id).first() #
        data = {
            "id": challenge.id,
            "name": challenge.name,
            "value": challenge.value,
            "description": challenge.description,
            "category": challenge.category,
            "state": challenge.state,
            "max_attempts": challenge.max_attempts,
            "type": challenge.type,
            "api_base_uri": byoac.api_base_uri,
            "type_data": {
                "id": cls.id,
                "name": cls.name,
                "templates": cls.templates,
                "scripts": cls.scripts,
            }
        }
        team: Teams = get_current_team()
        if not team:
            data["deploy_status"] = "UNKNOWN_USER_IS_NOT_MEMBER_OF_A_TEAM"
        else:
            # byoac_cd = ByoaChallengeDeploys.query.filter_by(challenge_id=challenge.id,team_id=team.id).first()
            byoac_cd = get_or_create_byoa_cd(challenge.id, team.id)
            data["deploy_status"] = byoac_cd.deploy_status
        return data


def create_k8s_job_object(aws_info: ByoaTeamAwsInfo, job_name: str, container_image: str, labels: Dict, team_id: int, chal_ref: str) -> V1Job:
    """

    :param labels: K8s labels to add to the job, should be dict where key is label name and value is value of the label
    :param aws_info:
    :param job_name: use get_k8s_job_name() to get name and pass to here
    :param container_image: i.e. cloud-ctf-cloudctfbot-pull-secret
    :return:
    """
    # Configureate Pod template container
    access_key = k8sclient.V1EnvVar(
        name="TF_VAR_AWS_ACCESS_KEY_ID",
        value=aws_info.AWS_ACCESS_KEY_ID)
    secret_key = k8sclient.V1EnvVar(
        name="TF_VAR_AWS_SECRET_ACCESS_KEY",
        value=aws_info.AWS_SECRET_ACCESS_KEY)
    region = k8sclient.V1EnvVar(
        name="TF_VAR_AWS_REGION",
        value=aws_info.AWS_REGION)
    # TODO this can probably be removed? cluster should be set up to do this automatically already
    image_pull_secrets = k8sclient.V1LocalObjectReference(
        name="cloud-ctf-cloudctfbot-pull-secret")
    byoa_volume = k8sclient.V1Volume(persistent_volume_claim=k8sclient.V1PersistentVolumeClaimVolumeSource(claim_name="team-byoa-pvc"), name="vol0")
    volume_mount = k8sclient.V1VolumeMount(mount_path="/var/data/terraform", name="vol0", sub_path=f"team{team_id}/{chal_ref}")

    container = k8sclient.V1Container(
        name=job_name,
        image=container_image,
        env=[access_key, secret_key, region],
        volume_mounts=[volume_mount])
    # Create and configurate a spec section
    template = k8sclient.V1PodTemplateSpec(
        metadata=k8sclient.V1ObjectMeta(labels=labels),
        spec=k8sclient.V1PodSpec(restart_policy="Never", containers=[container],image_pull_secrets=[image_pull_secrets], volumes=[byoa_volume]))
    # Create the specification of deployment
    spec = k8sclient.V1JobSpec(
        template=template,
        backoff_limit=4)
    # Instantiate the job object
    job = k8sclient.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=k8sclient.V1ObjectMeta(name=job_name),
        spec=spec)

    return job


def run_k8s_job(api_instance: k8sclient.BatchV1Api, job: V1Job, namespace="default") -> V1Job:
    api_response = api_instance.create_namespaced_job(
        body=job,
        namespace=namespace)
    # log("Job created. status='%s'" % str(api_response.status))
    return api_response


def delete_k8s_job(api_instance: k8sclient.BatchV1Api, job_name: str, namespace="default") -> V1Job:
    api_response = api_instance.delete_namespaced_job(
        name=job_name,
        namespace=namespace,
        grace_period_seconds=0)
    # log("Job created. status='%s'" % str(api_response.status))
    return api_response


def get_or_create_byoa_cd(challenge_id, team_id) -> ByoaChallengeDeploys:
    byoa_cd = get_byoa_cd(challenge_id, team_id)
    if byoa_cd:
        return byoa_cd
    else:
        byoa_cd = ByoaChallengeDeploys(challenge_id=challenge_id, team_id=team_id)
        db.session.add(byoa_cd)
        db.session.commit()
        return byoa_cd

def get_byoa_cd(challenge_id, team_id) -> Union[ByoaChallengeDeploys, None]:
    return ByoaChallengeDeploys.query.filter_by(challenge_id=challenge_id, team_id=team_id).first()


def get_byoa_cds(**kwargs) -> collections.Iterable:
    # deployments = ByoaChallengeDeploys.query()
    # app.logger.info('CiscoCTF: I am checking the BYOA challenge deploys')
    # log(  "CiscoCTF","[{msg}]", msg="I am checking the BYOA challenge deploys")
    # return ByoaChallengeDeploys.query.filter_by(**kwargs) # This does not work... not sure what difference is, below works so w/e
    return db.session.query(ByoaChallengeDeploys.id, ByoaChallengeDeploys.challenge_id, ByoaChallengeDeploys.team_id,
                            ByoaChallengeDeploys.deploy_status).filter_by(**kwargs)


def get_byoa_cds_as_dicts(**kwargs) -> List[Dict]:
    '''
    Returns all ByoaChallengeDeploys db entries as a list of dicts
    :return:
    '''
    byoa_cd_query = get_byoa_cds(**kwargs)
    ret = []
    for row in byoa_cd_query:
        # if row.deploy_status is "NOT_DEPLOYED":
        # log("CiscoCTF", "changing to DEPLOYED")
        # row.deploy_status = "DEPLOYED_IN_CODE"
        # db.session.commit()
        ret.append(row._asdict())

    # log("CiscoCTF", "[{byoa_deploys}]", byoa_deploys=ret)
    return ret

def load(app):
    app.db.create_all()
    CHALLENGE_CLASSES["byoa"] = ByoaChallenge
    register_plugin_assets_directory(
        app, base_path="/plugins/byoa_challenges/assets/"
    )

    app.config['TEMPLATES_AUTO_RELOAD'] = True
    # This does not work, makes call return a 404
    # app.url_map.add(Rule('/plugins/byoa_challenges/deploy/<challenge_id>/<team_id>', endpoint='byoa_challenges.view_byoa_challenge_deploy', methods=['GET', 'POST']))
    # app.url_map.add(Rule('/plugins/byoa_challenges/deploy/<challenge_id>', endpoint='byoa_challenges.view_byoa_challenge_deploy', methods=['GET', 'POST']))


    @app.route('/plugins/byoa_challenges/deploys', methods=['GET'])
    @requires_auth
    def view_byoa_deploys():
        try:
            # authed_or_fail()
            # deployments = ByoaChallengeDeploys.query.filter_by(team_id=team_info.id).first()
            # deployments = [{'id': 1, 'team_id': 1, 'challenge_id': 69, 'deploy_status': 'DERPED'}]
            # if they are admin display all, otherwise only display deploys for their team
            if is_admin():
                deployments = get_byoa_cds_as_dicts()
            else:
                team: Teams = get_current_team()
                deployments = get_byoa_cds_as_dicts(team_id=team.id)
            # return {"deployments": deployments}
            return render_template('cisco/byoa_challenges/byoa_deploys.html', deployments=deployments)
            # return {"success": True, "team": team}
        except ByoaException as be:
            return be.get_response_from_exception()


    @app.route('/plugins/byoa_challenges/view/<challenge_id>/<team_id>', methods=['GET'])
    @app.route('/plugins/byoa_challenges/view/<challenge_id>', methods=['GET'])
    @requires_auth
    def view_byoa_challenge_deploy(challenge_id, team_id=None):
        try:
            challenge = ByoaChallengeEntry.query.filter_by(id=challenge_id).first()
            if not challenge:
                raise ByoaException("This challenge_id does not exist.", ["Invalid challenge_id! This challenge_id does not exist."], 404)
                # return Response('{"errors": ["Invalid challenge_id! This challenge_id does not exist."]}', status=404, mimetype='application/json')

            team: Teams = get_current_team()
            if team_id is not None:
                if int(team_id) != team.id and not is_admin():
                    raise ByoaException("Non admin tried to view another team's deploy.", ["You are not an admin, you trickster"], 403)
                bcd = get_or_create_byoa_cd(challenge_id, team_id)
            else:
                bcd = get_or_create_byoa_cd(challenge_id, team.id)
            k8s_job = None
            job_name = ''
            metadata = bcd.get_byoa_metadata()
            if bcd.deploy_status in ['DEPLOYING', 'DEPLOYED', 'FAILED_DEPLOY']:
                if request.args.get('check_job') == 'true':
                    log("CiscoCTF", "checking on job...")
                    bcd.check_k8s_job('deploy')
                k8s_job = bcd.get_k8s_job('deploy', challenge.api_base_uri).__dict__
                # job_name = k8s_job["_metadata"]["labels"]["job-name"]
                job_name = f"{bcd.get_chal_ref()}-team{bcd.team_id}-deploy"
                if is_admin():
                    metadata.admin_job_url_deploy=f"https://rancher-cloudctfseccon2021.cisco.com/dashboard/c/local/explorer/batch.job/{get_k8s_namespace()}/{job_name}#pods"
            elif bcd.deploy_status in ['DESTROYING', 'FAILED_DESTROY']:
                if request.args.get('check_job') == 'true':
                    log("CiscoCTF", "checking on job...")
                    bcd.check_k8s_job('destroy')
                if bcd.deploy_status != 'DESTROYED':
                    k8s_job = bcd.get_k8s_job('destroy', challenge.api_base_uri).__dict__

                job_name = f"{bcd.get_chal_ref()}-team{bcd.team_id}-destroy"
                job_name_deploy = f"{bcd.get_chal_ref()}-team{bcd.team_id}-deploy"
                if is_admin():
                    metadata.admin_job_url_deploy=f"https://rancher-cloudctfseccon2021.cisco.com/dashboard/c/local/explorer/batch.job/{get_k8s_namespace()}/{job_name_deploy}#pods"
                    metadata.admin_job_url_destroy=f"https://rancher-cloudctfseccon2021.cisco.com/dashboard/c/local/explorer/batch.job/{get_k8s_namespace()}/{job_name}#pods"
            return render_template('cisco/byoa_challenges/bcd.html', bcd=bcd.__dict__, challenge=challenge.__dict__,
                                   k8s_deploy_job=k8s_job, metadata=metadata)
        except ByoaException as be:
            return be.get_response_from_exception()


    @app.route('/plugins/byoa_challenges/deploy/<challenge_id>/<team_id>', methods=['GET'])
    @app.route('/plugins/byoa_challenges/deploy/<challenge_id>', methods=['GET'])
    @requires_auth
    def deploy_byoa_challenge(challenge_id, team_id=None):
        try:
            # authed_or_fail()
            # make sure challenge exists
            challenge = ByoaChallengeEntry.query.filter_by(id=challenge_id).first()
            if not challenge:
                raise ByoaException("This challenge_id does not exist.", ["Invalid challenge_id! This challenge_id does not exist."], 404)

            team: Teams = get_current_team()
            if team_id is not None:
                if int(team_id) != team.id and not is_admin():
                    raise ByoaException("Non admin tried to view another team's deploy.", ["You are not an admin, you trickster"], 403)
            else:
                team_id = team.id
            # return Response('{"challenge_id": '+challenge_id+', "team_id": '+str(team.id)+'}', status=409, mimetype='application/json')
            bcd = get_or_create_byoa_cd(challenge_id, team_id)
            # Check current deploy status
            if bcd.deploy_status != 'NOT_DEPLOYED':
                return render_template('cisco/byoa_challenges/bcd.html', bcd=bcd.__dict__, challenge=challenge.__dict__,
                                       banner={"msg": f"Unable to deploy challenge because the current deploy status is '{bcd.deploy_status}'! You can only deploy if the status is NOT_DEPLOYED", "level": "danger"}), 409
                # raise Exception('Unable to deploy challenge because the current deploy status is '+bcd.deploy_status+'! You can only deploy if the status is NOT_DEPLOYED')

            # deploy and set status in DB
            bcd.deploy_challenge()
            return render_template('cisco/byoa_challenges/bcd.html', bcd=bcd.__dict__, challenge=challenge.__dict__,
                                   banner={"msg": "Deploy Job started!", "level": "info"})
        except ByoaException as be:
            return be.get_response_from_exception()

    @app.route('/plugins/byoa_challenges/reset/<challenge_id>/<team_id>', methods=['GET'])
    @app.route('/plugins/byoa_challenges/reset/<challenge_id>', methods=['GET'])
    @requires_auth
    def reset_byoa_challenge_deploy(challenge_id, team_id=None):
        try:
            challenge = ByoaChallengeEntry.query.filter_by(id=challenge_id).first()
            if not challenge:
                raise ByoaException("This challenge_id does not exist.", ["Invalid challenge_id! This challenge_id does not exist."], 404)
                # return Response('{"errors": ["Invalid challenge_id! This challenge_id does not exist."]}', status=404, mimetype='application/json')

            team: Teams = get_current_team()
            force = False
            if team_id is not None:
                if int(team_id) != team.id and not is_admin():
                    raise ByoaException("Non admin tried to view another team's deploy.", ["You are not an admin, you trickster"], 403)
                bcd = get_or_create_byoa_cd(challenge_id, team_id)
                if request.args.get('force') == 'true':
                    log("CiscoCTF", "force resetting...")
                    force = True
            else:
                bcd = get_or_create_byoa_cd(challenge_id, team.id)

            bcd.reset_challenge_deploy(force)
            return render_template('cisco/byoa_challenges/bcd.html', bcd=bcd.__dict__, challenge=challenge.__dict__,
                                   banner={"msg": f"Successfully reset deployment status. You may now try to deploy this.", "level": "success"})
        except ByoaException as be:
            return be.get_response_from_exception()

    @app.route('/plugins/byoa_challenges/validate/<challenge_id>/<team_id>', methods=['GET'])
    @app.route('/plugins/byoa_challenges/validate/<challenge_id>', methods=['GET'])
    @requires_auth
    def validate_byoa_challenge_deploy(challenge_id, team_id=None):
        try:
            challenge = ByoaChallengeEntry.query.filter_by(id=challenge_id).first()
            if not challenge:
                raise ByoaException("This challenge_id does not exist.", ["Invalid challenge_id! This challenge_id does not exist."], 404)
                # return Response('{"errors": ["Invalid challenge_id! This challenge_id does not exist."]}', status=404, mimetype='application/json')

            team: Teams = get_current_team()
            if team_id is not None:
                if int(team_id) != team.id and not is_admin():
                    raise ByoaException("Non admin tried to view another team's deploy.", ["You are not an admin, you trickster"], 403)
                bcd = get_or_create_byoa_cd(challenge_id, team_id)
            else:
                bcd = get_or_create_byoa_cd(challenge_id, team.id)

            validation_result = bcd.validate_challenge()
            print('validation_result')
            print(validation_result)
            return render_template('cisco/byoa_challenges/bcd.html', bcd=bcd.__dict__, challenge=challenge.__dict__,
                                   validation_result=validation_result.__dict__)
        except ByoaException as be:
            return be.get_response_from_exception()

    @app.route('/plugins/byoa_challenges/destroy/<challenge_id>/<team_id>', methods=['GET'])
    @app.route('/plugins/byoa_challenges/destroy/<challenge_id>', methods=['GET'])
    @requires_auth
    def destroy_byoa_challenge_deploy(challenge_id, team_id=None):
        try:
            challenge = ByoaChallengeEntry.query.filter_by(id=challenge_id).first()
            if not challenge:
                raise ByoaException("This challenge_id does not exist.", ["Invalid challenge_id! This challenge_id does not exist."], 404)
                # return Response('{"errors": ["Invalid challenge_id! This challenge_id does not exist."]}', status=404, mimetype='application/json')

            team: Teams = get_current_team()
            if team_id is not None:
                if int(team_id) != team.id and not is_admin():
                    raise ByoaException("Non admin tried to view another team's deploy.", ["You are not an admin, you trickster"], 403)
                bcd = get_or_create_byoa_cd(challenge_id, team_id)
            else:
                bcd = get_or_create_byoa_cd(challenge_id, team.id)

            bcd.destroy_challenge()
            return render_template('cisco/byoa_challenges/bcd.html', bcd=bcd.__dict__, challenge=challenge.__dict__,
                                   banner={"msg": f"Successfully queued job to destroy deployment.", "level": "success"})
        except ByoaException as be:
            return be.get_response_from_exception()


def requires_auth(function):
    @wraps(function)
    def authed_or_fail(*args, **kwargs):
        if not authed():
            ex = ByoaException("User is not logged in", None, 401)
            return ex.get_response_from_exception()
        return function(*args, **kwargs)
    return authed_or_fail


def get_ctf_admin_cloud_aws_cred() -> ByoaTeamAwsInfo:
    return ByoaTeamAwsInfo(
        AWS_REGION=os.getenv('CTF_ADMIN_AWS_REGION'),
        AWS_ACCESS_KEY_ID=os.getenv('CTF_ADMIN_AWS_ACCESS_KEY_ID'),
        AWS_SECRET_ACCESS_KEY=os.getenv('CTF_ADMIN_AWS_SECRET_ACCESS_KEY')
    )

def get_k8s_namespace() -> str:
    return os.getenv('CTF_K8S_NAMESPACE')

def get_base_terraform_path():
    return '/var/data/team-byoa-pvc'
