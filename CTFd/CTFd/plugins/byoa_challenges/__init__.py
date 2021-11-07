import collections
import pprint

import boto3
from attr import dataclass
from flask import Blueprint, render_template, Response
from kubernetes.client import V1Job
from werkzeug.routing import Rule

from CTFd.models import Challenges, db, TeamFieldEntries
# from CTFd.schemas.fields import TeamFieldEntriesSchema
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES, BaseChallenge
from CTFd.models import Teams
from CTFd.utils.user import get_current_team, is_admin, authed
from CTFd.schemas.teams import TeamSchema
from CTFd.utils.logging import log
from typing import Union, List, Dict
from kubernetes import client as k8sclient
from kubernetes import config
from .byoa_exception import ByoaException
from functools import wraps

@dataclass
class ByoaTeamAwsInfo:
    AWS_REGION: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str


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
    # NOT_DEPLOYED, DEPLOYING, DEPLOYED, ERROR_DEPLOYING, SOLVED
    deploy_status = db.Column(db.String(64), default="NOT_DEPLOYED")
    # stores random schemaless info, like messages from the deploy, or variables from the deploy, etc.
    ctf_metadata = db.Column(db.JSON, default=None)

    def __init__(self, challenge_id, team_id, ctf_metadata=None):
        self.challenge_id = challenge_id
        self.team_id = team_id
        self.ctf_metadata = ctf_metadata

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

    def deploy_challenge(self):
        if self.deploy_status != 'NOT_DEPLOYED':
            err = "call to deploy_challenge and the deploy_status was not currently set to NOT_DEPLOYED! It is currently "+self.deploy_status
            raise ByoaException(err, [err], 400)
        #self.deploy_status = 'DEPLOYING'
        #db.session.commit()

        # Check VPC count
        vpcs = self.get_all_aws_vpcs()

        if len(vpcs)>=5:
            return {"errors": ["VPC greater than 5...In AWS, by default, only 5 VPC's are allowed. Please delete one or more VPC to get the challenge deployed."]}

        # Do the deploy
        aws_info = self.get_byoa_team_aws_info()
        config.load_kube_config()
        batch_v1 = k8sclient.BatchV1Api()
        d_info = self.get_byoa_team_aws_info()
        k8s_job = create_k8s_job_object(d_info, self.get_k8s_job_name('deploy'), self.get_ccc_image_name('deploy'),
                                        {"type": "challenge-deploy", "ctf-challenge-id": self.challenge_id,
                                         "ctf-team-id": self.team_id})
        job = run_k8s_job(batch_v1, k8s_job)
        # log("K8s Job created. status='%s'" % str(job.status))
        # TODO NEXT: figure out what we need to return here and how to rely info to end user inside of challenge


    def destroy_challenge(self):
        if self.deploy_status != 'DEPLOYED':
            err = "call to destroy_challenge and the deploy_status was not currently set to DEPLOYED! It is currently "+self.deploy_status
            raise ByoaException(err, [err], 400)

        self.deploy_status = 'DESTROYING'
        db.session.commit()
        # TODO NEXT: figure out what we need to return here and how to rely info to end user inside of challenge


    def validate_challenge(self):
        if self.deploy_status != 'DEPLOYED':
            err = "call to validate_challenge and the deploy_status was not currently set to DEPLOYED! It is currently "+self.deploy_status
            raise ByoaException(err, [err], 400)

    # TODO NEXT: figure out what we need to return here and how to rely info to end user inside of challenge


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

    def get_aws_challenge_vpc_label_name(self):
        return "cisco-cloud-ctf-challenge-"+str(self.challenge_id)

    def get_all_aws_vpcs(self):
        aws_info = self.get_byoa_team_aws_info()
        client = boto3.client('ec2', aws_access_key_id=aws_info.AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=aws_info.AWS_SECRET_ACCESS_KEY, region_name=aws_info.AWS_REGION)
        describeVpc= client.describe_vpcs()
        return describeVpc['Vpcs']


    def get_k8s_job_name(self, job_type: str):
        '''
        Gets the K8s job name to be used for a K8s job.
        :param job_type: should be one of: deploy, destroy, validate
        :return str: string with job name. i.e. challenge1-team1-deploy
        '''
        if job_type not in ['deploy', 'destroy', 'validate']:
            raise Exception("Unknown job_type " + job_type)
        return 'challenge-' + str(self.challenge_id) + '-team' + str(self.team_id) + '-' + job_type

    def get_ccc_image_name(self, job_type: str):
        '''
        Gets the containers.cisco.com image name to be used for a K8s job.
        :param job_type: should be one of: deploy, destroy, validate
        :return str: string with image name. i.e. containers.cisco.com/cloud-ctf/challenge1-deploy
        '''
        if job_type not in ['deploy', 'destroy', 'validate']:
            raise Exception("Unknown job_type " + job_type)
        return 'containers.cisco.com/cloud-ctf/challenge' + str(self.challenge_id) + '-' + job_type


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


def create_k8s_job_object(aws_info: ByoaTeamAwsInfo, job_name: str, container_image: str, labels: Dict) -> V1Job:
    """

    :param labels: K8s labels to add to the job, should be dict where key is label name and value is value of the label
    :param aws_info:
    :param job_name: use get_k8s_job_name() to get name and pass to here
    :param container_image: i.e. cloud-ctf-cloudctfbot-pull-secret
    :return:
    """
    # Configureate Pod template container
    access_key = k8sclient.V1EnvVar(
        name="AWS_ACCESS_KEY_ID",
        value=aws_info.AWS_ACCESS_KEY_ID)
    secret_key = k8sclient.V1EnvVar(
        name="AWS_SECRET_ACCESS_KEY",
        value=aws_info.AWS_SECRET_ACCESS_KEY)
    # TODO this can probably be removed? cluster should be set up to do this automatically already
    image_pull_secrets = k8sclient.V1LocalObjectReference(
        name="cloud-ctf-cloudctfbot-pull-secret")
    container = k8sclient.V1Container(
        name=job_name,
        image=container_image,
        env=[access_key,secret_key])
    # Create and configurate a spec section
    template = k8sclient.V1PodTemplateSpec(
        metadata=k8sclient.V1ObjectMeta(labels=labels),
        spec=k8sclient.V1PodSpec(restart_policy="Never", containers=[container],image_pull_secrets=[image_pull_secrets]))
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
            # authed_or_fail()
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
            return render_template('cisco/byoa_challenges/bcd.html', bcd=bcd.__dict__, challenge=challenge.__dict__)
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
                                   banner={"msg": "Deploy Job started! Refresh this page to check the deploy status.", "level": "info"})
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