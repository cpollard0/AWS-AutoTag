import boto3

#ARN Formats:
#arn:partition:service:region:account-id:resource
#arn:partition:service:region:account-id:resourcetype/resource 
arnFormats = [
    { 
        "format":"arn:aws:{service}:{region}:{accountId}:{resourceType}/{resourceName}",
        "services":['volume','ec2']
    },
    { 
        "format":"arn:aws:{service}:{region}:{accountId}:{resourceType}:{resourceName}",
        "services":['rds']
    },
    { 
        "format":"arn:aws:{service}:{region}:{accountId}:resource",
        "services":['bar']
    },
    { 
        "format":"arn:aws:{service}:::{resourceName}",
        "services":['s3']
    }
]
#arn:partition:service:region:account-id:resourcetype:resource
#

def lambda_handler(event, context): 
    client = boto3.client('resourcegroupstaggingapi')  
    print(event)
    principal = event['detail']['userIdentity']['principalId']
    userType = event['detail']['userIdentity']['type']
    if userType == 'IAMUser':
        user = event['detail']['userIdentity']['userName']
    elif userType == 'Root':
        user = 'Root'
    else:
        user = principal.split(':')[1]
    #inspect event for type
    source = event['source'].replace('aws.','')
    if source == 'ec2':
        if event['detail']['responseElements']['volumeId']:
            resourceType = "volume"
            resourceName = event['detail']['responseElements']['volumeId'] 
    elif source == 's3':
        resourceName = event['detail']['requestParameters']['bucketName']
        resourceType = source
    
    info = {
        'service': source,
        'region':event['region'],
        'accountId':event['account'],
        'resourceName':resourceName,
        'resourceType':resourceType
    }
    arn = (item for item in arnFormats if resourceType in item["services"]).next()['format']
    print(arn)
    print(arn.format(**info))  
    response = client.tag_resources(
        ResourceARNList=[arn.format(**info)],
        Tags={'CreatedBy': user, 'CreateDate':event['time'][:10]}
    )
    return 'Successfully tagged resources'