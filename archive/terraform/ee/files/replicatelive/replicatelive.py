import boto3


def lambda_handler(event, context):
    record = event['Records'][0]
    fname = record['s3']['object']['key']
    buck = record['s3']['bucket']['name']
    s3 = boto3.client('s3')
    targbuck='ukmda-live'
    s3.copy_object(Bucket=targbuck, Key=fname, CopySource={'Bucket': buck, 'Key': fname}) 
    jpgf = fname.replace('.xml', 'P.jpg')
    s3.copy_object(Bucket=targbuck, Key=jpgf, CopySource={'Bucket': buck, 'Key': jpgf}) 
    print(f'copied {jpgf} to {targbuck}')
    print(buck, fname)
