.PHONY: init plan apply deploy
include ../.env
export

init:
	cd vpc && terraform init

plan:
	cd vpc && terraform plan

apply:
	cd vpc && terraform apply

deploy: init apply
