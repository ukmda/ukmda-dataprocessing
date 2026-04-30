# Copyright (C) 2018-2023 Mark McIntyre
#
# Python script to create execMatching shell script to be run on the calc engine
#

import os
import sys
import datetime

from traj.distributeCandidates import getTrajsolverPaths


# make sure the local trajectories folder is synced with the master copy
#
def refreshTrajectories(outf, matchstart, matchend, trajpath):
    for d in range(matchend, matchstart+1):
        thisdt=datetime.datetime.now() + datetime.timedelta(days=-d)
        yr = thisdt.year
        mth = thisdt.month
        dy = thisdt.day
        trajloc=f'trajectories/{yr}/{yr}{mth:02d}/{yr}{mth:02d}{dy:02d}'
        outf.write(f'aws s3 sync {trajpath}/{trajloc} {trajloc} --exclude "*" --include "*.pickle" --quiet\n')
    return 


# make sure the shared bucket is updated with any new locally updated trajectories
#
def pushUpdatedTrajectoriesShared(outf, matchstart, matchend, targpath):
    for d in range(matchend, matchstart+1):
        thisdt=datetime.datetime.now() + datetime.timedelta(days=-d)
        yr = thisdt.year
        ym=thisdt.strftime('%Y%m')
        ymd=thisdt.strftime('%Y%m%d')
        trajloc=f'trajectories/{yr}/{ym}/{ymd}'
        outf.write(f'if [ -d {trajloc} ] ; then \n')
        outf.write(f'aws s3 sync {trajloc} {targpath}/{trajloc} --exclude "*" --include "*.pickle" --include "*report.txt" --quiet\n')
        outf.write(f'if [ -d {trajloc}/plots ] ; then \n')
        outf.write(f'aws s3 sync {trajloc}/plots {targpath}/{trajloc}/plots --quiet\n')
        outf.write('fi\n')
        outf.write('fi\n')
    outf.write(f'aws s3 sync trajectories/{yr}/plots {targpath}/trajectories/{yr}/plots --quiet\n')
    outf.write(f'aws s3 sync trajectories/{yr}/{ym}/plots {targpath}/trajectories/{yr}/{ym}/plots --quiet\n')
    return 


# make sure the website is updated with any new locally updated trajectories
#
def pushUpdatedTrajectoriesWeb(outf, matchstart, matchend, webpath):
    for d in range(matchend, matchstart+1):
        thisdt=datetime.datetime.now() + datetime.timedelta(days=-d)
        yr = thisdt.year
        ym=thisdt.strftime('%Y%m')
        ymd=thisdt.strftime('%Y%m%d')
        trajloc=f'trajectories/{yr}/{ym}/{ymd}'
        targloc=f'{yr}/orbits/{ym}/{ymd}'
        outf.write(f'if [ -d {trajloc} ] ; then \n')
        outf.write(f'aws s3 sync {trajloc} {webpath}/{targloc} --quiet\n')
        outf.write('fi\n')
        outf.write(f'aws s3 sync {trajloc}/plots {webpath}/{targloc}/plots --quiet\n')
    outf.write(f'aws s3 sync trajectories/{yr}/plots {webpath}/{yr}/orbits/plots --quiet\n')
    outf.write(f'aws s3 sync trajectories/{yr}/{ym}/plots {webpath}/{yr}/orbits/{ym}/plots --quiet\n')
    return 


# Create the density plots showing meteor showers
#
def createDensityPlots(outf, calcdir, enddt, includeyear=True):
    yr = enddt.year
    ym = enddt.strftime('%Y%m')

    outf.write(f'mkdir -p {calcdir}/trajectories/{yr}/plots\n')
    outf.write(f'mkdir -p {calcdir}/trajectories/{yr}/{ym}/plots\n')

    if includeyear:
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


# Sync the raw camera data from shared storage to the local disk
#
def SyncRawData(outf, matchstart, matchend, shbucket):
    # camera data - no need to replicate it for an historical date
    outf.write(f'targdirs=$(aws s3 ls {shbucket}/ | egrep -v "traj|daily|test|plot|proce|dbs"|grep PRE | awk \'{{print $2}}\')\n') 
    outf.write('for td in $targdirs ; do\n')
    for d in range(matchend+1, matchstart+2):
        thisdt=datetime.datetime.now() + datetime.timedelta(days=-d)
        trgdy=thisdt.strftime('%Y%m%d')
        outf.write(f'	aws s3 sync {shbucket}/$td ./$td --exclude "*" --include "${{td:0:6}}_{trgdy}*" --quiet\n')
    outf.write('done\n')
    return


#
# Get a list of images that are used by the solutions
#

def gatherUsedImageList(outf, matchstart, matchend, shbucket):
    for d in range(matchend, matchstart+1):
        thisdt=datetime.datetime.now() + datetime.timedelta(days=-d)
        yr = thisdt.year
        mth = thisdt.month
        dy = thisdt.day
        trajloc = f'trajectories/{yr}/{yr}{mth:02d}/{yr}{mth:02d}{dy:02d}'
        out_dir = '~/data/distrib'
        outf.write(f'python -c "from traj.pickleAnalyser import getAllImages;getAllImages(\'{trajloc}\', \'{out_dir}\');"\n')
    outf.write(f'aws s3 sync {out_dir}  {shbucket}/matches/consumed/ --exclude "*" --include "consumed_*.txt" --quiet\n')
    outf.write(f'rm {out_dir}/consumed_*.txt\n')
    return 


#
# Create the bash script that consolidates the generated data and makes sure the website and shared area are updated 

def createExecConsolSh(matchstart, matchend, execconsolsh, istest=''):

    istest = True if istest.lower()=='true' else False
    print(f'istest is {istest}')

    srcpath, shbucket, webbucket = getTrajsolverPaths(istest=istest)
    csuser = os.getenv('SERVERUSERID', default='ec2-user')
    calcdir = f'/home/{csuser}/ukmon-shared/matches/RMSCorrelate' 

    enddt = datetime.datetime.now() + datetime.timedelta(days=-matchend)
    includeyear = False
    if enddt.day == 30:
        includeyear = True

    with open(execconsolsh, 'w') as outf:
        outf.write('#!/bin/bash\n')
        outf.write(f'source /home/{csuser}/venvs/wmpl/bin/activate\n')
        outf.write(f'export PYTHONPATH=/home/{csuser}/src/WesternMeteorPyLib:/home/{csuser}/src/ukmon_pylib\n')

        outf.write(f'cd {calcdir}\n')
        outf.write('logger -s -t execConsol start\n')
        outf.write(f'aws s3 sync {srcpath}/ ~/data/distrib/canddbs/ --exclude "*" --include "*.db" --exclude "dbs/*" --quiet\n')

        outf.write(f'python -m traj.consolidateDistTraj ~/data/distrib/canddbs/ {calcdir}/dbs/\n')

        outf.write(f'aws s3 sync {calcdir}/dbs/ {srcpath}/dbs/ --exclude "*" --include "*.db" --quiet\n')

        outf.write('logger -s -t execConsol syncing any updated trajectories from shared S3\n')
        refreshTrajectories(outf, matchstart, matchend, shbucket)
        outf.write('logger -s -t execConsol creating density plots\n')
        createDensityPlots(outf, calcdir, enddt, includeyear)
        outf.write('logger -s -t execConsol pushing data back to S3\n')
        pushUpdatedTrajectoriesShared(outf, matchstart, matchend, shbucket)
        pushUpdatedTrajectoriesWeb(outf, matchstart, matchend, webbucket)
        outf.write('logger -s -t execConsol getting the image list\n')
        gatherUsedImageList(outf, matchstart, matchend, shbucket)

        outf.write('logger -s -t execConsol done\n')
    return

#
# Create a bash script to replot the density charts if needed


def createExecReplotSh(matchstart, matchend, execconsolsh, istest=''):

    istest = True if istest.lower()=='true' else False

    shbucket = os.getenv('UKMONSHAREDBUCKET', default='s3://ukmda-shared')
    csuser = os.getenv('SERVERUSERID', default='ec2-user')
    calcdir = f'/home/{csuser}/ukmon-shared/matches/RMSCorrelate' 
    _, outpath, _ = getTrajsolverPaths(istest=istest)

    enddt = datetime.datetime.now() + datetime.timedelta(days=-matchend)
    with open(execconsolsh, 'w') as outf:
        outf.write('#!/bin/bash\n')
        outf.write(f'source /home/{csuser}/venvs/wmpl/bin/activate\n')
        outf.write(f'export PYTHONPATH=/home/{csuser}/src/WesternMeteorPyLib:/home/{csuser}/src/ukmon_pylib\n')
        outf.write(f'cd {calcdir}\n')
        outf.write('logger -s -t execReplot start\n')
        refreshTrajectories(outf, matchstart, matchend, outpath)
        createDensityPlots(outf, calcdir, enddt, False)
        gatherUsedImageList(outf, matchstart, matchend, shbucket)
        outf.write('logger -s -t execReplot done\n')
    return


def createDistribMatchingSh(matchstart, matchend, execmatchingsh, istest=False):
    csuser = os.getenv('SERVERUSERID', default='ec2-user')

    startdt = datetime.datetime.now() + datetime.timedelta(days=-matchstart)
    enddt = datetime.datetime.now() + datetime.timedelta(days=-matchend)
    print(startdt, enddt)
    startdtstr = startdt.strftime('%Y%m%d-080000')
    enddtstr = enddt.strftime('%Y%m%d-080000')
    rundatestr = enddt.strftime('%Y%m%d')

    calcdir = f'/home/{csuser}/ukmon-shared/matches/RMSCorrelate' 

    _, outpath, webpath = getTrajsolverPaths(istest=istest)

    srcpath = os.getenv('UKMONSHAREDBUCKET') + '/matches/RMSCorrelate'

    with open(execmatchingsh, 'w') as outf:
        outf.write('#!/bin/bash\n')
        outf.write(f'source /home/{csuser}/venvs/wmpl/bin/activate\n')
        outf.write(f'export PYTHONPATH=/home/{csuser}/src/WesternMeteorPyLib:/home/{csuser}/src/ukmon_pylib\n')
        outf.write(f'cd {calcdir}\n')
        outf.write('df -h . \n')

        # fetch anything thats new from S3
        outf.write('logger -s -t execdistrib syncing latest trajectories from shared S3\n')
        # in test, we seeded the test area with prod trajectories in April 2026
        refreshTrajectories(outf, matchstart, matchend, outpath)

        outf.write('logger -s -t execdistrib syncing the raw data from shared S3\n')
        SyncRawData(outf, matchstart, matchend, srcpath)
        
        outf.write('logger -s -t execdistrib starting correlator to update existing matches and create candidates\n')
        outf.write('mkdir -p ./candidates/processed\n')
        outf.write('rm ./candidates/*.pickle >/dev/null 2>&1\n')
        outf.write(f'time python -m wmpl.Trajectory.CorrelateRMS . --dbdir ./dbs --logdir ./logs --mcmode 4 -l -r \"({startdtstr},{enddtstr})\"\n')

        # backup the raw candidates in case i need to reprocess some by hand
        outf.write(f'tar czf ./candidates/processed/{rundatestr}.tgz ./candidates/*.pickle\n')
        outf.write('find ./candidates/processed/ -name "*.tgz" -mtime +14 -exec rm -f ' + '{} \\;\n')
        outf.write('find ./logs/ -mtime +28 -exec rm -f ' + '{} \\;\n')

        outf.write('logger -s -t execdistrib backing up the database to trajdb\n')
        outf.write(f'tar cvzf ./trajdb/databases_{rundatestr}.tgz dbs/observations.db dbs/trajectories.db dbs/candidates.db\n')
        outf.write('find ./trajdb/ -name "*" -mtime +14 -exec rm -f ' + '{} \\;\n')

        outf.write('logger -s -t execdistrib distributing candidates and launching containers\n')
        outf.write(f'time python -m traj.distributeCandidates {rundatestr} ./candidates {istest}\n')

        # do this again to fetch todays results
        outf.write('logger -s -t execdistrib refetch latest trajectories\n')
        refreshTrajectories(outf, matchstart, matchend, outpath)
    
        outf.write('logger -s -t execdistrib and sync back to S3 as well\n')
        pushUpdatedTrajectoriesShared(outf, matchstart, matchend, outpath)
        pushUpdatedTrajectoriesWeb(outf, matchstart, matchend, webpath)

        outf.write('logger -s -t execdistrib done\n')


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: createDistribMatchingSh day1 day2 outfile optional_istest')
        exit(1)
    matchstart = int(sys.argv[1])
    matchend = int(sys.argv[2])
    outfname = sys.argv[3]
    if len(sys.argv) > 4:
        istest = True if sys.argv[4].lower()=='true' else False

    createDistribMatchingSh(matchstart, matchend, outfname, istest)
