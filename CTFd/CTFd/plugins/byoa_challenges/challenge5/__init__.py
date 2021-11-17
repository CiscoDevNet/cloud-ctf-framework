import re
from typing import Optional
import requests
from attr import dataclass
from CTFd.utils.logging import log

# this will return different flags based on the state of the application

@dataclass
class ByoaChallengeValidationReturn:
    message: str
    result: bool
    flag: Optional[str] = None

def validate_chalenge(bcd) -> ByoaChallengeValidationReturn:
    ''' terraform outputs
    "outputs": {
        "db_server_address": {
          "value": "ctf-chal5-sqldb.cbokp9fbnqsg.us-east-1.rds.amazonaws.com",
          "type": "string"
        },
        "web_server_address": {
          "value": "ec2-3-239-128-67.compute-1.amazonaws.com",
          "type": "string"
        }
      },
    '''
    tf_data = bcd.get_terraform_state_dict()
    web_host = tf_data['outputs']['web_server_address']['value']

    url = 'http://' + web_host


    try:
        resp = requests.get(url, timeout=3)
    except Exception as e:
        log("CiscoCTF", "caught exception {e}", e=e)
        return ByoaChallengeValidationReturn(message="Ran into an issue trying to check the server (is it up?).", result=False)

    if resp.status_code != 200:
        return ByoaChallengeValidationReturn(message="The web server is not returning 200...something must be broken.", result=False)

    log("CiscoCTF", "headers {headers}", headers=resp.headers)
    if 'shaself' not in resp.headers:
        return ByoaChallengeValidationReturn(message="The application is returning, but it seems you have modified the application code as it is no longer returning as expected. You only need to make changes to the environment, not the application code.", result=False)

    body = str(resp.content)
    if "Could not connect: Where is maria?" in body:
        return ByoaChallengeValidationReturn(message="It looks like the web server is up, but it still can not find maria.", result=False)

    if "Connected to the database!" in body:
        msg = "It looks like you found maria!<br>"+ "Here is the flag for 'My First Cloud LAMP': '" + get_flag('connected') + "'"
        if "Could not find my table?" in body:
            msg = msg + "<br>For the current state of the application you have earned the flag for 'My First Cloud LAMP'. Note there are still more issues to fix in this application in order to get the remaining flags."
            return ByoaChallengeValidationReturn(result=True, message=msg, flag=get_flag('connected'))
        else:
            issue_cnt = 0
            # make sure symbolic link is not a readable page
            smylink_state = check_symbolic_maria(web_host)
            if smylink_state == True:
                msg = msg + "<br>You have fixed the Symbolic Maria issue, here is the flag for challenge 'Symbolic Maria Exposure': "+get_flag('symbolic_maria_fixed')
            else:
                msg = msg + smylink_state
                issue_cnt += 1

            full_app_state = check_full_app_state(web_host)
            if full_app_state == True:
                msg = msg + "<br>You have fixed the application"
                if(issue_cnt):
                    msg = msg + ", but there are still some outstanding issues to fix (see Outstanding problems above). But here is the flag for 'Who dropped my tables?'"
                else:
                    msg = msg + ", we are up an running now! Here is the flag for 'Who dropped my tables?'"
                return ByoaChallengeValidationReturn(result=True, message=msg, flag=get_flag('table_exists_and_app_loading'))
            else:
                msg = msg + full_app_state

            msg = msg + "<br>The application is still not fully functioning as expected :("
            return ByoaChallengeValidationReturn(result=False, message=msg)

    return ByoaChallengeValidationReturn(result=False, message="The web server returns now, but validation has not pass. Did you modify the application code?")

def get_flag(app_state):
    if app_state == 'connected':
        return "flag{d0_y0u_know_where_My_friend_Maria_is?}"
    if app_state == 'table_exists_and_app_loading':
        return "flag{I_can_RDS_all_0n_mY_0wn!}"
    if app_state == 'symbolic_maria_fixed':
        return "flag{Hidden_symb0lic_links_g3t_me_everytimE}"

def check_symbolic_maria(web_host: str):
    '''
    we expect 404 response on the .maria file to be valid
    :param web_host:
    :return:
    '''
    try:
        url = f"http://{web_host}/.maria"
        resp = requests.get(url, timeout=3)
        if resp.status_code == 200:
            return "<br>Outstanding problem: Symbolic Maria not fixed"
        elif resp.status_code != 404:
            return "<br>Outstanding problem: Symbolic Maria not fixed as expected"

    except Exception as e:
        log("CiscoCTF", "caught exception {e}", e=e)
        return "<br>Outstanding problem: Unable to connect to host"

    # if we made it here, symlink issue is solved
    return True

def check_full_app_state(web_host: str):
    # TODO figure out how to connect to sql and get the schema of the table for extra validation
    # Thanks for visiting the site. You are visitor number 1
    url = f"http://{web_host}"
    try:
        resp = requests.get(url, timeout=3)
        if resp.status_code != 200:
            return f"<br>Outstanding problem: Server is not returning 200 status (got {resp.status_code})"

        body = str(resp.content)
        if "Could not find my table?" in body:
            return f"<br>Outstanding problem: Application state is not as expected :( did you modify the app?"

        cur_visits = get_current_vists_from_body(body)
        if isinstance(cur_visits, int):
            #check again and make sure it is higher than before
            resp = requests.get(url, timeout=3)
            if resp.status_code != 200:
                return f"<br>Outstanding problem: Server is not returning 200 status (got {resp.status_code})"

            body = str(resp.content)
            new_visits = get_current_vists_from_body(body)
            if isinstance(new_visits, int):
                if new_visits > cur_visits:
                    # count went up since we last visited, good enough
                    return True
                else:
                    return f"<br>Outstanding problem: The visitor tracking is not increasing, are you sure the app is functioning correctly?"
            else:
                return new_visits
        else:
            return cur_visits

    except Exception as e:
        log("CiscoCTF", "caught exception {e}", e=e)
        return "<br>Outstanding problem: Ran into an issue trying to check the server (is it up?)."

def get_current_vists_from_body(body: str):
    '''
     Looging for this content:
      <p>Thanks for visiting the site. You are visitor number <strong>1</strong></p>

      and this function would return 1 from above example
    :param body:
    :return: string with error for user, otherwise int value of current visits pulled from page
    '''
    if "Thanks for visiting the site. You are visitor number" not in body:
        return f"<br>Outstanding problem: Application state is not as expected. The visitor tracking is not online."

    visits_search = re.search('<p>Thanks for visiting the site. You are visitor number <strong>(\d+)</strong></p>', body)
    if visits_search:
        return int(visits_search.group(1))
    else:
        return f"<br>Outstanding problem: Application state is not as expected. Can not find number of visits."
