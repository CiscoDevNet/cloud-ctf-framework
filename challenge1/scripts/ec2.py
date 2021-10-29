import boto3
session = boto3.Session(region_name="ap-south-1")


ec2 = session.resource('ec2',aws_access_key_id="xxxxxxxxxxxxxxxx", aws_secret_access_key="xxxxxxxxxxxxxxxx")

instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']},{'Name': 'tag:Name', 'Values': ['CloudCTFchall1']}])

count=0

for instance in instances:
    print(instance.id, instance.instance_type)
    count=count+1

print(count)
