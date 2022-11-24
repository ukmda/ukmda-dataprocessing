#
# lambda function to be triggered when a csv file arrives in ukmon-shared
# to copy it to the temp area for consolidation later
#
import boto3
import os
from urllib.parse import unquote_plus


def lambda_handler(event, context):

    s3 = boto3.resource('s3')

    record = event['Records'][0]

    s3bucket = record['s3']['bucket']['name']
    s3object = record['s3']['object']['key']
    target = 'ukmon-shared'

    _, fname = os.path.split(s3object)
    if fname[:3] !='M20' and fname[6:9] != '_20':
        # yep not interested
        print(f'ignoring {s3object}')
        return 0

    outf = 'consolidated/temp/' + fname
    s3object = unquote_plus(s3object)
    print(s3object)
    print(outf)
    src = {'Bucket': s3bucket, 'Key': s3object}
    s3.meta.client.copy_object(Bucket=target, Key=outf, CopySource=src)

    return 0
