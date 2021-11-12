#!/bin/bash

cd "$TF_BASE_DIR" || exit 4
echo "current working dir:"
pwd
echo "file list:"
ls -lash

terraform init
terraform plan
terraform apply -auto-approve
