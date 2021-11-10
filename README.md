# CloudCTF
this the repo for cloud ctf 

# Container Registry
This is the custom ctfd image we will use for the competition which will be deployed in the k3s cluster:  
https://containers.cisco.com/repository/cloud-ctf/ctfd

# Local Development
This project is managed via Makefile. You can build and push ctfd image, as well as stand up a local instance of ctfd.

## Quick Start
Build ctfd container with custom code (plugins)
```bash
make build-ctfd
```

Run the container:
```bash
make run-ctfd
```

Navigate to http://localhost:8000 to setup your local ctfd instance.

If you make changes to your plugin code you need to restart services to pick up the changes in ctfd app:
```bash
make restart-ctfd
```

## Running ctfd locally

### Build the container
Build ctfd container with custom code (plugins)
```bash
make build-ctfd
```

### Start the container
```bash
make run-ctfd
```

This will start a docker container with ctfd and port 8000 exposed on localhost.
Go to http://localhost:8000 to access the web UI after running above command.

### Shell into the container
If you want to shell into the running container, run:
```bash
make shell-ctfd
``` 
which will drop you into the container at root of hte CTFd project (/opt/CTFd)

### Persistent DB for local dev
The database for local development is sqllite, and the file will be at `.data/ctfd.db`, 
which is linked into the running container at `/opt/CTFd/CTFd/ctfd.db`

### Add k8s config to test k8s jobs
Put your kube config file in location `.data/kube-config` if you want to test deploy/destroy k8s jobs.
The dockerfile will symlink this file to `/home/ctfd/.kube/config` so if it exists it will just work. 
When in production this file is passed in as a volume which will overwrite the symlink.

If you want to test k8s jobs locally, you need to create your own namespace in the cluster to stick the jobs. Once you have that, you need to re-run the ctfd local container and pass the `CTF_K8S_NAMESPACE` variable. for example:
```bash
make run-cftd CTF_K8S_NAMESPACE=my-namespace
```

Note that if you are doing this, you will not be able to access the terraform state locally as the terraform state will be stored in the cluster inside of a PersistentVolume.  
To test the deploy/destroy operations, just use the `bc` make commands, you will not be able to test 100% end-to-end locally for the deploy/destory/validate.
### Stop CTFd
```bash
make stop-ctfd
```

### Start CTFd (if already created)
If the container already exists and you ran `make stop-ctfd` and just want to start it again, just run:
```bash
make start-ctfd
```

You can also remove the container to stop services
```bash
make rm-ctfd
```

### Delete current app and start a new one
If you want to delete current data and make a new fresh ctfd application:
1. Remove the current container: `make rm-ctfd`
2. Remove the db file: `rm .data/ctfd.db`
3. Start the container again: `make run-ctfd`

The ctfd application UI should now take you through the ctfd set up.


# Building and pushing images
The ctfd container image just extends the default ctfd docker container image and then copies files into place as needed.
Primarily, this just copies plugins from this directory into `/opt/CTFd/CTFd/plugins/`

## Build image locally
To make a local image:
```bash
make build-ctfd
```

## Push image to container registry (containers.cisco.com)
To push up a new image run:
```bash
make push-ctfd
```
Note: this will build and then push, so you do not need to run the build command before running this.
Once you push a new version, you should make a tag for that version. by default this push will just push the image to the "manualtag" label. you should copy this to a v<version> label (i.e. v21 if last version was v20)


# Building BYOA Challenge job images

To build a challenge image job, i.e. by default it will be challenge1-deploy image:
```bash
make build-bc
```
This results in a build command as follows:  
```
docker build \
    -f Dockerfile.deploy_byoa_chal \
    -t cloud-ctf/challenge1-deploy:local \
    --build-arg CHALLENGE_REF_ARG=challenge1 \
    --build-arg RUN_SCRIPT_ARG=/opt/CloudCTF/deploy_byoa_chal.sh \
    --build-arg TF_BASE_DIR_ARG=/opt/CloudCTF/challenge1 \
    .
```
You can see how this is built, and you can override build variables as needed to the make command
```
CHALLENGE_REF_ARG ?= challenge1
BYOA_JOB_ACTION ?= deploy
IMAGE_NAME_BYOA_JOB = $(CHALLENGE_REF_ARG)-$(BYOA_JOB_ACTION)
CCC_PATH_BYOA_JOB ?= containers.cisco.com/$(NS)/$(IMAGE_NAME_BYOA_JOB)
BYOA_DOCKER_BUILD_FILE ?= Dockerfile.deploy_byoa_chal
RUN_SCRIPT_ARG ?= /opt/CloudCTF/deploy_byoa_chal.sh
TF_BASE_DIR_ARG ?= /opt/CloudCTF/$(CHALLENGE_REF_ARG)
```

For example, assuming challenge1 terraform base path is inside of the `vpc` dir,  
then we need to use a different path for `TF_BASE_DIR_ARG` docker build arg.  
We will run make command to achieve this:
```bash
make build-bc TF_BASE_DIR_ARG=/opt/CloudCTF/challenge1/vpc
```


## Builds for each challenge:
## challenge1
build deploy image:
```bash
make build-bc TF_BASE_DIR_ARG=/opt/CloudCTF/challenge1/vpc
```
Run the deploy image:
```bash
make run-bc CHALLENGE_REF_ARG=challenge1
```
push deploy image:
```bash
make push-bc TF_BASE_DIR_ARG=/opt/CloudCTF/challenge1/vpc
```

build destroy image:
```bash
make build-bc TF_BASE_DIR_ARG=/opt/CloudCTF/challenge1/vpc BYOA_JOB_ACTION=destroy
```
Run the destroy image:
```bash
make run-bc CHALLENGE_REF_ARG=challenge1 BYOA_JOB_ACTION=destroy
```
push destroy image:
```bash
make push-bc TF_BASE_DIR_ARG=/opt/CloudCTF/challenge1/vpc BYOA_JOB_ACTION=destroy
```

## Other challenges
The other challenges are all the same structure, so you only need to provide the `CHALLENGE_REF_ARG` and `BYOA_JOB_ACTION` variables.  
The only difference between the challenges is the `CHALLENGE_REF_ARG` so these steps are the same except you pass that challenge ref value you want to build. 
### Example challenge2
build challenge2 deploy image:
```bash
make build-bc CHALLENGE_REF_ARG=challenge2
```
Run the challenge2 deploy image:
```bash
make run-bc CHALLENGE_REF_ARG=challenge2
```
push challenge2 deploy image:
```bash
make push-bc CHALLENGE_REF_ARG=challenge2
```

build challenge2 destroy image:
```bash
make build-bc CHALLENGE_REF_ARG=challenge2 BYOA_JOB_ACTION=destroy
```
Run the challenge2 destroy image:
```bash
make run-bc CHALLENGE_REF_ARG=challenge2 BYOA_JOB_ACTION=destroy
```
push the challenge2 destroy image:
```bash
make push-bc CHALLENGE_REF_ARG=challenge2 BYOA_JOB_ACTION=destroy
```