.PHONY: set-env show-env install build-ctfd push-ctfd run-ctfd stop-cftd start-ctfd rm-ctfd shell-ctfd
include .env
export

NS ?= cloud-ctf
IMAGE_NAME_CTFD ?= ctfd
VERSION ?= local
CCC_PATH_CTFD ?= containers.cisco.com/$(NS)/$(IMAGE_NAME_CTFD)
PUSH_TAG ?= manualbuild
LOCAL_CONTAINER_NAME_CTFD ?= cisco-cloud-ctfd

#This doesn't set the env outside of the make process, just use this which will echo the command, then you can copy and run it manually
set-env:
	set -o allexport && source .env && set +o allexport

show-env:
	env |grep -E 'AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY'

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