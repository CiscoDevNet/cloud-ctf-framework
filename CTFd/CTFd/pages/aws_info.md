## Steps for Registering a new team

1. Pick the AWS account that you want to use.  
Each team will need to have an AWS (free) account. All the challenges can be deployed using free account.  
If you do not have an AWS account, you can [go here and click "create a free account"](https://aws.amazon.com/free/?trk=ps_a134p000003yBfsAAE&trkCampaign=acq_paid_search_brand&sc_channel=ps&sc_campaign=acquisition_US&sc_publisher=google&sc_category=core&sc_country=US&sc_geo=NAMER&sc_outcome=acq&sc_detail=%2Bcreate%20%2Baws%20%2Baccount&sc_content=Account_bmm&sc_segment=438195700997&sc_medium=ACQ-P|PS-GO|Brand|Desktop|SU|AWS|Core|US|EN|Text&s_kwcid=AL!4422!3!438195700997!b!!g!!%2Bcreate%20%2Baws%20%2Baccount&ef_id=CjwKCAjw7--KBhAMEiwAxfpkWJwRVjpuXNfVhQxI0idhvMVSlDyY9DXOMGi8kXLUHDo_VEc27lKHrBoCoYsQAvD_BwE:G:s&s_kwcid=AL!4422!3!438195700997!b!!g!!%2Bcreate%20%2Baws%20%2Baccount&all-free-tier.sort-by=item.additionalFields.SortRank&all-free-tier.sort-order=asc&awsf.Free%20Tier%20Types=*all&awsf.Free%20Tier%20Categories=*all).

2. Create a new user in the account with security credentials.  
In order for the CTF to be able to deploy challenges to your cloud account, you will need to provide programmatic user credentials to the CTF team when you register a team. The role for the user provided is provided by the CTF team and will have restricted access to only be able to do the actions required by the CTF, which should only be actions that deploy free content (I.e. the CTF team will not deploy something on your account which costs money).  
3. Assign the Role to the user (TBD)
4. Provide the credentials in CTFd app during team registration

### Create an IAM policy for CTF user
1. Get the policy: The policy you should assign the user you create for the CTF can be [downloaded here (JSON)](https://ctfd-custom-policy.s3.ap-south-1.amazonaws.com/final-policy.json)
2. In the policy JSON, you will need to replace 2 variables. open the json in a text edit and make the following find/replace all:

Replace `${Region}` with the aws region you are planning to use i.e. `ap-south-1`  
Replace `${Account}` with your AWS account ID (12 digit number). [Finding your AWS account ID](https://docs.aws.amazon.com/general/latest/gr/acct-identifiers.html#FindingYourAccountIdentifiers)
3. Log into AWS console with your root user or an admin user and create a new IAM policy. [Shortcut Link](https://console.aws.amazon.com/iam/home#/policies$new?step=edit)  
Go to the JSON tab and paste in the contents from the JSON file (from step 1) and then click continue. Add any tags, then Click Next:Review.
4. Give the policy a name and description then click create. 


### Create new user in AWS
You will create a user using the IAM service. [AWS Console Link](https://console.aws.amazon.com/iam/home#/users$new?step=details)  
To assign the role, pick the "Attach existing policies directly" option. Search for the policy you created, select it and hit next and continue through and create the user.