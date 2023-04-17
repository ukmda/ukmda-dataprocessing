# Copyright (C) 2018-2023 Mark McIntyre
#
# python to resubmit failed getExtraFiles runs
#
import boto3
import datetime
import os
import sys


templ = '{"Records": [{"s3": {"bucket": {"name": "ukmon-shared",\
    "arn": "arn:aws:s3:::ukmon-shared"},"object": {"key": "KEYHERE"}}}]}'


def checkMissedFTPdetect(prof='ukmonshared'):
    session=boto3.Session(profile_name=prof) 
    logcli = session.client('logs', region_name='eu-west-2')
    chkdt = datetime.datetime.now() + datetime.timedelta(days=-1)
    chkdt = chkdt.replace(hour=0, minute=0, second=0, microsecond=0)
    uxt = int(chkdt.timestamp()*1000)
    fails=[]
    response = logcli.filter_log_events(
        logGroupName="/aws/lambda/consolidateFTPdetect",
        startTime=uxt,
        filterPattern="missing ",
        limit=1000)
    if len(response['events']) > 0:
        for i in range(len(response['events'])):
            msg = response['events'][i]['message'].strip()
            spls = msg.split()
            fails.append(spls[-1])
    if 'nextToken' in response:
        while True:
            currentToken = response['nextToken']
            response = logcli.filter_log_events(
                logGroupName="/aws/lambda/consolidateFTPdetect",
                startTime=uxt,
                filterPattern="missing ",
                nextToken = currentToken,
                limit=1000)
            if len(response['events']) > 0:
                for i in range(len(response['events'])):
                    msg = response['events'][i]['message'].strip()
                    spls = msg.split()
                    fails.append(spls[-1])
            if 'nextToken' not in response:
                break
    fails = list(set(fails)) # remove duplicates
    #print(fails)
    s3c = boto3.client('s3')
    lambd = session.client('lambda', region_name='eu-west-2')
    buck = 'ukmon-shared'
    for evt in fails:
        res = s3c.list_objects_v2(Bucket=buck,Prefix=f'{evt}/FTP')
        if res['KeyCount'] > 0:
            ftpname = res['Contents'][0]['Key']
            res = s3c.list_objects_v2(Bucket=buck,Prefix=f'{evt}/.config')
            res2 = s3c.list_objects_v2(Bucket=buck,Prefix=f'{evt}/platepars_all_recalibrated.json')
            if res['KeyCount'] == 0 or res2['KeyCount'] == 0:
                print(f'config or platepar still missing for {evt}')
            else:
                thisevent = templ.replace('KEYHERE', ftpname)
                response = lambd.invoke(
                    FunctionName='consolidateFTPdetect',
                    InvocationType='Event',
                    Payload=thisevent,
                )
                print(f'resubmitting {evt}, status {response["StatusCode"]}')
    return 


def findOtherBadEvents():
    evts = []
    datadir=os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    lastf = os.path.join(datadir,'dailyreports', 'latest.txt')
    with open(lastf, 'r') as inf:
        lis = inf.readlines()
    for li in lis:
        splis = li.split(',')
        trajdir = splis[1]
        trajdir = trajdir[trajdir.find('matches'):]
        _, orbname = os.path.split(trajdir)
        orbname = orbname[:15] + '_trajectory.pickle'
        orbname = trajdir + '/' + orbname
        evts.append(orbname)
    badevents = checkFails(evts)
    return badevents


def findFailedEvents(prof='ukmonshared'):
    #session = boto3.Session(profile_name=prof) 
    logcli = boto3.client('logs', region_name='eu-west-2')
    datadir=os.getenv('DATADIR', default='/home/ec2-user/prod/data')
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
        logGroupName="/aws/lambda/getExtraOrbitFilesV2",
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
                logGroupName="/aws/lambda/getExtraOrbitFilesV2",
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

    realfails = checkFails(fails)
    return realfails


def checkFails(fails):
    s3 = boto3.client('s3', region_name='eu-west-2')
    s3bucket=os.getenv('WEBSITEBUCKET', default='s3://ukmeteornetworkarchive')[5:]
    realfails = []
    for f in fails:
        # example f : matches/RMSCorrelate/trajectories/2022/202202/20220227/20220227_011240.522_UK
        orb = f[f.find('/20')+1:]
        orb = 'reports/' + orb[:5] + 'orbits' + orb[4:]
        pth, _ = os.path.split(orb)
        _, zipname = os.path.split(pth) 
        keyf = pth + '/' + zipname + '.zip'
        try:
            _ = s3.head_object(Bucket=s3bucket, Key=keyf)
            #print(f'{pth} already done')
        except:
            print(f'adding {keyf}')
            realfails.append(f)
    return realfails


def rerunFails(fails, prof='ukmonshared'):
    session=boto3.Session(profile_name=prof) 
    lambd = session.client('lambda', region_name='eu-west-2')

    datadir=os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    lastf = os.path.join(datadir,'orbits', 'lastorbitcheck.txt')
    with open(lastf, 'w') as outf:
        rundt = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        outf.write(f'{rundt}\n')
    
    for evt in fails:
        thisevent = templ.replace('KEYHERE', evt)
        print(thisevent)
        response = lambd.invoke(
            FunctionName='getExtraOrbitFilesV2',
            InvocationType='Event',
            Payload=thisevent,
        )
        print(response["StatusCode"])
    return 


def resubmitPicklesForDay(dtstr, prof='ukmonshared'):
    s3 = boto3.client('s3')
    session = boto3.Session(profile_name=prof)
    lambd = session.client('lambda', region_name='eu-west-2')
    pref = f'matches/RMSCorrelate/trajectories/{dtstr[:4]}/{dtstr[:6]}/{dtstr}/'
    res = s3.list_objects_v2(Bucket='ukmon-shared',Prefix=pref)
    print(res)
    if res['KeyCount'] > 0:
        print(f"processing {res['KeyCount']} entries")
        for k in res['Contents']:
            if 'pickle' in k['Key']:
                print(f"{k['Key']}")
                thisevent = templ.replace('KEYHERE', k['Key'])
                response = lambd.invoke(FunctionName='getExtraOrbitFilesV2',
                    InvocationType='Event', Payload=thisevent)
                print(response["StatusCode"])
    else:
        print('no keys found')
    return


if __name__ == '__main__':
    if len(sys.argv) > 1:
        failedevts = [sys.argv[1]]
    else:
        failedevts = findFailedEvents()
    realfails = failedevts
    #print(realfails)
    otherfails = findOtherBadEvents()
    #print(otherfails)
    realfails = list(dict.fromkeys(realfails + otherfails))
    rerunFails(realfails)
    numfails = len(realfails)
    print(f'resubmitted {numfails}')
