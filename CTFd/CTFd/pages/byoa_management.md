<br>

# Bring Your Own Account (BYOA) Challenges
The majority of the challenges in this CTF are "BYOA" challenges, which require the Team to provide their own AWS account.  
This document describes how you will interact with these challenges.

## Deploy
To deploy a challenge you just need to click the "Deploy button". This will schedule a job to deploy the challenge to your AWS account.
<img src="/files/2541ad789c9551b9bde9e09f7ebcb379/challenge_view_not_deployed.png" alt="challenge_view_not_deployed" width="400"/>
<hr>
Click the "Refresh Status" to check and update the current status of the deployment.
<hr>
<img src="/files/93586947d8515678bbc9f221ca0e1e57/bcd_view_deploying.png" alt="challenge_view_not_deployed" width="400"/>
<hr>
Once the job is finished, the deploy_status will change to `DEPLOYED`.<br>
<img src="/files/73de2d9a6251f413eff261a0fb93006a/byoa_deployed.png" alt="challenge_view_not_deployed" width="400"/>
<hr>
Each challenge will be deployed in its own VPC, which will be created during the deployment. You must have no more than 5 VPCs in your region, otherwise deployment will not work.

## Validate
After you have deployed the challenge, follow the challenge description/hints and try to fix ths problem in the cloud deployment.
Once you think you have solved the challenge by modifying the cloud configuration appropriately, click the `Validate` button.  
This will check the cloud environment, and if you have correctly fixed the problem as per the challenge guidance, it will return the flag.

## Destroy
Once you have solved a challenge, or if you just want to remove the deployment from your cloud account, click the `Destroy` button.
This will desstroy the VPC and all other related resources that were created from this challenge deployment.

