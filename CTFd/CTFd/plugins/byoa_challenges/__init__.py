from flask import Blueprint

from CTFd.models import Challenges, Solves, db
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES, BaseChallenge
from CTFd.plugins.migrations import upgrade
from CTFd.utils.modes import get_model
from CTFd.models import Teams
from CTFd.utils.user import get_current_team

class ByoaChallengeEntry(Challenges):
    '''
    challenge model for storing challenges
    '''
    __mapper_args__ = {'polymorphic_identity': 'byoa'}
    challenge_id = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"), primary_key=True
    )
    # Stores the base uri for where validate/deploy/destroy
    api_base_uri = db.Column(db.String)

    def __init__(self, api_base_uri, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_base_uri = api_base_uri
# def __init__(self, api_base_uri, name, description, value, category, state, type='byoa'):
    #     self.name = name
    #     self.description = description
    #     self.value = value
    #     self.category = category
    #     self.type = type
    #     self.state = state
    #     self.api_base_uri = api_base_uri


class ByoaChallengeDeploys(db.Model):
    '''
    This model is for tracking byoa deployments and statuses
    '''
    challenge_id = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"), primary_key=True
    )
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    # NOT_DEPLOYED, DEPLOYING, DEPLOYED, ERROR_DEPLOYING, SOLVED
    deploy_status = db.Column(db.String, default="NOT_DEPLOYED")
    # stores random schemaless info, like messages from the deploy, or variables from the deploy, etc.
    ctf_metadata = db.Column(db.JSON, default=None)

    def __init__(self, team, ctf_metadata):
        self.target = team
        self.team_id = team.id
        self.ctf_metadata = ctf_metadata

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
        # byoac_deploy = ByoaChallengeDeploys.query.filter_by(challenge_id=challenge.id,team_id=team.id).first()
        # data["deploy_status"] = byoac_deploy.deploy_status
        data["deploy_status"] = "NOT_DEPLOYED"
        return data


def load(app):
    app.db.create_all()
    CHALLENGE_CLASSES["byoa"] = ByoaChallenge
    register_plugin_assets_directory(
        app, base_path="/plugins/byoa_challenges/assets/"
    )
