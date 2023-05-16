import boto3
import datetime


templ = '{"Records": [{"s3": {"object": {"key": "KEYHERE"}}}]}'


def test_curateLiveOneFile(fname=None):
    if fname is None:
        dtstr = datetime.datetime.now().strftime('%Y%m%d')
        s3 = boto3.client('s3')
        x = s3.list_objects_v2(Bucket='ukmon-live',Prefix=f'M{dtstr}')
        if x['KeyCount'] > 0:
            fname = x['Contents'][0]['Key']
        else:
            dtstr = (datetime.datetime.now()+datetime.timedelta(days=-1)).strftime('%Y%m%d')
            x = s3.list_objects_v2(Bucket='ukmon-live',Prefix=f'M{dtstr}')
            fname = x['Contents'][0]['Key']
        fname = fname.replace('P.jpg', '.xml')
    lmb = boto3.client('lambda', region_name='eu-west-1')
    payload = templ.replace('KEYHERE', fname)
    resp = lmb.invoke(FunctionName = 'MonitorLiveFeed', InvocationType='Event', LogType='None', Payload = payload)
    assert resp['ResponseMetadata']['HTTPStatusCode'] < 300
