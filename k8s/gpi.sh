#!/bin/bash
## Example:
#  gpi.sh mysql ctfd-dev
#  10.42.0.141
##
POD_FILTER=$1
NAMESPACE=$2

POD=`get_pod_name.sh $POD_FILTER $NAMESPACE`
get_pod_ip.sh $POD $NAMESPACE