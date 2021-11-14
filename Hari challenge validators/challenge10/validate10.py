from pprint import pprint
import boto3
import datetime as dt


class IAMChallenges():
    def __init__(self, key, secret, checktime=dt.datetime.now(dt.timezone.utc)):
        """
        Recieves the key, secret and score check time.
        """
        self._client = boto3.client(
            'iam', aws_access_key_id=key, aws_secret_access_key=secret)
        self.check_time = checktime

    def _get_pass_pol(self):
        try:
            pass_pol = self._client.get_account_password_policy()
            pass_pol = pass_pol.get("PasswordPolicy")
        except self._client.exceptions.NoSuchEntityException:
            pass_pol = {"error": "NoSuchEntityException"}
        except self._client.exceptions.ServiceFailureException:
            pass_pol = {"error": "ServiceFailureException"}
        except:
            pass_pol = {"error": "Unknown Error"}
        return pass_pol

    def ch10(self):
        user_flags = [False] * 2
        username = 'ctf-demo-user'
        try:
            atch_us = self._client.list_attached_user_policies(
                UserName=username)
            user_pol = self._client.list_user_policies(UserName=username)
        except self._client.exceptions.ServiceFailureException:
            pass
        
        if not atch_us.get('AttachedPolicies'):
            user_flags[0] = True
        if not user_pol.get('PolicyNames'):
            user_flags[1] = True
        if all(user_flags):
            return {'message': "Success", 'flag': "permissiononlygroup"}
        else:
            return {'message': "Failed"}


if __name__ == "__main__":
    try:

        iam_chal = IAMChallenges(
            "AWS_KEY", "AWS_SCERET")

        print("Ensure IAM Users Receive Permissions Only Through Groups")
        print(iam_chal.ch10())

    finally:
        print("Exiting.....")
