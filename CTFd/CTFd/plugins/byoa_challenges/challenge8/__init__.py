from typing import Optional
import boto3

import requests
from attr import dataclass

@dataclass
class ByoaChallengeValidationReturn:
    message: str
    result: bool
    flag: Optional[str] = None

def get_pass_pol(bcd):

    iam = boto3.client('iam', aws_access_key_id=bcd.get_byoa_team_aws_info().AWS_ACCESS_KEY_ID, aws_secret_access_key=bcd.get_byoa_team_aws_info().AWS_SECRET_ACCESS_KEY)
    try:
        pass_pol = iam.get_account_password_policy()
        pass_pol = pass_pol.get("PasswordPolicy")
    except iam.exceptions.NoSuchEntityException:
        pass_pol = {"error": "NoSuchEntityException"}
    except iam.exceptions.ServiceFailureException:
        pass_pol = {"error": "ServiceFailureException"}
    except:
        pass_pol = {"error": "Unknown Error"}
    return pass_pol

def validate_chalenge(bcd):

    pass_pol = get_pass_pol(bcd)
    print(pass_pol)
    if pass_pol.get("error"):
        return ByoaChallengeValidationReturn(message="Internal Error", result=False)
    if pass_pol.get("MinimumPasswordLength") >= 14:
        return ByoaChallengeValidationReturn(message="Challenge Validated Successfully ", result=True, flag='flag{passwordminlen14}')
    else:
        return ByoaChallengeValidationReturn(message="You did something wrong....Try harder", result=False)