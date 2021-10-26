.PHONY: init plan apply deploy
include ../.env
export

export TF_VAR_AWS_ACCESS_KEY_ID = $(AWS_ACCESS_KEY_ID)
export TF_VAR_AWS_SECRET_ACCESS_KEY = $(AWS_SECRET_ACCESS_KEY)

init:
	terraform init

plan:
	terraform plan

apply:
	terraform apply

deploy: init apply
