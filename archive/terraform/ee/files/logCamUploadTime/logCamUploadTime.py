#
# lambda function to be triggered when a csv file arrives in ukmon-shared
# to copy it to the temp area for consolidation later
#
import boto3


# add a row to the CamTimings table
def addRowCamTimings(s3bucket, s3object):
    s3c = boto3.client('s3')
    dtstamp = s3c.head_object(Bucket=s3bucket, Key=s3object)['LastModified']
    ddb = boto3.resource('dynamodb', region_name='eu-west-1') 
    table = ddb.Table('ukmon_uploadtimes')
    # s3object = archive/Tackley/UK0006/2022/202211/20221102/.config
    spls = s3object.split('/')
    camid = spls[2]
    manual = False
    uploaddate = dtstamp.strftime('%Y%m%d')
    uploadtime = dtstamp.strftime('%H%M%S')
    table.put_item(
        Item={
            'stationid': camid,
            'dtstamp': uploaddate + '_' + uploadtime,
            'uploaddate': int(uploaddate),
            'uploadtime': int(uploadtime),
            'manual': manual
        }
    )   
    return 


def lambda_handler(event, context):
    record = event['Records'][0]

    s3bucket = record['s3']['bucket']['name']
    s3object = record['s3']['object']['key']

    addRowCamTimings(s3bucket, s3object)
    return 0
