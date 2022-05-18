#
# Used when running the correlator in 'distributed' mode. 
# Pick up new groups of candidate trajectories and distribute them, then
# wait for completion and unpack the resultss. 
#

import json
import os
import sys
import shutil
import glob
import math
import datetime
import boto3
import time
import pickle
import tarfile

# imports are required to load the picklefiles
from wmpl.Trajectory.CorrelateRMS import TrajectoryReduced, DatabaseJSON # noqa: F401
from wmpl.Trajectory.CorrelateRMS import MeteorObsRMS, PlateparDummy, MeteorPointRMS # noqa: F401


class dummyMeteorObsRMS(object):
    def __init__(self, station_code, id):
        self.station_code = station_code
        self.id = id


def getClusterDetails(templdir):
    clusdetails = os.path.join(templdir, 'clusdetails.txt')
    with open(clusdetails) as inf:
        lis = inf.readlines()
    clusname = lis[0].strip()
    secgrp = lis[1].strip()
    subnet = lis[2].strip()
    exrolearn = lis[3].strip()
    loggrp = lis[4].strip()
    contname = lis[5].strip()
    return clusname, secgrp, subnet, exrolearn, loggrp, contname


def createTaskTemplate(rundate, buckname, spandays=3):
    d1 = (rundate + datetime.timedelta(days = -(spandays-1))).strftime('%Y%m%d')
    d2 = (rundate + datetime.timedelta(days = 1)).strftime('%Y%m%d')

    templdir,_ = os.path.split(__file__)
    templatefile = os.path.join(templdir, 'taskrunner.json')
    clusname, secgrp, subnet, exrolearn, _ = getClusterDetails(templdir)

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
    dbg = os.getenv('DEBUG')
    if dbg is None:
        return False
    elif dbg == '1':
        return True
    else:
        return False


def distributeCandidates(rundate, srcdir, targdir, maxcount=20):

    client = boto3.client('ecs', region_name='eu-west-2')
    print(f'Reading from {srcdir}')
    # obtain a list of picklefiles and sort by name
    flist = glob.glob1(srcdir, '*.pickle')
    flist.sort()

    # work out how many buckets i need
    numcands = len(flist)
    numbucks = int(math.ceil(numcands/maxcount))

    # create buckets
    buckroot = os.path.join(targdir, rundate.strftime('%Y%m%d'))
    taskarns = [None] * numbucks
    jsontempls = [None] * numbucks
    bucknames = [None] * numbucks

    isDbg = getDebugStatus()

    for i in range(0, numbucks):
        bucknames[i] = buckroot + f'_{i:02d}'
        if os.path.isdir(bucknames[i]):
            shutil.rmtree(bucknames[i])
        os.makedirs(bucknames[i], exist_ok=True)
        filelist = flist[i::numbucks]
        with open(os.path.join(bucknames[i], f'files_{i:02d}.txt'),'w') as outf:
            for fli in filelist:
                src = os.path.join(srcdir, fli)
                dst = os.path.join(bucknames[i], fli)
                shutil.copy2(src, dst)
                outf.write(f'{fli}\n')

        taskjson = createTaskTemplate(rundate, bucknames[i])

        response = client.run_task(**taskjson)
        while len(response['tasks']) == 0:
            response = client.run_task(**taskjson)

        taskarn = response['tasks'][0]['taskArn']
        taskarns[i] = taskarn
        jsontempls[i] = taskjson
        print(taskarn[51:])
        if isDbg is True and i == 3:
            break
    
    # may not be 20 tasks
    taskarns = [e for e in taskarns if e is not None]
    bucknames = [e for e in bucknames if e is not None]
    jsontempls = [e for e in jsontempls if e is not None]

    clusname = jsontempls[0]['cluster']
    dmpdata = [bucknames, taskarns, clusname]
    pickle.dump(dmpdata, open(buckroot + '.pickle','wb'))

    status = client.describe_clusters(clusters=[clusname])
    if len(status['clusters']) ==0:
        print('cluster not running!')
    else:
        rtc = status['clusters'][0]['runningTasksCount']
        ptc = status['clusters'][0]['pendingTasksCount']
        print(f'{rtc} running, {ptc} pending')

    return


def monitorProgress(rundate, targdir):
    client = boto3.client('ecs', region_name='eu-west-2')

    picklefile = os.path.join(targdir, rundate.strftime('%Y%m%d') + '.pickle')
    dumpdata = pickle.load(open(picklefile,'rb'))
    bucknames = dumpdata[0]
    taskarns = dumpdata[1]
    clusname = dumpdata[2]

    templdir,_ = os.path.split(__file__)
    _, _, _, _, loggrp, contname = getClusterDetails(templdir)
    # need to keep list of task ARNs and then check if they started properly.
    # Look for "lastStatus": "STOPPED",
    # if not "stopCode": "EssentialContainerExited"
    # then launch it again

    # wait 60s before testing whether everything is running
    taskcount = len(taskarns)
    while taskcount > 0:
        time.sleep(60.0)
        sts = client.describe_tasks(cluster=clusname, tasks=taskarns)
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
                    bucknames.pop(idx)
                    taskcount -= 1
                    print('task completed')
                    os.makedirs(os.path.join(targdir, 'logs'), exist_ok=True)
                    with open(os.path.join(targdir, 'logs', f'{thisarn[51:]}.log'), 'w') as outf:
                        for events in getLogDetails(loggrp, thisarn[51:], contname):
                            for evt in events:
                                evtdt = datetime.datetime.fromtimestamp(int(evt['timestamp']) / 1000)
                                msg = evt['message']
                                outf.write(f'{evtdt} {msg}\n')
    return


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


def unpackResults(targdir, buckname, remove=False):
    outdir = os.path.join(targdir, 'solved')
    os.makedirs(outdir, exist_ok=True)
    with tarfile.open(buckname + '.tgz', 'r:gz') as tar:
        tar.extractall(path=outdir)
    if remove is True:
        os.remove(buckname + '.tgz')
        shutil.rmtree(buckname)
    return 


def mergeDatabases(targdir, fldrname, masterfile):
    newdb = os.path.join(targdir, fldrname + '.json')
    mergedb = DatabaseJSON(newdb)
    mastdb = DatabaseJSON(masterfile)
    mastdb.db_file_path = masterfile
    # merge successful trajectories
    for traj in mergedb.trajectories:
        traj_obj = TrajectoryReduced(traj, json_dict = mergedb.trajectories[traj].__dict__)
        traj_file_path = traj_obj.traj_file_path
        traj_file_path = '/home/ec2-user/data/RMSCorrelate/' + traj_file_path[traj_file_path.find('trajectories'):]
        traj_obj.traj_file_path = traj_file_path
        mastdb.addTrajectory(traj_file_path, traj_obj=traj_obj)
    # merge failed trajectories 
    for traj in mergedb.failed_trajectories:
        traj_obj = TrajectoryReduced(traj, json_dict = mergedb.failed_trajectories[traj].__dict__)
        traj_file_path = traj_obj.traj_file_path
        traj_file_path = '/home/ec2-user/data/RMSCorrelate/' + traj_file_path[traj_file_path.find('trajectories'):]
        traj_obj.traj_file_path = traj_file_path
        mastdb.addTrajectory(traj_file_path, traj_obj=traj_obj, failed=True)
    # merge paired obs data
    for p in mergedb.paired_obs:
        ids = mergedb.paired_obs[p]
        for id in ids:
            met_obs = dummyMeteorObsRMS(p, id)
            mastdb.addPairedObservation(met_obs)
    # save the master DB again
    mastdb.save()
    return


if __name__ == '__main__':
    if len(sys.argv) < 4:
        rundt = datetime.datetime(2022,4,21)
    else:
        rundt = datetime.datetime.strptime(sys.argv[1], '%Y%m%d')

    matchdir = os.getenv('MATCHDIR')
    srcdir = os.path.join(matchdir, 'distrib', 'candidates')
    targdir = os.path.join(matchdir, 'distrib')

    distributeCandidates(rundt, srcdir, targdir)

    monitorProgress(rundt, targdir)
