# Copyright (C) 2018-2023 Mark McIntyre
#
# Used when running the correlator in 'distributed' mode. 
# Pick up new groups of candidate trajectories and distribute them, 
# then wait for completion and gather the logs. 
#

import json
import os
import sys
import glob
import math
import datetime
import boto3
import time
import pickle


def getClusterDetails(templdir):
    sts = boto3.client('sts')
    accid = sts.get_caller_identity()['Account']
    if accid == '183798037734':
        clusdetails = os.path.join(templdir, 'clusdetails-mda.txt')
    else:
        clusdetails = os.path.join(templdir, 'clusdetails-mm.txt')
    with open(clusdetails) as inf:
        lis = inf.readlines()
    clusname = lis[0].strip()
    secgrp = lis[1].strip()
    subnet = lis[2].strip()
    exrolearn = lis[3].strip()
    loggrp = lis[4].strip()
    contname = lis[5].strip()
    return [clusname, secgrp, subnet, exrolearn, loggrp, contname]


def createTaskTemplate(rundate, buckname, clusdets, spandays=3):
    d1 = (rundate + datetime.timedelta(days = -(spandays-1))).strftime('%Y%m%d')
    d2 = (rundate + datetime.timedelta(days = 1)).strftime('%Y%m%d')

    templdir,_ = os.path.split(__file__)
    templatefile = os.path.join(templdir, 'taskrunner.json')
    clusname = clusdets[0]
    secgrp = clusdets[1]
    subnet = clusdets[2]
    exrolearn = clusdets[3]

    _, buckname = os.path.split(buckname)
    with open(templatefile) as inf:
        templ = json.load(inf)
        templ['cluster'] = clusname
        templ['networkConfiguration']['awsvpcConfiguration']['subnets'] = [f'{subnet}']
        templ['networkConfiguration']['awsvpcConfiguration']['securityGroups'] = [f'{secgrp}']
        templ['overrides']['executionRoleArn'] = exrolearn
        templ['overrides']['containerOverrides'][0]['command'] = [f'{buckname}', f'{d1}', f'{d2}']

    return templ


def getDebugStatus():
    dbg = os.getenv('DEBUG', default='0')
    if dbg == '1':
        return True
    else:
        return False


def distributeCandidates(rundate, srcdir, targdir, clusdets, maxcount=20):

    clusname = clusdets[0]

    ecsclient = boto3.client('ecs', region_name='eu-west-2')
    status = ecsclient.describe_clusters(clusters=[clusname])
    if len(status['clusters']) == 0:
        print('cluster not running!')
        return False

    print(f'Reading from {srcdir}')
    # obtain a list of picklefiles and sort by name
    flist = glob.glob1(srcdir, '*.pickle')
    if len(flist) == 0:
        print('no candidates to process')
        return False
    flist.sort()

    # work out how many buckets i need
    numcands = len(flist)
    numbucks = int(math.ceil(numcands/maxcount))

    # create buckets
    targdir = targdir[5:]
    outbucket=targdir[:targdir.find('/')]
    targdir = targdir[targdir.find('/')+1:]
    buckroot = os.path.join(targdir, rundate.strftime('%Y%m%d'))

    taskarns = [None] * numbucks
    jsontempls = [None] * numbucks
    bucknames = [None] * numbucks

    isDbg = getDebugStatus()

    s3 = boto3.client('s3')
    for i in range(0, numbucks):
        bucknames[i] = buckroot + f'_{i:02d}'
        filelist = flist[i::numbucks]
        for fli in filelist:
            src = os.path.join(srcdir, fli)
            dst = os.path.join(bucknames[i], fli)
            s3.upload_file(src, outbucket, dst)

        taskjson = createTaskTemplate(rundate, bucknames[i], clusdets)

        response = ecsclient.run_task(**taskjson)
        while len(response['tasks']) == 0:
            response = ecsclient.run_task(**taskjson)

        taskarn = response['tasks'][0]['taskArn']
        taskarns[i] = taskarn
        jsontempls[i] = taskjson
        print(taskarn[51:])
        if isDbg is True and i == 3:
            break
    
    # in debug mode, we don't fill the arrays entirely
    taskarns = [e for e in taskarns if e is not None]
    bucknames = [e for e in bucknames if e is not None]
    jsontempls = [e for e in jsontempls if e is not None]

    print(f' {len(flist)} candidates, {len(taskarns)} arns')
    dmpdata = [bucknames, taskarns, clusname]

    src = os.path.join('/tmp', rundate.strftime('%Y%m%d') + '.pickle')
    dst = buckroot + '.pickle'

    pickle.dump(dmpdata, open(src,'wb'))
    s3.upload_file(src, outbucket, dst)

    status = ecsclient.describe_clusters(clusters=[clusname])
    rtc = status['clusters'][0]['runningTasksCount']
    ptc = status['clusters'][0]['pendingTasksCount']
    print(f'{rtc} running, {ptc} pending')

    return True


def monitorProgress(rundate):
    client = boto3.client('ecs', region_name='eu-west-2')
    s3 = boto3.client('s3')
    archbucket = os.getenv('UKMONSHAREDBUCKET', default='s3://ukmda-shared')[5:]
    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')

    templdir,_ = os.path.split(__file__)
    clusdets = getClusterDetails(templdir)

    # load the buckets, tasks and cluster name from the dump file
    rundate = datetime.datetime.strptime(rundate, '%Y%m%d')
    picklefile = os.path.join(datadir, 'distrib', rundate.strftime('%Y%m%d') + '.pickle')
    rempickle = f"matches/distrib/{rundate.strftime('%Y%m%d')}.pickle"
    try:
        s3.download_file(archbucket, rempickle, picklefile)
    except:
        print('no containers to monitor')
        return 
    dumpdata = pickle.load(open(picklefile,'rb'))
    bucknames = dumpdata[0]
    taskarns = dumpdata[1]
    clusname = dumpdata[2]

    # details of the loggroup and container name 
    loggrp = clusdets[4]
    contname = clusdets[5]

    # need to keep list of task ARNs and then check if they started properly.
    # Look for "lastStatus": "STOPPED",
    # if not "stopCode": "EssentialContainerExited"
    # then launch it again

    # wait 20s before testing whether everything is running
    time.sleep(20.0)
    print('starting checks')    
    taskcount = len(taskarns)
    while taskcount > 0:
        # can't describe more than 99 tasks at a time
        sts = client.describe_tasks(cluster=clusname, tasks=taskarns[:99])
        #print(sts)
        for tsk in sts['failures']:
            if tsk['reason'] == 'MISSING':
                idx = taskarns.index(tsk['arn'])
                thisarn=taskarns.pop(idx)
                thisbuck = bucknames.pop(idx)
                taskcount -= 1
                _, thisbuck = os.path.split(thisbuck)
                try:
                    pref = f'matches/distrib/{thisbuck}/'
                    objects_to_delete = s3.list_objects(Bucket=archbucket, Prefix=pref)
                    delete_keys = {'Objects': []}
                    delete_keys['Objects'] = [{'Key': k} for k in [obj['Key'] for obj in objects_to_delete.get('Contents', [])]]
                    s3.delete_objects(Bucket=archbucket, Delete=delete_keys)
                except:
                    print('folder already removed')
                print(f'task {tsk["arn"][51:]} completed already')
        for tsk in sts['tasks']:
            print(f'checking {tsk["taskArn"][51:]}')
            idx = taskarns.index(tsk['taskArn'])
            #print(tsk['taskArn'], tsk['lastStatus'])
            if tsk['lastStatus'] == 'STOPPED':
                if tsk['stopCode'] != 'EssentialContainerExited':
                    # retry the task
                    thisjson = createTaskTemplate(rundate, bucknames[idx])
                    response = client.run_task(**thisjson)
                    taskarns[idx] = response['tasks'][0]['taskArn']
                    print('task restarted')
                else:
                    thisarn=taskarns.pop(idx)
                    thisbuck = bucknames.pop(idx)
                    taskcount -= 1
                    _, thisbuck = os.path.split(thisbuck)
                    try:
                        pref = f'matches/distrib/{thisbuck}/'
                        objects_to_delete = s3.list_objects(Bucket=archbucket, Prefix=pref)
                        delete_keys = {'Objects': []}
                        delete_keys['Objects'] = [{'Key': k} for k in [obj['Key'] for obj in objects_to_delete.get('Contents', [])]]
                        s3.delete_objects(Bucket=archbucket, Delete=delete_keys)
                    except:
                        print('folder already removed')
                    print('task completed')

                    # collect the logs from CloudWatch 
                    realfname=None
                    logdir = os.path.join(datadir, '..', 'logs', 'distrib')
                    os.makedirs(logdir, exist_ok=True)
                    tmpfname = os.path.join(logdir, f'{thisarn[51:]}.log')
                    with open(tmpfname, 'w') as outf:
                        for events in getLogDetails(loggrp, thisarn[51:], contname):
                            for evt in events:
                                evtdt = datetime.datetime.fromtimestamp(int(evt['timestamp']) / 1000)
                                msg = evt['message']
                                outf.write(f'{evtdt} {msg}\n')
                                if msg[:10] == 'processing':
                                    realfname = msg[11:].strip()

                    locname = os.path.join(logdir, f'{realfname}.log')
                    os.rename(tmpfname, locname)
                    remlog = f'matches/distrib/logs/{realfname}.log'
                    s3.upload_file(Filename=locname, Bucket=archbucket, Key=remlog)
        if len(taskarns) > 99:
            sts = client.describe_tasks(cluster=clusname, tasks=taskarns[99:199])
            for tsk in sts['failures']:
                if tsk['reason'] == 'MISSING':
                    idx = taskarns.index(tsk['arn'])
                    thisarn=taskarns.pop(idx)
                    thisbuck = bucknames.pop(idx)
                    taskcount -= 1
                    _, thisbuck = os.path.split(thisbuck)
                    try:
                        pref = f'matches/distrib/{thisbuck}/'
                        objects_to_delete = s3.list_objects(Bucket=archbucket, Prefix=pref)
                        delete_keys = {'Objects': []}
                        delete_keys['Objects'] = [{'Key': k} for k in [obj['Key'] for obj in objects_to_delete.get('Contents', [])]]
                        s3.delete_objects(Bucket=archbucket, Delete=delete_keys)
                    except:
                        print('folder already removed')
                    print(f'task {tsk["arn"][51:]} completed already')
            for tsk in sts['tasks']:
                print(f'checking {tsk["taskArn"][51:]}')
                idx = taskarns.index(tsk['taskArn'])
                if tsk['lastStatus'] == 'STOPPED':
                    if tsk['stopCode'] != 'EssentialContainerExited':
                        # retry the task
                        thisjson = createTaskTemplate(rundate, bucknames[idx])
                        response = client.run_task(**thisjson)
                        taskarns[idx] = response['tasks'][0]['taskArn']
                        print('task restarted')
                    else:
                        thisarn=taskarns.pop(idx)
                        thisbuck = bucknames.pop(idx)
                        taskcount -= 1
                        _, thisbuck = os.path.split(thisbuck)
                        try:
                            pref = f'matches/distrib/{thisbuck}/'
                            objects_to_delete = s3.list_objects(Bucket=archbucket, Prefix=pref)
                            delete_keys = {'Objects': []}
                            delete_keys['Objects'] = [{'Key': k} for k in [obj['Key'] for obj in objects_to_delete.get('Contents', [])]]
                            s3.delete_objects(Bucket=archbucket, Delete=delete_keys)
                        except:
                            print('folder already removed')
                        print('task completed')

                        # collect the logs from CloudWatch 
                        realfname=None
                        logdir = os.path.join(datadir, '..', 'logs', 'distrib')
                        os.makedirs(logdir, exist_ok=True)
                        tmpfname = os.path.join(logdir, f'{thisarn[51:]}.log')
                        with open(tmpfname, 'w') as outf:
                            for events in getLogDetails(loggrp, thisarn[51:], contname):
                                for evt in events:
                                    evtdt = datetime.datetime.fromtimestamp(int(evt['timestamp']) / 1000)
                                    msg = evt['message']
                                    outf.write(f'{evtdt} {msg}\n')
                                    if msg[:10] == 'processing':
                                        realfname = msg[11:].strip()

                        locname = os.path.join(logdir, f'{realfname}.log')
                        os.rename(tmpfname, locname)
                        remlog = f'matches/distrib/logs/{realfname}.log'
                        s3.upload_file(Filename=locname, Bucket=archbucket, Key=remlog)
        if taskcount > 0:
            # wait 60s before checking again
            print('sleeping for 60s')
            time.sleep(60.0)
    return


def getMissedLogs(picklefile):
    s3 = boto3.client('s3')
    archbucket = os.getenv('UKMONSHAREDBUCKET', default='s3://ukmda-shared')[5:]
    dumpdata = pickle.load(open(picklefile,'rb'))
    taskarns = dumpdata[1]
    loggrp = '/ecs/trajcont'
    contname = 'trajcont'
    logdir = '/home/ec2-user/prod/logs/distrib'
    for thisarn in taskarns:
        tmpfname = os.path.join(logdir, f'{thisarn[51:]}.log')
        with open(tmpfname, 'w') as outf:
            for events in getLogDetails(loggrp, thisarn[51:], contname):
                for evt in events:
                    evtdt = datetime.datetime.fromtimestamp(int(evt['timestamp']) / 1000)
                    msg = evt['message']
                    outf.write(f'{evtdt} {msg}\n')
                    if msg[:10] == 'processing':
                        realfname = msg[11:].strip()
        locname = os.path.join(logdir, f'{realfname}.log')
        os.rename(tmpfname, locname)
        remlog = f'matches/distrib/logs/{realfname}.log'
        s3.upload_file(Filename=locname, Bucket=archbucket, Key=remlog)


def getLogDetails(loggrp, thisarn, contname, region_name='eu-west-2'):
    """
    Get all event messages of a group and stream from CloudWatch Logs AWS
    """
    client = boto3.client('logs', region_name=region_name)

    # first request
    response = client.get_log_events(
        logGroupName=loggrp,
        logStreamName=f'ecs/{contname}/{thisarn}',
        startFromHead=True)
    yield response['events']

    # second and later
    while True:
        prev_token = response['nextForwardToken']
        response = client.get_log_events(
            logGroupName=loggrp,
            logStreamName=f'ecs/{contname}/{thisarn}',
            nextToken=prev_token)
        # same token then break
        if response['nextForwardToken'] == prev_token:
            break
        yield response['events']


if __name__ == '__main__':
    if len(sys.argv) < 4:
        rundt = datetime.datetime(2022,4,21)
        srcdir = '/home/ec2-user/ukmon-shared/matches/RMSCorrelate/candidates' # hardcoded on calcserver
        buck = os.getenv('UKMONSHAREDBUCKET', default='s3://ukmda-shared')
        targdir = f'{buck}/matches/distrib'
    else:
        rundt = datetime.datetime.strptime(sys.argv[1], '%Y%m%d')
        srcdir = sys.argv[2]
        targdir = sys.argv[3]

    templdir,_ = os.path.split(__file__)
    clusdets = getClusterDetails(templdir)
    print(clusdets)
    distributeCandidates(rundt, srcdir, targdir, clusdets)
    
