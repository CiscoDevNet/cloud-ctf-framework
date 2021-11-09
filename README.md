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