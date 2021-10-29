.PHONY: init plan apply deploy
include ../.env
export

show-env:
	env |grep -E 'AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY'

init:
	cd vpc && terraform init

plan:
	cd vpc && terraform plan

apply:
	cd vpc && terraform apply

deploy: init apply

destroy:
	cd vpc && terraform destroy