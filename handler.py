import boto3

# ARN Formats:
# arn:partition:service:region:account-id:resource
# arn:partition:service:region:account-id:resourcetype/resource
arnFormats = [
    {
        "format": "arn:aws:{service}:{region}:{accountId}:{resourceType}/{resourceName}",
        "services": [ 'ec2', 'dynamodb', 'elasticloadbalancing']
    },
    {
        "format": "arn:aws:{service}:{region}:{accountId}:{resourceType}:{resourceName}",
        "services": ['rds']
    },
    {
        "format": "arn:aws:{service}:{region}:{accountId}:resource",
        "services": ['bar']
    },
    {
        "format": "arn:aws:{service}:::{resourceName}",
        "services": ['s3']
    }
]


# arn:partition:service:region:account-id:resourcetype:resource
#

def auto_tag_handler(event, context):
    client = boto3.client('resourcegroupstaggingapi')
    print(event)

    info = extractInfoFromEvent(event)
    response = client.tag_resources(
        ResourceARNList=[buildARN(info)],
        Tags={'CreatedBy': info['user'], 'CreateDate': event['time'][:10]}
    )
    return response


def extractInfoFromEvent(event):
    principal = event['detail']['userIdentity']['principalId']
    userType = event['detail']['userIdentity']['type']
    if userType == 'IAMUser':
        user = event['detail']['userIdentity']['userName']
    elif userType == 'Root':
        user = 'Root'
    else:
        user = principal.split(':')[1]
    # inspect event for type
    source = event['source'].replace('aws.', '')
    resourceType = source
    if source == 'ec2':
        if 'volumeId' in event['detail']['responseElements']:
            resourceType = u'volume'
            resourceName = event['detail']['responseElements']['volumeId']
    elif source == 'elasticloadbalancing':
        resourceType = u'loadbalancer'
        resourceName = event['detail']['requestParameters']['loadBalancerName']
    elif source == 's3':
        resourceName = event['detail']['requestParameters']['bucketName']
        resourceType = source
    elif source == 'dynamodb':
        resourceName = event['detail']['requestParameters']['tableName']
        resourceType = 'table'
    return {
        'service': source,
        'region': event['region'],
        'accountId': event['account'],
        'resourceName': resourceName,
        'resourceType': resourceType,
        'user': user
    }


def  buildARN (info):
    arn = (item for item in arnFormats if info['service'] in item["services"]).next()['format']
    return arn.format(**info)
