# Steps for setting up K3 cluster
The following document will walk you through one example way to set up the infrastructure on Kubernetes.   
This example walkthrough uses [K3s](https://k3s.io/) as the K8s distribution since it is lightweight and easy to set up, but this project will work on any flavor of K8s.

# Set up the Kubernetes Cluster
The first step is to set up your Kubernetes cluster. If you already have a K8s cluster, you can skip to [the create a namespace step](#create-a-namespace).

## Quick Install Script
The below steps will walk you through the setup if you want to understand more about how it is deployed.  
If you want to run a script which will do all of the steps below for you, you can use the [k8s/k3s_setup.sh](k8s/k3s_setup.sh) script.  
```bash
cd k8s
./k3s_setup.sh
```

## Deploy K3s
Set up K3 cluster as per https://k3s.io/  
If you are just going to run 1 master node, it should be as simple as running 1 command:  
```bash
curl -sfL https://get.k3s.io | sh -
```

## Verify k3s kubectl get node
Once you've run the install, you can verify via the command below:
```bash
k3s kubectl get node
```
Example output:
```
NAME                 STATUS   ROLES                  AGE    VERSION
cloud-ctf-cisco   Ready    control-plane,master   215d   v1.21.5+k3s2
```
In this example our hostname of the server is `cisco-cloud-ctf`, which is also what K3s picked up as the name for the node.

# Create a namespace
We will now create a namespace on K8s which will hold all of our services, secrets, etc.  
```bash
kubectl create namespace cloud-ctf-cisco
```
The above command creates a new namespace called `cloud-ctf-cisco`

## Set your default namespace
Now that we have the namespace created we can set the current session to default to this namespace so that we do not need to add the namespace to every `kubectl` command.   
This is an optional step but note the rest of the guide assumes you set your default namespace to this and the example commands will not include that option.  
Command:
```
kubectl config set-context --current --namespace=cloud-ctf-cisco
```

# Clone this repository to the node
Now that we have figured out where we will host, we need to add the deployments to K8s. The easiest way to do this is to just clone this repository locally and then use the deployment yaml files.  
You can put this wherever you want on your server, `/opt/` is recommended for linux servers.  
Example
```
cd /opt
git clone https://github.com/CiscoDevNet/cloud-ctf-framework.git
cd cloud-ctf-framework
```
The above will clone the repository to the `/opt/cloud-ctf-framework` directory. 

# Deploy the application services
The next step is deploying all the services involved in running the application. This is accomplished by using the deployment yaml files provided in this repo for each service.  
There will be 3 deployments for the 3 services:  
- [CTFd App](#deploy-the-ctfd-web-app-service)
- [MySQL Server](#deploy-the-mysql-server)
- [Redis Server](#deploy-the-redis-server)

First, change to the `k8s/ctfd_configs` directory
```bash
cd k8s/ctfd_configs
```

## Deploy the ctfd web app service
First we will deploy the web application for ctfd. This will deploy the [open source CTFd project](https://github.com/CTFd/CTFd).  
The deployment yaml file will be `ctfd-deployment.yaml`  
Note: The deploy yaml files use the `cloud-ctf-cisco` namespace. If you are using a different namespace you will need to modify the yaml file first and change the namespace in all of the `namespace` entries.  
Deploy command:
```bash
kubectl apply -f ctfd-deployment.yaml
```
You should see output similar to:
```
persistentvolumeclaim/ctf-pv-logs created
persistentvolumeclaim/ctfd-pv-uploads created
deployment.apps/cloud-ctf-cisco created
service/ctfd created
```

You can list the services/deployments to verify:
```
# kubectl get services
NAME   TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
ctfd   ClusterIP   10.43.153.98   <none>        8000/TCP   2m

# kubectl get deployments
NAME              READY   UP-TO-DATE   AVAILABLE   AGE
cloud-ctf-cisco   1/1     1            1           2m7s
```

## Deploy the mysql server
The CTFd application requires a mysql database for persistent storage, so we will deploy that next using the `ctfd-mysql-deployment.yaml` file.
```
kubectl apply -f ctfd-mysql-deployment.yaml
```
Example output:
```
persistentvolumeclaim/ctfd-mysql-db-pv created
deployment.apps/ctfd-mysql-db created
service/ctfd-mysql-db created
```

## Deploy the redis server
The CTFd application requires a redis database to use for caching, so we will deploy that next using the `ctfd-redis-deployment.yaml` file.  
```
kubectl apply -f ctfd-redis-deployment.yaml
```
Example output:
```
persistentvolumeclaim/ctfd-redis-cache-pv created
deployment.apps/ctfd-redis-cache created
service/ctfd-redis-cache created
```

# Verify the application deployment
Now that we have deployed the services, we need to make sure everything is up and running as expected.

## List the deployments
First, list the deployments via `kubectl get deployments`  
Example output:
```
# kubectl get deployments
NAME               READY   UP-TO-DATE   AVAILABLE   AGE
ctfd-mysql-db      1/1     1            1           44h
ctfd-redis-cache   1/1     1            1           44h
ctfd               1/1     1            1           45h
```

## Get the cluster IP of the CTFd service
Next let's find the cluster IP address of the CTFd service so we can verify the web app is responding.  
Run the command `kubectl get service`  
Example output:
```
# kubectl get service
NAME               TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
ctfd               ClusterIP   10.43.153.98   <none>        8000/TCP   10m
ctfd-mysql-db      ClusterIP   10.43.94.189   <none>        3306/TCP   6m51s
ctfd-redis-cache   ClusterIP   10.43.88.233   <none>        6379/TCP   5m9s
```
From the above example output, the cluster IP address for the web service (ctfd) is `10.43.153.98` and it is listening on port `8000`. 
## Verify the CTFd HTTP service
Now let's make sure the HTTP service is replying to requests. To do this we can use something like `curl` from the CLI of a cluster node.  
```
curl http://10.43.153.98:8000
```
The response should look like below, which should give us a redirect to the setup page for CTFd:  
```html
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>Redirecting...</title>
<p>You should be redirected automatically to target URL: <a href="/setup">/setup</a>.  If not click the link.
```
This means that the CTFd application wants you to set it up, things are working!  

# Setting up the ingress to the application
Now that we have verified that the application is ready for setup, we need to set up the ingress.  
In the current state, this can only accept connections on the cluster IP, which is not exposed outside of the cluster, so it's not usable yet for anyone who is not a cluster admin.  
This is also only listening on HTTP, and not HTTPS. Since we are going to be accepting AWS credentials through this web application, 
it is highly recommended to only allow connections to the application on an encrypted connection.  

## Generate a self-signed certificate
We will simply use a self-signed certificate in this example, but it would be recommended to use proper PKI set up for the certificates, which may vary per cluster.
A simple one line command like below can be used to generate the self-signed cert and a new private key.
```
openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout ctfd-server.key -out ctfd-server.crt
```
This command will prompt you for information to populate the self-signed certificate with. Go through all the prompts. 
For this example we used `cisco-cloud-ctf-demo.cisco.com` as the Common Name on the cert:
```
Common Name (e.g. server FQDN or YOUR name) []:cisco-cloud-ctf-demo.cisco.com
```
This will create 2 files:  
`ctfd-server.key` - This contains the private key for the certificate (keep this secured)     
`ctfd-server.crt` - This is the certificate which will be presented to people when they connect to the application.

## Create a secret to hold the certificate data
Now that we have our certificate and key generated, we can add them to K8s as a secret so that we can reference them securely in our deployment.
Run the following command to add a secret called `cloudctfsecret` with `tls` as the type:
```bash
kubectl create secret tls cloudctfsecret --key ctfd-server.key --cert ctfd-server.crt
```
Example output:
```
secret/cloudctfsecret created
```

## Modify the ingress yaml
The last step for setting up the ingress in this example is to apply the `cloudingress.yaml` file, but first you need to make modifications to this file.  
You can make a copy of the file, note that the `local` directory inside of `ctfd_configs` is included in the `.gitignore` so you can do the following to make a copy:
```bash
mkdir local
cp cloudingress.yaml local/cloudingress.yaml
```
Now edit the `local/cloudingress.yaml` file and make the following changes:
1. Modify the ingress IP
The ingress IP is set to `<external ip of node>` in this yaml, set this to the IP address that people will be able to reach the node on externally.  
Example:
```yaml
status:
  loadBalancer:
    ingress:
      - ip: 10.83.181.181
```
2. Set the `spec->tls->hosts` and `spec->rules->host` to the proper hostname.
You will want to set these fields to the common name that you used on the self-signed certificate. 
In this example we used `cisco-cloud-ctf-demo.cisco.com` so our spec would look as follows:
```yaml
spec:
  tls:
    - hosts:
        - cisco-cloud-ctf-demo.cisco.com
      secretName: cloudctfsecret
  rules:
    - host: cisco-cloud-ctf-demo.cisco.com 
```

## Deploy the ingress
Now that you have made the changes to the ingress, you can apply it:
```bash
kubectl apply -f local/cloudingress.yaml
```
Example output:
```
ingress.networking.k8s.io/cloud-ctf-secure created
```

You can verify it was applied by running `kubectl get ingress`.  
Example:
```
# kubectl get ingress
NAME               CLASS    HOSTS                            ADDRESS         PORTS     AGE
cloud-ctf-secure   <none>   cisco-cloud-ctf-demo.cisco.com   10.83.181.181   80, 443   2m13s
```

# Navigate to the web app in a browser
That's it! Now you should have the CTFd application deployed on a K3s instance. 
Now you should be able to navigate to the application in a web browser so that you can start the setup.   
You will need to navigate to the hostname defined in your ingress in order to get to the web application.   
If you have not set up DNS records for the hostname on your ingress, you can shortcut that for now by just putting an entry into your local computer's `/etc/hosts` file (linux and Mac, windows also has a hosts file you can modify to add local entries)  

Example:  
add the following to /etc/hosts
```
10.83.181.181   cisco-cloud-ctf-demo.cisco.com
```

Now if I navigate to `https://cisco-cloud-ctf-demo.cisco.com` in a web browser I should see the Setup page for the CTFd. You can now go through the setup for CTFd.  


# Troubleshooting

## pods not starting due to PersistentVolumeClaims 
If you do not have a default storage class, or if the default storage class was not available when you applied the deployments, you might see something like below in the events when you describe the pod(s):  
`kubectl describe pod cloud-ctf-cisco-565dc49856-8szct`
```
Events:
Type     Reason            Age                 From               Message
  ----     ------            ----                ----               -------
Warning  FailedScheduling  18m                 default-scheduler  0/1 nodes are available: 1 pod has unbound immediate PersistentVolumeClaims.
Warning  FailedScheduling  93s (x17 over 18m)  default-scheduler  0/1 nodes are available: 1 pod has unbound immediate PersistentVolumeClaims
```

If you list the pvcs:  
`kubectl get pvc`
```bash
NAME                  STATUS    VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS   AGE
ctf-pv-logs           Pending                                                     31m
ctfd-pv-uploads       Pending                                                     31m
ctfd-mysql-db-pv      Pending                                                     31m
ctfd-redis-cache-pv   Pending                                                     31m
```
If you see the `STORAGECLASS` is blank, that means the default did not get applied at the time of the PVC creation.
This can happen if you deploy before the default storage class provisioner is ready. 

If you describe the pvc you should see something like below:
```bash
kubectl describe pvc ctf-pv-logs
Name:          ctf-pv-logs
Namespace:     cloud-ctf-cisco
StorageClass:
Status:        Pending
Volume:
Labels:        app=ctf-pv-logs
               ctfd=ctf-pv
Annotations:   <none>
Finalizers:    [kubernetes.io/pvc-protection]
Capacity:
Access Modes:
VolumeMode:    Filesystem
Used By:       cloud-ctf-cisco-565dc49856-8szct
Events:
  Type    Reason         Age                  From                         Message
  ----    ------         ----                 ----                         -------
  Normal  FailedBinding  89s (x122 over 31m)  persistentvolume-controller  no persistent volumes available for this claim and no storage class is set
```

If you get into this state you should destroy and re-deploy once the default SC is available, which can be done with the following 2 commands:
```
kubectl delete all --all --namespace cloud-ctf-cisco
kubectl delete pvc ctfd-pv-uploads ctfd-mysql-db-pv ctfd-redis-cache-pv ctf-pv-logs
```
If you don't want to (or don't have) a default storage class, you will need to modify the deployment yamls and add a `storageClassName` under the spec for each PersistentVolumeClaim.  
Example:
add `storageClassName: my-storage-class` under the spec:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  namespace: cloud-ctf-cisco
  creationTimestamp: null
  labels:
    ctfd: ctf-pv
    app: ctfd-pv-uploads
  name: ctfd-pv-uploads
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 500Mi
  storageClassName: my-storage-class
```
If you don't specify one it will use the cluster's default.