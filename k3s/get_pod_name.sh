#!/bin/bash
## Example:
#  get_pod_ip.sh ctfd-mysql-db-65f59f5dc8-wdzwg ctfd-dev
#  10.42.0.141
##

POD_FILTER=$1
NAMESPACE=$2

IP_STR=`kubectl get pods -n$NAMESPACE |grep $POD_FILTER`
IP_ARR=(${IP_STR//: / })
echo ${IP_ARR[0]}