from typing import Optional
import boto3

import requests
from attr import dataclass

@dataclass
class ByoaChallengeValidationReturn:
    message: str
    result: bool
    flag: Optional[str] = None

def validate_chalenge(bcd):

    client = boto3.client('ec2', aws_access_key_id=bcd.get_byoa_team_aws_info().AWS_ACCESS_KEY_ID, aws_secret_access_key=bcd.get_byoa_team_aws_info().AWS_SECRET_ACCESS_KEY,region_name=bcd.get_byoa_team_aws_info().AWS_REGION)

    try:
        response = client.describe_instances(
                Filters=[{'Name': 'instance-state-name', 'Values': ['running']},{'Name': 'tag:Name', 'Values': ['SSRF']}]
            )
    except:
        return ByoaChallengeValidationReturn(message="You did something wrong....Try harder", result=False)

    url=response['Reservations'][0]['Instances'][0]['MetadataOptions']['HttpTokens']


    if url=='required' or url=='disabled':
        return ByoaChallengeValidationReturn(message="Challenge Validated Successfully ", result=True, flag='flag{ec2_metadata_v2_is_more_secure}')
    else:
        return ByoaChallengeValidationReturn(message="You did something wrong....Try harder", result=False)