import boto3


def vpc(ACCESS_KEY,SECRET_KEY):



    #ACCESS_KEY = 'AKIA5AG3WQBBJK3NOJVV'
    #SECRET_KEY = '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'

    client = boto3.client('ec2',aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

    #e=client.describe_instances()
    session = boto3.Session(region_name="ap-south-1")


    ec2 = session.resource('ec2')

    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']},{'Name': 'tag:Name', 'Values': ['CloudCTFchall1']}])
    
    print(type(instances))

    for instance in instances:
        print(instance.id, instance.instance_type) 
    #e=e['Reservations']
    #print(e['Instances'])

    a= client.describe_vpcs()

    #print(a)

    b=a['Vpcs']
    dict={}
    #print('no of vpc is', len(b))

    for i in range(len(b)):
        #print(b[i]['IsDefault'])
        
        if b[i]['IsDefault']==False:
            
            e=b[i]['Tags'][0]['Value']
            dict[e]= b[i]['VpcId']

        
            
        
        elif b[i]['IsDefault']==True:
            dict['Default']=b[i]['VpcId']
        
            


    #print(dict)


if __name__=='__main__':

    access_key = 'AKIA5AG3WQBBJK3NOJVV'
    secret_key = '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'
    #print('access key is',access_key)

    vpc(access_key,secret_key)

