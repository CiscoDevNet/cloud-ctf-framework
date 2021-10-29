from CTFd.schemas.teams import TeamSchema
from CTFd.schemas.users import UserSchema
from CTFd.utils.user import get_current_team, get_current_user
from CTFd.models import Teams, Users

def load(app):
    @app.route('/plugins/jgroetzi-test-1', methods=['POST', 'GET'])
    def view_plugins_jgroetzi_test1():
        team: Teams = get_current_team()
        team_info = TeamSchema().dump(team)

        user: Users = get_current_user()

        user_info = UserSchema().dump(user)

        return {"success": True, "team": team_info.data, "user": user_info.data}
