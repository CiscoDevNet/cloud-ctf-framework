<img class="w-100 mx-auto d-block" style="max-width: 3000px;padding: 1px;padding-top: 14vh;" src="/files/802bb5d197374d0edc8eb0a187356031/seccon_logo.jpg">
<h3>Cloud CTF</h3>

With technology rapidly moving towards Cloud it is imperative to understand how to implement Cloud Security and also make the applications deployed in Cloud more Secure.

This CTF is focused on building Cloud skills by solving real life practical challenges.


<h3>What do you need to participate in this challenge?</h3>

1) Each team will need to have an AWS (free) account. All the challenges can be deployed using free account. [go here and click "create a free account"](https://aws.amazon.com/free/?trk=ps_a134p000003yBfsAAE&trkCampaign=acq_paid_search_brand&sc_channel=ps&sc_campaign=acquisition_US&sc_publisher=google&sc_category=core&sc_country=US&sc_geo=NAMER&sc_outcome=acq&sc_detail=%2Bcreate%20%2Baws%20%2Baccount&sc_content=Account_bmm&sc_segment=438195700997&sc_medium=ACQ-P|PS-GO|Brand|Desktop|SU|AWS|Core|US|EN|Text&s_kwcid=AL!4422!3!438195700997!b!!g!!%2Bcreate%20%2Baws%20%2Baccount&ef_id=CjwKCAjw7--KBhAMEiwAxfpkWJwRVjpuXNfVhQxI0idhvMVSlDyY9DXOMGi8kXLUHDo_VEc27lKHrBoCoYsQAvD_BwE:G:s&s_kwcid=AL!4422!3!438195700997!b!!g!!%2Bcreate%20%2Baws%20%2Baccount&all-free-tier.sort-by=item.additionalFields.SortRank&all-free-tier.sort-order=asc&awsf.Free%20Tier%20Types=*all&awsf.Free%20Tier%20Categories=*all)

2) In order for the CTF to be able to deploy challenges to your cloud account, you will need to provide programmatic user credentials to the CTF team when you register a team. The role for the user provided is provided by the CTF team and will have restricted access to only be able to do the actions required by the CTF, which should only be actions that deploy free content (I.e. the CTF team will not deploy something on your account which costs money).

IMPORTANT: It will be assumed that you are providing an account which is still in the free tier 12 month trial. If you provide an existing AWS account that is no longer in the free trial 12 month period, your account will likely have charges incurred. If you use an account which is still in the 12 month free trial stage, but you have used most of your free quota already, you may see charges on the account. If you are unsure, the safest things to do is to just simply create a new free account to use for this CTF, or pay for the charges (which should be minimal as only t2.micro ec2 instances are deployed for the most part).

The challenges are designed to work with free account without any additional costs, assuming the free account still has free quota left and is still in the free trial period.

[See more information about how to set up and provide credentials](https://cloudctfseccon2021.cisco.com/byoa_info)


<h3>What is the format of this CTF? </h3>

This CTF will leverage Amazon Web Services (AWS) as the cloud provider and all challenges will involve cloud concepts and interacting with the cloud to solve challenges. The challenges will be Offensive and Defensive based where either you need to find the vulnerability or fix it.

The CTF type is jeopardy style where you will find and submit a flag for each challenge in order to get points. How you get the flag will depond on the challenge.
Some challenges will involve deploying infrastructure into the cloud, and you need to find the misconfiguration which has security concerns and fix it. For these type of challenges, each challenge will be deployed into its own VPC. By default your AWS account will only allow up to 5 VPCs, so if there are more than 5 challenges you will not be able to deploy them all at once. The deploys are dynamic and you will be able to control which ones are deployed at any time from the CTFd application. Make sure that your account has less then 5 VPCs in use or you likely will not be able to use that account to participate in the challenges as requesting more VPCs for your account takes multiple days.

Note: The challenges will only support deploying to the follow AWS regions:

`ap-south-1`, `us-east-1`, `eu-west-2`

During the Registration kindly make sure the region you choose as all the challenges would be deployed in that region and cannot be changed later. If you make a mistake when registering your team, please just let the admins know and they can correct the information for you.

<h3>Is it Team or Individual based? </h3>

This CTF is meant to be Team based where each Team can have at max 4 members and will share a single AWS account, but you are also free to participate on your own as the only member of the team if you prefer.

<h3>When does it start?</h3>
This CTF is scheduled to start on November 16 around 5pm IST and will run through November 18.

<h3>How can we register? </h3>

You need to register on this server. During the event you can ask your queries on Team space https://eurl.io/#yflNpTech

<h3>What's in it for me?</h3>
Besides learning about cloud deployments, we will be offering prizes!  
There will be prizes awarded for the top 3 teams in each region (AMER, EU, APJC).  
Make sure you register with your cec (cisco email) if you want to be eligible for prizes.

<h3>Admins</h3>
<p class="p1">The CTF is brought to you by below Cyber Security enthusiasts. The names are not listed in any specific order.</p>
<p class="p1">John Groetzinger</p>
<p class="p1">Bhavik Shah</p>
<p class="p1">Ankush Kumar</p>
<p class="p1">Harikrishnan Jayachandran</p>
<p class="p1">Geoff Serrao</p>