<<<<<<< HEAD
# from .. import ByoaChallengeDeploys
=======
# from .. import ByoaChallengeDeploys
>>>>>>> 0f545aee483bbaf4dbcc913e2a9907a778ad3098
import requests


def validate_chalenge(bcd):
    # TODO Bhavik to fill in validation code
    tf_data = bcd.get_terraform_state_dict()
    return tf_data
    #url = tf_data['outputs']['public_ip']['value']
    real = tf_data['outputs']['public_ip']['value']

    url= 'http://' + real


    try:
        resp = requests.get(url, timeout=3) #3 seconds
    except Exception:

        return {"Note : Challenge Failed, Please try again"}


    #My External IP validation
    url_lamda= 'https://emlxxz79gg.execute-api.ap-south-1.amazonaws.com/dev?publicip='+real

    extresp = requests.request("GET", url_lamda)

    if resp.status_code == 200:

        if 'timed' in extresp.text:

            return {"Note:Challenge Validated Successfully --- flag{Cloud_security_Infra_important}"}


        else:
            return {"Note Challenge Failed, Please try again"}
    else:

        return {"Note Challenge Failed, Please try again"}


