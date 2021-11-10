#!/bin/bash

cd "$TF_BASE_DIR" || exit 4

terraform init
terraform plan
terraform apply -auto-approve
