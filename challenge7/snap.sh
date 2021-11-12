#!/bin/bash

keyword="*snapshot of image.vmdk*"
#keyword="*Classified*"

regions=( us-east-1 us-east-2 ap-south-1 )
for i in "${regions[@]}"
do
    echo -n "Region: ${i}"
    aws ec2 describe-snapshots --region ${i} --filters "Name=description,Values=$keyword"
done
