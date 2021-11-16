from typing import Optional
import boto3
import datetime as dt
import requests
from attr import dataclass

@dataclass
class ByoaChallengeValidationReturn:
    message: str
    result: bool
    flag: Optional[str] = None

def get_desc_trails(bcd):
     cloudtrail = boto3.client('cloudtrail', aws_access_key_id=bcd.get_byoa_team_aws_info().AWS_ACCESS_KEY_ID, aws_secret_access_key=bcd.get_byoa_team_aws_info().AWS_SECRET_ACCESS_KEY, region_name=bcd.get_byoa_team_aws_info().AWS_REGION)
     
     try:
         trails = cloudtrail.describe_trails() 
     except Exception:
         return None
     return trails.get('trailList')


def validate_chalenge(bcd):
    trails = get_desc_trails(bcd)
    if not trails:
        return ByoaChallengeValidationReturn(message="Internal Error", result=False)
    flags = False

    for index, trail in enumerate(trails):
        if trail['Name'] != "ctf-demo-trail":
            continue

        flags = trail.get('LogFileValidationEnabled')
        
        if flags:
            return ByoaChallengeValidationReturn(message="Challenge Validated Successfully ", result=True, flag='flag{LogFileValidationEnabled}')
        else:
            return ByoaChallengeValidationReturn(message="You did something wrong....Try harder", result=False)




