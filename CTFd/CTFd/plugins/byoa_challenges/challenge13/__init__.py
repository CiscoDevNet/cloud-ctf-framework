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
    bucket_name = tf_data['outputs']['bucket_name']['value']

    s3 = boto3.client('s3', aws_access_key_id=bcd.get_byoa_team_aws_info().AWS_ACCESS_KEY_ID, aws_secret_access_key=bcd.get_byoa_team_aws_info().AWS_SECRET_ACCESS_KEY, region_name=bcd.get_byoa_team_aws_info().AWS_REGION)
    to_check = {"BlockPublicAcls": True,"IgnorePublicAcls": True,"BlockPublicPolicy": True,"RestrictPublicBuckets": True}
    try:
        pub_acc_block = s3.get_public_access_block(Bucket=bucket_name)
    except s3.exceptions.NoSuchBucket:
        return ByoaChallengeValidationReturn(message="You did something wrong....Try harder", result=False)
    temp1 = pub_acc_block.get('PublicAccessBlockConfiguration')
    if temp1 == to_check:
        return ByoaChallengeValidationReturn(message="Challenge Validated Successfully ", result=True, flag='flag{s3bucketmadeprivate}')
    else:
        return ByoaChallengeValidationReturn(message="You did something wrong....Try harder", result=False)


