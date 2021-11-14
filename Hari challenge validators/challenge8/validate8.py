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

    def ch8(self):
        pass_pol = self._get_pass_pol()
        if pass_pol.get("error"):
            return {'error': "Internal Error"}
        if pass_pol.get("MinimumPasswordLength") >= 14:
            return {'message': "Success", 'flag': "passwordminlen14"}
        else:
            return {'message': "Failed"}



if __name__ == "__main__":
    try:

        iam_chal = IAMChallenges(
            "AWS_KEY", "AWS_SCERET")

        print("Check Password Minimum Lenght of 14:")
        print(iam_chal.ch8())

    finally:
        print("Exiting.....")
