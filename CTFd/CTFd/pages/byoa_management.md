<br>
<br>

## Steps for Registering a new team

1. Pick the AWS account that you want to use.  
   Each team will need to have an AWS (free) account. All the challenges can be deployed using free account.  
   If you do not have an AWS account, you can [go here and click "create a free account"](https://aws.amazon.com/free/?trk=ps_a134p000003yBfsAAE&trkCampaign=acq_paid_search_brand&sc_channel=ps&sc_campaign=acquisition_US&sc_publisher=google&sc_category=core&sc_country=US&sc_geo=NAMER&sc_outcome=acq&sc_detail=%2Bcreate%20%2Baws%20%2Baccount&sc_content=Account_bmm&sc_segment=438195700997&sc_medium=ACQ-P|PS-GO|Brand|Desktop|SU|AWS|Core|US|EN|Text&s_kwcid=AL!4422!3!438195700997!b!!g!!%2Bcreate%20%2Baws%20%2Baccount&ef_id=CjwKCAjw7--KBhAMEiwAxfpkWJwRVjpuXNfVhQxI0idhvMVSlDyY9DXOMGi8kXLUHDo_VEc27lKHrBoCoYsQAvD_BwE:G:s&s_kwcid=AL!4422!3!438195700997!b!!g!!%2Bcreate%20%2Baws%20%2Baccount&all-free-tier.sort-by=item.additionalFields.SortRank&all-free-tier.sort-order=asc&awsf.Free%20Tier%20Types=*all&awsf.Free%20Tier%20Categories=*all).

2. Create a new user in the account with security credentials.  
   In order for the CTF to be able to deploy challenges to your cloud account, you will need to provide programmatic user credentials to the CTF team when you register a team. The role for the user provided is provided by the CTF team and will have restricted access to only be able to do the actions required by the CTF, which should only be actions that deploy free content (I.e. the CTF team will not deploy something on your account which costs money).
3. Create an IAM policy for CTF user
   1. Get the policy: The policy you should assign the user you create for the CTF can be [downloaded here (JSON)](https://ctfd-custom-policy.s3.ap-south-1.amazonaws.com/final-policy.json)
   2. In the policy JSON, you will need to replace 2 variables. open the json in a text edit and make the following find/replace all:

   Replace `${Region}` with the aws region you are planning to use i.e. `ap-south-1`  
   Replace `${Account}` with your AWS account ID (12 digit number). [Finding your AWS account ID](https://docs.aws.amazon.com/general/latest/gr/acct-identifiers.html#FindingYourAccountIdentifiers)  
   
   4. Log into AWS console with your root user or an admin user and create a new IAM policy. [Shortcut Link](https://console.aws.amazon.com/iam/home#/policies$new?step=edit)  
      Go to the JSON tab and paste in the contents from the JSON file (from step 1) and then click continue. Add any tags, then Click `Next:Review`.
   5. Give the policy a name and description and then click `create`.
4. Create new user in AWS and assign the policy.
   1. You will create a user using the IAM service. [AWS Console Link](https://console.aws.amazon.com/iam/home#/users$new?step=details)
   2. To assign the role, pick the "Attach existing policies directly" option. Search for the policy you created, select it and hit next and continue through and create the user.
5. Provide the credentials in CTFd app during team registration


If you have any questions or concerns, please feel free to reach out to the admins via email: cloudctf@cisco.com
<br>

# Bring Your Own Account (BYOA) Challenges
The majority of the challenges in this CTF are "BYOA" challenges, which require the Team to provide their own AWS account.  
This document describes how you will interact with these challenges.

## Deploy
To deploy a challenge you just need to click the `Deploy` button. This will schedule a job to deploy the challenge to your AWS account.
<img src="/files/8293a41512ec7c665376f762a6b97072/challenge_view_not_deployed.png" alt="challenge_view_not_deployed" width="400"/>
<hr>
Click the "Refresh Status" to check and update the current status of the deployment.
<hr>
<img src="/files/f3842f3b80ddafb1880e4f523da748c7/bcd_view_deploying.png" alt="challenge_view_not_deployed" width="400"/>
<hr>
Once the job is finished, the deploy_status will change to `DEPLOYED`.<br>
<img src="/files/7364672bf103127b2c793f4e6b7088b9/byoa_deployed.png" alt="challenge_view_not_deployed" width="400"/>
<hr>
Each challenge will be deployed in its own VPC, which will be created during the deployment. You must have no more than 5 VPCs in your region, otherwise deployment will not work.

## Validate
After you have deployed the challenge, follow the challenge description/hints and try to fix ths problem in the cloud deployment.
Once you think you have solved the challenge by modifying the cloud configuration appropriately, click the `Validate` button.  
This will check the cloud environment, and if you have correctly fixed the problem as per the challenge guidance, it will return the flag.

## Destroy
Once you have solved a challenge, or if you just want to remove the deployment from your cloud account, click the `Destroy` button.
This will desstroy the VPC and all other related resources that were created from this challenge deployment.


# Interacting with the challenge VPC
You are free to do whatever in your VPC (it is your account). However, in order to interact with the challenges there are a few things to note:

- Do not delete any ec2 instances, interfaces, or gateways that were deployed in the challenge VPC. These actions will never be required to solve a challenge.
- If you want to delete everything, use the `Destroy` button for each challenge, this will gracefully and completely tear down the vpc that was deployed. If you try to delete things and clean up a vpc on your own, you may miss dependancies which if left untouched could start charging your account money. 
- Using the `Destroy` button will remove 100% of the things created by the CTF. If you created any additional resources in a challenge VPC, you may need to manually destroy these on your own, the destroy process is only aware of things that it creates.
- Try to only deploy 1 challenge at a time, to reduce risk of using all of quota your free tier account faster. You get 750 hours of ec2 run time, but if you had 75 instances deployed, this would only be 10 hours total. Each challenge only deploys roughly ec2 instance, the more you deploy at once the faster you will use up quota, just keep this in mind.
- If you want to switch the challenge you are working on you can just deploy a second one. It would be reccommended to power down the instances of the challenge that you are not working on and power them back on when you are working on them to save quota of free tier.