.PHONY: set-env show-env install build-ctfd push-ctfd run-ctfd stop-cftd start-ctfd rm-ctfd shell-ctfd build-bc push-bc
include .env
export

NS ?= cloud-ctf
IMAGE_NAME_CTFD ?= ctfd
VERSION ?= local
CCC_PATH_CTFD ?= containers.cisco.com/$(NS)/$(IMAGE_NAME_CTFD)
PUSH_TAG ?= manualbuild
LOCAL_CONTAINER_NAME_CTFD ?= cisco-cloud-ctfd

#Vars for BYOA deploy/destroy builds
CHALLENGE_REF_ARG ?= challenge1
BYOA_JOB_ACTION ?= deploy
IMAGE_NAME_BYOA_JOB = $(CHALLENGE_REF_ARG)-$(BYOA_JOB_ACTION)
CCC_PATH_BYOA_JOB ?= containers.cisco.com/$(NS)/$(IMAGE_NAME_BYOA_JOB)
BYOA_DOCKER_BUILD_FILE ?= Dockerfile.deploy_byoa_chal
RUN_SCRIPT_ARG ?= /opt/CloudCTF/deploy_byoa_chal.sh
TF_BASE_DIR_ARG ?= /opt/CloudCTF/$(CHALLENGE_REF_ARG)
LOCAL_CONTAINER_NAME_BYOA ?= $(IMAGE_NAME_BYOA_JOB)
LOCAL_TFSTATE_BASE_DIR ?= ${CURDIR}/.data/$(CHALLENGE_REF_ARG)

#This doesn't set the env outside of the make process, just use this which will echo the command, then you can copy and run it manually
set-env:
	set -o allexport && source .env && set +o allexport

show-env:
	env |grep -E 'AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY|AWS_REGION'

install:
	brew install terraform

build-ctfd:
	docker build -t $(NS)/$(IMAGE_NAME_CTFD):$(VERSION) .

push-ctfd: build-ctfd
	docker image tag $(NS)/$(IMAGE_NAME_CTFD):$(VERSION) $(CCC_PATH_CTFD):$(PUSH_TAG) && docker image push $(CCC_PATH_CTFD):$(PUSH_TAG)

run-ctfd:
	mkdir -p .data && touch .data/ctfd.db && docker run --name=$(LOCAL_CONTAINER_NAME_CTFD) -d --restart always -p 8000:8000 -v ${CURDIR}/.data/ctfd.db:/opt/CTFd/CTFd/ctfd.db -v ${CURDIR}:/opt/CloudCTF $(NS)/$(IMAGE_NAME_CTFD):$(VERSION)

stop-cftd:
	docker stop $(LOCAL_CONTAINER_NAME_CTFD)

start-ctfd:
	docker start $(LOCAL_CONTAINER_NAME_CTFD)

restart-ctfd:
	docker restart $(LOCAL_CONTAINER_NAME_CTFD)

rm-ctfd:
	docker rm -f $(LOCAL_CONTAINER_NAME_CTFD)

shell-ctfd:
	docker exec -it $(LOCAL_CONTAINER_NAME_CTFD) bash

rt: restart-ctfd tail-ctfd

tail-ctfd:
	docker logs --follow --tail 5 $(LOCAL_CONTAINER_NAME_CTFD)

build-bc:
	docker build -f $(BYOA_DOCKER_BUILD_FILE) -t $(NS)/$(IMAGE_NAME_BYOA_JOB):$(VERSION) --build-arg CHALLENGE_REF_ARG=$(CHALLENGE_REF_ARG) --build-arg RUN_SCRIPT_ARG=$(RUN_SCRIPT_ARG) --build-arg TF_BASE_DIR_ARG=$(TF_BASE_DIR_ARG) .

push-bc: build-bc
	docker image tag $(NS)/$(IMAGE_NAME_BYOA_JOB):$(VERSION) $(CCC_PATH_BYOA_JOB):$(PUSH_TAG) && docker image push $(CCC_PATH_BYOA_JOB):$(PUSH_TAG)

run-bc:
	docker run --rm --name $(LOCAL_CONTAINER_NAME_BYOA) --env TF_VAR_AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) --env TF_VAR_AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) --env TF_VAR_AWS_REGION=$(AWS_REGION) -v $(LOCAL_TFSTATE_BASE_DIR):/var/data/terraform $(NS)/$(IMAGE_NAME_BYOA_JOB):$(VERSION)
