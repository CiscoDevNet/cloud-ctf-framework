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
    try:
        buck_rules = s3.get_bucket_encryption(Bucket=bucket_name)
    except s3.exceptions.NoSuchBucket:
       return ByoaChallengeValidationReturn(message="You did something wrong....Try harder", result=False)
    except s3.exceptions.ClientError:
        return ByoaChallengeValidationReturn(message="You did something wrong....Try harder", result=False)
    temp1 = buck_rules.get('ServerSideEncryptionConfiguration')
    temp2 = temp1.get('Rules')[0]
    temp3 = temp2.get('ApplyServerSideEncryptionByDefault')
    enc_algo = temp3.get('SSEAlgorithm')
    if enc_algo == 'AES256' or enc_algo == 'aws:kms':
        return ByoaChallengeValidationReturn(message="Challenge Validated Successfully ", result=True, flag='flag{s3bucketencryptedatrest}')
    else:
        return ByoaChallengeValidationReturn(message="You did something wrong....Try harder", result=False)


