from pprint import pprint
import boto3
import json


class Storage:
    def __init__(self, key, secret, region):
        self._client = boto3.client('s3',
                                    aws_access_key_id=key,
                                    aws_secret_access_key=secret,
                                    region_name=region)
       
    def ch12(self):
        try:
            buck_rules = self._client.get_bucket_encryption(
                Bucket="ctf-important-logs")
        except self._client.exceptions.NoSuchBucket:
            return {'message': "Failed"}
        except self._client.exceptions.ClientError:
            return {'message': "Failed"}
        temp1 = buck_rules.get('ServerSideEncryptionConfiguration')
        temp2 = temp1.get('Rules')[0]
        temp3 = temp2.get('ApplyServerSideEncryptionByDefault')
        enc_algo = temp3.get('SSEAlgorithm')
        if enc_algo == 'AES256' or enc_algo == 'aws:kms':
            return {'message': "Success", 'flag': "s3bucketencryptedatrest"}
        else:
            return {'message': "Failed"}

if __name__ == "__main__":
    try:

        storage = Storage("AWS_KEY",
                          "AWS_SCERET", "ap-south-1")
        print('encryption-at-rest is enabled for all S3 buckets')
        pprint(storage.ch12())
        
    finally:
        print("EXITING....")
