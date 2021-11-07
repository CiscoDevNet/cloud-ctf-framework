# BYOA Challenges for CTFd (Cisco Cloud CTF)

Custom Cisco plugin for BYOA challenges

## How it works

You can view all deploys at uri `/plugins/byoa_challenges/deploys`  
Admin users will see all deploys, regular users will only see their deploys.  

You can view specific challenge deploys details at uri `/plugins/byoa_challenges/deploy/<challenge_id>`

Admins can add optional `<team_id>` to end of the challenge deploy paths to view a specific teams challenge:  
Example: `/plugins/byoa_challenges/deploy/<challenge_id>/<team_id>`

If a non admin goes to another team id link, it will return 403.

Doing a POST request to this url will deploy that challenge.  

Currently the plan is all deploys, validations, destroys will just be container K8s jobs.
We can move this to native python if we want, but using k8s will make it easier to be asynchronous and to check status.


# OLD Idea
## How it works
When you add a new byoa challenge you must provide additional parameter(s):

`api_base_uri` - The base URI for where this challenge should be interacted with.  
Example: `/plugins/challenge-1-byoa`  
This will be used as base URI for the known BYOA actions (i.e. deploy, destroy, validate)

### Known BYOA actions
The known BYOA actions are ones which all the BYOA challenge plugins must provide. They are as follows:

`deploy` - This will deploy the challenge. 
URI Path: `<api_base_uri>/deploy`  
Example: If your `api_base_uri` was `/plugins/challenge-1-byoa` then the URI called to deploy this challenge would be
`/plugins/challenge-1-byoa/deploy`, which you would expect to have code to handle the deploy be in the `CTFd/plugins/challenge-1-byoa/__init__.py` file.

`destroy` - This will destroy the challenge.
URI Path: `<api_base_uri>/destroy`  
Example: If your `api_base_uri` was `/plugins/challenge-1-byoa` then the URI called to destroy this challenge would be
`/plugins/challenge-1-byoa/destroy`, which you would expect to have code to handle the destroy be in the `CTFd/plugins/challenge-1-byoa/__init__.py` file.

`validate` - This will validate the challenge.
URI Path: `<api_base_uri>/validate`  
Example: If your `api_base_uri` was `/plugins/challenge-1-byoa` then the URI called to validate this challenge would be
`/plugins/challenge-1-byoa/validate`, which you would expect to have code to handle the validate be in the `CTFd/plugins/challenge-1-byoa/__init__.py` file.

# Helpers and Utils

## Deploying challenges
Your plugin code can leverage the `byoa_challenges.deploy_challenge` function to deploy.

Example usage: TBD