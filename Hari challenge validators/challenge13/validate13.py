from pprint import pprint
import boto3
import json


class Storage:
    def __init__(self, key, secret, region):
        self._client = boto3.client('s3',
                                    aws_access_key_id=key,
                                    aws_secret_access_key=secret,
                                    region_name=region)
       


    def ch13(self):
        to_check = {
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True
        }
        try:
            pub_acc_block = self._client.get_public_access_block(
                Bucket="ctf-confidential-logs")
        except self._client.exceptions.NoSuchBucket:
            return {'message': "Failed"}
        temp1 = pub_acc_block.get('PublicAccessBlockConfiguration')
        if temp1 == to_check:
            return {'message': "Success", 'flag': "s3bucketmadeprivate"}
        else:
            return {'message': "Failed"}

if __name__ == "__main__":
    try:

        storage = Storage("AWS_KEY",
                          "AWS_SCERET", "ap-south-1")
        print('Block Public Access are configured for S3 buckets')
        pprint(storage.ch13())
        
    finally:
        print("EXITING....")
