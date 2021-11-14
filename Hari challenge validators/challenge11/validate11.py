import boto3
import json
import datetime as dt
from pprint import pprint


class Cloudtrail:
    def __init__(self, key, secret, region, check_time=dt.datetime.now(dt.timezone.utc)):
        self._client = boto3.client('cloudtrail',
                                    aws_access_key_id=key,
                                    aws_secret_access_key=secret,
                                    region_name=region)
        self._s3api_client = boto3.client('s3',
                                          aws_access_key_id=key,
                                          aws_secret_access_key=secret,
                                          region_name=region)
        self.check_time = check_time

    def _get_desc_trails(self):
        try:
            trails = self._client.describe_trails()
        except self._client.exceptions.DBClusterNotFoundFault:
            return None
        return trails.get('trailList')

# 3.2 Ensure CloudTrail log file validation is enabled

    def ch11(self):
        trails = self._get_desc_trails()
        if not trails:
            return {'errors': "Internal Error"}
        flags = False
        for index, trail in enumerate(trails):
            if trail['Name'] != "ctf-demo-trail":
                continue
            flags = trail.get('LogFileValidationEnabled')
        if flags:
            return {'message': "Success", 'flag': "LogFileValidationEnabled"}
        else:
            return {'message': "Failed"} 


if __name__ == "__main__":
    try:

        cloudtrail = Cloudtrail(
            "AWS_KEY", "AWS_SCERET", "ap-south-1")

        print("Ensure CloudTrail log file validation is enabled:")
        pprint(cloudtrail.ch11())

    finally:
        print("Exiting...")
