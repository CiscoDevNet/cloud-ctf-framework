# Steps for setting up K3 cluster
1) Set up K3 cluster as per https://k3s.io/
2) Command to verify k3s kubectl get node
NAME                 STATUS   ROLES                  AGE    VERSION
cloudctfseccon2021   Ready    control-plane,master   215d   v1.21.5+k3s2
3) kubectl create namespace cloud-ctf-cisco
4) kubectl config set-context --current --namespace=cloud-ctf-cisco
5) git clone https://github.com/CiscoDevNet/cloud-ctf-framework.git
6) cd CiscoDevNet/k3s/ctfd-configs
7) kubectl apply -f ctfd-deployment.yaml
8) kubectl apply -f ctfd-mysql-deployment.yaml
9) kubectl apply -f ctfd-redis-deployment.yaml
10) Verification of the application being deployed
kubectl get deployments
NAME               READY   UP-TO-DATE   AVAILABLE   AGE
ctfd-mysql-db      1/1     1            1           44h
ctfd-redis-cache   1/1     1            1           44h
ctfd               1/1     1            1           45h
11) Get the cluster ip of the ctfd service
kubectl get service
NAME               TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
ctfd               ClusterIP   10.43.93.92     <none>        8000/TCP   45h
ctfd-mysql-db      ClusterIP   10.43.145.210   <none>        3306/TCP   45h
ctfd-redis-cache   ClusterIP   10.43.152.0     <none>        6379/TCP   44h
12) Make a curl request to the custer ip curl http://10.43.93.92:8000
Response should be like below which gives us to configure the CTFD page.
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>Redirecting...</title>
<p>You should be redirected automatically to target URL: <a href="/setup">/setup</a>.  If not click the link.

13) Generate self signed certificate as below 
openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout server.key -out server.crt

14) Create a secret using command 
kubectl create kubectl create secret tls cloudctfsecret --key server.key --cert server.crt

15) kubectl apply -f cloudingress.yaml
