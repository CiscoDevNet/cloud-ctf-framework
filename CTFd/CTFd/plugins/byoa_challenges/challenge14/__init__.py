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


def validate_chalenge(bcd):

    tf_data = bcd.get_terraform_state_dict()
    infra_dev_policy = tf_data['outputs']['infra-dev-policy']['value']
    infra_prod_policy = tf_data['outputs']['infra-prod-policy']['value']

    client = boto3.client('iam', aws_access_key_id=bcd.get_byoa_team_aws_info().AWS_ACCESS_KEY_ID, aws_secret_access_key=bcd.get_byoa_team_aws_info().AWS_SECRET_ACCESS_KEY, region_name=bcd.get_byoa_team_aws_info().AWS_REGION)

    response_dev = client.get_policy_version(
        PolicyArn=infra_dev_policy,
        VersionId='v1'
    )

    response_prod = client.get_policy_version(
        PolicyArn=infra_prod_policy,
        VersionId='v1'
    )

    dev_str=""
    prod_str=""

    for i in response_dev['PolicyVersion']['Document']['Statement']:
        for k in i['Resource']:
            dev_str=dev_str+k

    for i in response_prod['PolicyVersion']['Document']['Statement']:
        for k in i['Resource']:
            prod_str=prod_str+k

    if 'dev' in dev_str and 'prod' in prod_str:
        if 'prod' in dev_str and 'dev' in prod_str:
            return ByoaChallengeValidationReturn(message="You did something wrong....Try harder", result=False)
        else:
            return ByoaChallengeValidationReturn(message="Challenge Validated Successfully ", result=True, flag='flag{iamS3bucketResctrictionPolicy}')
    else:
        return ByoaChallengeValidationReturn(message="You did something wrong....Try harder", result=False)


