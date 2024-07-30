# Copyright (C) 2018-2023 Mark McIntyre
#
# Python script to create execMatching shell script to be run on the calc engine
#

import os
import sys
import datetime
import json


# read the task template to determine the paths to write any data to
#
def getTrajsolverPaths():
    templdir,_ = os.path.split(__file__)
    with open(os.path.join(templdir, 'taskrunner.json'), 'r') as inf:
        taskdets = json.load(inf)
    taskenv = taskdets['overrides']['containerOverrides'][0]['environment']
    srcpath = [x for x in taskenv if x['name']=='SRCPATH'][0]['value'] # path from which trajsolver will consume candidates
    outpath = [x for x in taskenv if x['name']=='OUTPATH'][0]['value'] # path to which trajsolver will publish trajectories
    webpath = [x for x in taskenv if x['name']=='WEBPATH'][0]['value'] # web loc to which trajsolver will publish trajectories

    return srcpath, outpath, webpath


# make sure the local trajectories folder is synced with the master copy
#
def refreshTrajectories(outf, matchstart, matchend, trajpath):
    #thiskey = getKeyForBucket(trajpath)
    outf.write('logger -s -t execdistrib syncing any updated trajectories from shared S3\n')
    #outf.write(f'source {thiskey}\n')
    for d in range(matchend, matchstart+1):
        thisdt=datetime.datetime.now() + datetime.timedelta(days=-d)
        yr = thisdt.year
        mth = thisdt.month
        dy = thisdt.day
        trajloc=f'trajectories/{yr}/{yr}{mth:02d}/{yr}{mth:02d}{dy:02d}'
        outf.write(f'aws s3 sync {trajpath}/{trajloc} {trajloc} --exclude "*" --include "*.pickle" \n')
    return 


# make sure the master copy is updated with any new locally updated trajectories
#
def pushUpdatedTrajectoriesShared(outf, matchstart, matchend, targpath):
    # thiskey = getKeyForBucket(targpath)
    outf.write('logger -s -t execdistrib syncing any updated trajectories to shared S3\n')
    for d in range(matchend, matchstart+1):
        thisdt=datetime.datetime.now() + datetime.timedelta(days=-d)
        yr = thisdt.year
        ym=thisdt.strftime('%Y%m')
        ymd=thisdt.strftime('%Y%m%d')
        trajloc=f'trajectories/{yr}/{ym}/{ymd}'
        outf.write(f'if [ -d {trajloc} ] ; then \n')
        outf.write(f'aws s3 sync {trajloc} {targpath}/matches/RMSCorrelate/{trajloc} --exclude "*" --include "*.pickle" --include "*report.txt" --quiet\n')
        outf.write(f'aws s3 sync {trajloc}/plots {targpath}/matches/RMSCorrelate/{trajloc}/plots --quiet\n')
        outf.write('fi\n')
    outf.write(f'aws s3 sync trajectories/{yr}/plots {targpath}/matches/RMSCorrelate/trajectories/{yr}/plots --quiet\n')
    outf.write(f'aws s3 sync trajectories/{yr}/{ym}/plots {targpath}/matches/RMSCorrelate/trajectories/{yr}/{ym}/plots --quiet\n')
    return 


# make sure the master copy is updated with any new locally updated trajectories
#
def pushUpdatedTrajectoriesWeb(outf, matchstart, matchend, webpath):
    # thiskey = getKeyForBucket(webpath)
    outf.write('logger -s -t execdistrib syncing any updated trajectories to the website\n')
    for d in range(matchend, matchstart+1):
        thisdt=datetime.datetime.now() + datetime.timedelta(days=-d)
        yr = thisdt.year
        ym=thisdt.strftime('%Y%m')
        ymd=thisdt.strftime('%Y%m%d')
        trajloc=f'trajectories/{yr}/{ym}/{ymd}'
        targloc=f'reports/{yr}/orbits/{ym}/{ymd}'
        outf.write(f'if [ -d {trajloc} ] ; then \n')
        outf.write(f'aws s3 sync {trajloc} {webpath}/{targloc} --quiet\n')
        outf.write('fi\n')
        outf.write(f'aws s3 sync {trajloc}/plots {webpath}/{targloc}/plots --quiet\n')
    outf.write(f'aws s3 sync trajectories/{yr}/plots {webpath}/reports/{yr}/orbits/plots --quiet\n')
    outf.write(f'aws s3 sync trajectories/{yr}/{ym}/plots {webpath}/reports/{yr}/orbits/{ym}/plots --quiet\n')
    return 


def createDensityPlots(outf, calcdir, enddt):
    outf.write('logger -s -t execdistrib creating density plots\n')
    yr = enddt.year
    ym = enddt.strftime('%Y%m')

    outf.write(f'mkdir -p {calcdir}/trajectories/{yr}/plots\n')
    outf.write(f'mkdir -p {calcdir}/trajectories/{yr}/{ym}/plots\n')

    outf.write(f'python -m wmpl.Trajectory.AggregateAndPlot {calcdir}/trajectories/{yr} -p -s 30 -o {calcdir}/trajectories/{yr}/plots\n')
    outf.write(f'python -m wmpl.Trajectory.AggregateAndPlot {calcdir}/trajectories/{yr}/{ym} -p -s 30 -o {calcdir}/trajectories/{yr}/{ym}/plots\n')

    outf.write(f'rm -f {calcdir}/trajectories/{yr}/plots/world_map.png\n')
    outf.write(f'rm -f {calcdir}/trajectories/{yr}/{ym}/plots/world_map.png\n')

    for i in range(5):
        thisdt = enddt + datetime.timedelta(days=-i)
        yr = thisdt.year
        ym = thisdt.strftime('%Y%m')
        ymd = thisdt.strftime('%Y%m%d')
        outf.write(f'mkdir -p {calcdir}/trajectories/{yr}/{ym}/{ymd}/plots\n')
        outf.write(f'python -m wmpl.Trajectory.AggregateAndPlot {calcdir}/trajectories/{yr}/{ym}/{ymd} -p -s 30 -o {calcdir}/trajectories/{yr}/{ym}/{ymd}/plots\n')
        outf.write(f'rm -f {calcdir}/trajectories/{yr}/{ym}/{ymd}/plots/world_map.png\n')
    return


def SyncRawData(outf, matchstart, matchend, shbucket, calcdir):
    # camera data - no need to replicate it for an historical date
    outf.write('logger -s -t execdistrib starting raw data sync\n')
    outf.write(f'targdirs=$(aws s3 ls {shbucket}/matches/RMSCorrelate/ | egrep -v "traj|daily|test|plot|proce"|grep PRE | awk \'{{print $2}}\')\n') 
    outf.write('for td in $targdirs ; do\n')
    outf.write('logger -s -t execdistrib processing $td\n')
    for d in range(matchend+1, matchstart+2):
        thisdt=datetime.datetime.now() + datetime.timedelta(days=-d)
        trgdy=thisdt.strftime('%Y%m%d')
        outf.write(f'	aws s3 sync {shbucket}/matches/RMSCorrelate/$td {calcdir}/$td --exclude "*" --include "${{td:0:6}}_{trgdy}*" --quiet\n')
    outf.write('done\n')
    return


def createExecConsolSh(matchstart, matchend, execconsolsh):
    shbucket = os.getenv('UKMONSHAREDBUCKET', default='s3://ukmda-shared')
    webbucket = os.getenv('WEBSITEBUCKET', default='s3://ukmda-website')
    calcdir = '/home/ec2-user/ukmon-shared/matches/RMSCorrelate' # hardcoded!
    _, outpath, _ = getTrajsolverPaths()
    enddt = datetime.datetime.now() + datetime.timedelta(days=-matchend)

    with open(execconsolsh, 'w') as outf:
        outf.write('#!/bin/bash\n')
        outf.write('source /home/ec2-user/venvs/wmpl/bin/activate\n')
        outf.write('export PYTHONPATH=/home/ec2-user/src/WesternMeteorPyLib:/home/ec2-user/src/ukmon_pylib\n')
        outf.write('export AWS_PROFILE=ukmonshared\n')
        outf.write(f'cd {calcdir}\n')
        outf.write('logger -s -t execConsol start\n')

        outf.write('python -m traj.consolidateDistTraj ~/data/distrib/ ~/data/distrib/processed_trajectories.json\n')

        refreshTrajectories(outf, matchstart, matchend, outpath)
        createDensityPlots(outf, calcdir, enddt)
        pushUpdatedTrajectoriesShared(outf, matchstart, matchend, shbucket)
        pushUpdatedTrajectoriesWeb(outf, matchstart, matchend, webbucket)
        outf.write('unset AWS_PROFILE\n')
        outf.write('logger -s -t execConsol done\n')
    return


def createDistribMatchingSh(matchstart, matchend, execmatchingsh):
    shbucket = os.getenv('UKMONSHAREDBUCKET', default='s3://ukmda-shared')
    webbucket = os.getenv('WEBSITEBUCKET', default='s3://ukmda-website')

    startdt = datetime.datetime.now() + datetime.timedelta(days=-matchstart)
    enddt = datetime.datetime.now() + datetime.timedelta(days=-matchend)
    print(startdt, enddt)
    startdtstr = startdt.strftime('%Y%m%d-080000')
    enddtstr = enddt.strftime('%Y%m%d-080000')
    rundatestr = enddt.strftime('%Y%m%d')

    calcdir = '/home/ec2-user/ukmon-shared/matches/RMSCorrelate' # hardcoded!

    srcpath, outpath, webpath = getTrajsolverPaths()

    with open(execmatchingsh, 'w') as outf:
        outf.write('#!/bin/bash\n')
        outf.write('source /home/ec2-user/venvs/wmpl/bin/activate\n')
        outf.write('export PYTHONPATH=/home/ec2-user/src/WesternMeteorPyLib:/home/ec2-user/src/ukmon_pylib\n')
        outf.write('export AWS_PROFILE=ukmonshared\n')
        outf.write(f'cd {calcdir}\n')
        outf.write('df -h . \n')

        # fetch anything thats new from S3
        refreshTrajectories(outf, matchstart, matchend, outpath)

        outf.write('logger -s -t execdistrib syncing the raw data from shared S3\n')
        outf.write(f'aws s3 cp {srcpath}/processed_trajectories.json {calcdir}/processed_trajectories.json --quiet\n')
        outf.write(f'ls -ltr {calcdir}/*.json\n')

        SyncRawData(outf, matchstart, matchend, shbucket, calcdir)
        
        outf.write('logger -s -t execdistrib starting correlator to update existing matches and create candidates\n')
        outf.write(f'mkdir -p {calcdir}/candidates\n')
        outf.write(f'rm {calcdir}/candidates/*.pickle >/dev/null 2>&1\n')
        outf.write(f'time python -m wmpl.Trajectory.CorrelateRMS {calcdir} -i 1 -l -r \"({startdtstr},{enddtstr})\"\n')

        outf.write('logger -s -t execdistrib backing up the database to trajdb\n')
        outf.write(f'cp {calcdir}/processed_trajectories.json {calcdir}/trajdb/processed_trajectories.json.{rundatestr}\n')

        outf.write('logger -s -t execdistrib Syncing the database back to shared S3\n')
        outf.write(f'if [ -s {calcdir}/processed_trajectories.json ] ; then\n')
        outf.write(f'aws s3 cp {calcdir}/processed_trajectories.json {srcpath}/processed_trajectories.json --quiet\n')
        outf.write('else echo "bad database file" ; fi \n')

        outf.write('logger -s -t execdistrib distributing candidates and launching containers\n')
        outf.write(f'time python -m traj.distributeCandidates {rundatestr} {calcdir}/candidates {srcpath}\n')

        # do this again to fetch todays results
        refreshTrajectories(outf, matchstart, matchend, outpath)
        
        #createDensityPlots(outf, calcdir, enddt)

        pushUpdatedTrajectoriesShared(outf, matchstart, matchend, shbucket)
        pushUpdatedTrajectoriesWeb(outf, matchstart, matchend, webbucket)

        outf.write('unset AWS_PROFILE\n')
        outf.write('logger -s -t execdistrib done\n')


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: createDistribMatchingSh day1 day2 outfile')
        exit(1)
    matchstart = int(sys.argv[1])
    matchend = int(sys.argv[2])
    outfname = sys.argv[3]

    createDistribMatchingSh(matchstart, matchend, outfname)
