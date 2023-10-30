import boto3
import botocore


def lambda_handler(event, context):
    record = event['Records'][0]
    fname = record['s3']['object']['key']
    buck = record['s3']['bucket']['name']
    s3 = boto3.client('s3')
    targbuck='ukmda-live'
    try:
        s3.head_object(Bucket=targbuck, Key=fname)
        print(f'{fname} already exists in {targbuck}')
    except botocore.exceptions.ClientError:
        s3.copy_object(Bucket=targbuck, Key=fname, CopySource={'Bucket': buck, 'Key': fname}) 
        jpgf = fname.replace('.xml', 'P.jpg')
        s3.copy_object(Bucket=targbuck, Key=jpgf, CopySource={'Bucket': buck, 'Key': jpgf}) 
        print(f'copied {jpgf} to {targbuck}')
