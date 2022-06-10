#!/bin/bash
# Does the k3s set up end-to-end
# Installs k3s
# Deploys all ctfd resources

curl -sfL https://get.k3s.io | sh -

echo "sleeping to give k3s some time to initialize..."
sleep 15
kubectl create namespace cloud-ctf-cisco

kubectl config set-context --current --namespace=cloud-ctf-cisco

cd ctfd_configs

kubectl apply -f ctfd-deployment.yaml

kubectl apply -f ctfd-mysql-deployment.yaml

kubectl apply -f ctfd-redis-deployment.yaml


openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout ctfd-server.key -out ctfd-server.crt

kubectl create secret tls cloudctfsecret --key ctfd-server.key --cert ctfd-server.crt

mkdir -p local
cp cloudingress.yaml local/cloudingress.yaml

vim local/cloudingress.yaml


kubectl apply -f local/cloudingress.yaml
