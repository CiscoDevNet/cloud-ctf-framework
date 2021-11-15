from typing import Optional

import requests
from attr import dataclass

# To fix the challenges one need to remove the any any rule at top (position 100) of NACL
@dataclass
class ByoaChallengeValidationReturn:
    message: str
    result: bool
    flag: Optional[str] = None

def validate_chalenge(bcd):
    tf_data = bcd.get_terraform_state_dict()
    # return tf_data
    #url = tf_data['outputs']['public_ip']['value']
    real = tf_data['outputs']['public_ip']['value']

    url= 'http://' + real


    try:
        resp = requests.get(url, timeout=3) #3 seconds
    except Exception:
        return ByoaChallengeValidationReturn(message="You did something wrong....Try harder", result=False)


    #My External IP validation
    url_lamda= 'https://emlxxz79gg.execute-api.ap-south-1.amazonaws.com/dev?publicip='+real

    extresp = requests.request("GET", url_lamda)

    if resp.status_code == 200:

        if 'timed' in extresp.text:

            return ByoaChallengeValidationReturn(message="Challenge Validated Successfully ", result=True, flag='flag{Cloud_security_Infra_important}')

            #return {"Note:Challenge Validated Successfully --- flag{Cloud_security_Infra_important}"}


        else:
            return ByoaChallengeValidationReturn(message="Validation failed...You are closer...Try harder", result=False)
            #return {"Note Challenge Failed, Please try again"}
    else:
        return ByoaChallengeValidationReturn(message="You messed up badly...Try harder", result=False)


        #return {"Note Challenge Failed, Please try again"}


