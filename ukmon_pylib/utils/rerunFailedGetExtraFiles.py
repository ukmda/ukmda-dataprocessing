#
# python to resubmit failed getExtraFiles runs
#
import boto3
import datetime
import os
import sys


templ = '{"Records": [{"s3": {"bucket": {"name": "ukmon-shared",\
    "arn": "arn:aws:s3:::ukmon-shared"},"object": {"key": "KEYHERE"}}}]}'


def findFailedEvents():
    logcli = boto3.client('logs', region_name='eu-west-2')
    datadir=os.getenv('DATADIR')
    lastf = os.path.join(datadir,'orbits', 'lastorbitcheck.txt')
    if os.path.isfile(lastf):
        with open(lastf, 'r') as inf:
            dt = inf.readline().strip()
        chkdt = datetime.datetime.strptime(dt, '%Y%m%d_%H%M%S')
    else:
        chkdt = datetime.datetime.now() + datetime.timedelta(days=-1)
        chkdt = chkdt.replace(hour=0, minute=0, second=0, microsecond=0)

    print(chkdt)
    uxt = int(chkdt.timestamp()*1000)

    fails=[]
    response = logcli.filter_log_events(
        logGroupName="/aws/lambda/getExtraFiles",
        startTime=uxt,
        filterPattern="Error processing ",
        limit=1000)
    if len(response['events']) > 0:
        for i in range(len(response['events'])):
            msg = response['events'][i]['message'].strip()
            spls = msg.split(' ')
            fails.append(spls[2])
    if 'nextToken' in response:
        while True:
            currentToken = response['nextToken']
            response = logcli.filter_log_events(
                logGroupName="/aws/lambda/getExtraFiles",
                startTime=uxt,
                filterPattern="Error processing ",
                nextToken = currentToken,
                limit=1000)
            if len(response['events']) > 0:
                for i in range(len(response['events'])):
                    msg = response['events'][i]['message'].strip()
                    spls = msg.split(' ')
                    fails.append(spls[2])
            if 'nextToken' not in response:
                break
    
    return fails


def checkFails(fails):
    s3 = boto3.client('s3', region_name='eu-west-2')
    s3bucket='ukmon-shared'
    realfails = []
    for f in fails:
        pth, _ = os.path.split(f)
        _, zipname = os.path.split(pth) 
        keyf = pth + '/' + zipname + '.zip'
        try:
            _ = s3.head_object(Bucket=s3bucket, Key=keyf)
            print('already done')
        except:
            realfails.append(f)
    return realfails


def rerunFails(fails):
    lambd = boto3.client('lambda', region_name='eu-west-2')

    datadir=os.getenv('DATADIR')
    lastf = os.path.join(datadir,'orbits', 'lastorbitcheck.txt')
    with open(lastf, 'w') as outf:
        rundt = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        outf.write(f'{rundt}\n')
    
    for evt in fails:
        thisevent = templ.replace('KEYHERE', evt)
        print(thisevent)
        response = lambd.invoke(
            FunctionName='getExtraFiles',
            InvocationType='Event',
            Payload=thisevent,
        )
        print(response["StatusCode"])
    return 


if __name__ == '__main__':
    if len(sys.argv) > 1:
        failedevts = [sys.argv[1]]
    else:
        failedevts = findFailedEvents()
    realfails = checkFails(failedevts)
    print(realfails)
    print(len(realfails))
    rerunFails(realfails)
