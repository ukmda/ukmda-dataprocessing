#
# Used when running the correlator in 'distributed' mode. 
# Pick up new groups of candidate trajectories and distribute them.
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


def createTaskTemplate(rundate, buckname, spandays=3):
    d1 = (rundate + datetime.timedelta(days = -(spandays-1))).strftime('%Y%m%d')
    d2 = (rundate + datetime.timedelta(days = 1)).strftime('%Y%m%d')

    templdir,_ = os.path.split(__file__)
    templatefile = os.path.join(templdir, 'taskrunner.json')
    clusdetails = os.path.join(templdir, 'clusdetails.txt')
    with open(clusdetails) as inf:
        lis = inf.readlines()
    clusname = lis[0].strip()
    secgrp = lis[1].strip()
    subnet = lis[2].strip()
    exrolearn = lis[3].strip()

    targdir, buckname = os.path.split(buckname)
    with open(templatefile) as inf:
        templ = json.load(inf)
        templ['cluster'] = clusname
        templ['networkConfiguration']['awsvpcConfiguration']['subnets'] = [f'{subnet}']
        templ['networkConfiguration']['awsvpcConfiguration']['securityGroups'] = [f'{secgrp}']
        templ['overrides']['executionRoleArn'] = exrolearn
        templ['overrides']['containerOverrides'][0]['command'] = [f'{buckname}', f'{d1}', f'{d2}']

    return templ, clusname


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
    buckroot = os.path.join(targdir, rundate.strftime('%Y%m%d_'))
    taskarns = [None] * numbucks
    jsontempls = [None] * numbucks
    for i in range(0, numbucks):
        buckname = buckroot + f'{i:02d}'
        if os.path.isdir(buckname):
            shutil.rmtree(buckname)
        os.makedirs(buckname, exist_ok=True)
        bucklist = flist[i::numbucks]
        with open(os.path.join(buckname, f'files_{i:02d}.txt'),'w') as outf:
            for fli in bucklist:
                src = os.path.join(srcdir, fli)
                dst = os.path.join(buckname, fli)
                shutil.copy2(src, dst)
                outf.write(f'{fli}\n')

        jsontempl, clusname = createTaskTemplate(rundate, buckname)
        response = client.run_task(**jsontempl)
        if len(response['tasks']) == 0:
            print('task did not start')
        else:
            taskarn = response['tasks'][0]['taskArn']
            taskarns[i] = taskarn
            jsontempls[i] = jsontempls
            print(taskarn[51:])
    
    status = client.describe_clusters(clusters=[clusname])
    if len(status['clusters']) ==0:
        print('cluster not running!')
    else:
        rtc = status['clusters'][0]['runningTasksCount']
        ptc = status['clusters'][0]['pendingTasksCount']
        print(f'{rtc} running, {ptc} pending')

    # need to keep list of task ARNs and then check if they started properly.
    # Look for "lastStatus": "STOPPED",
    # if not "stopCode": "EssentialContainerExited"
    # then launch it again

    # wait 30s before testing whether everything is running
    taskcount = len(taskarns)
    while taskcount > 0:
        time.sleep(60.0)
        sts = client.describe_tasks(cluster=clusname, tasks=taskarns)
        for tsk in sts['tasks']:
            print(f'checking {tsk["taskArn"]}')
            idx = taskarns.index(tsk['taskArn'])
            if tsk['lastStatus'] == 'STOPPED':
                if tsk['stopCode'] != 'EssentialContainerExited':
                    # retry the task
                    thisjson = jsontempls[idx]
                    response = client.run_task(**thisjson)
                    taskarns[idx] = response['tasks'][0]['taskArn']
                    taskcount += 1
                    print(f'task {idx} restarted')
                else:
                    jsontempls.pop(idx)
                    taskarns.pop(idx)
                    taskcount -= 1
                    print(f'task {idx} completed')


if __name__ == '__main__':
    if len(sys.argv) < 4:
        rundt = datetime.datetime(2022,4,21)
        srcdir = 'f:/videos/meteorcam/ukmondata/disttest/RMSCorrelate/candidates'
        targdir = 'f:/videos/meteorcam/ukmondata/disttest/RMSCorrelate/distribs'
    else:
        rundt = datetime.datetime.strptime(sys.argv[1], '%Y%m%d')
        matchdir = os.getenv('MATCHDIR')
        srcdir = os.path.join(matchdir, 'distrib', 'candidates')
        targdir = os.path.join(matchdir, 'distrib')
    distributeCandidates(rundt, srcdir, targdir)
