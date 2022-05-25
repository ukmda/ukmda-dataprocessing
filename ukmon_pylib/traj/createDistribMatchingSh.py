#
# Python script to create execMatching shell script to be run on the calc engine
#

import os
import sys
import datetime


shkey = os.getenv('UKMONSHAREDKEY')
shbucket = os.getenv('UKMONSHAREDBUCKET')
webkey = os.getenv('WEBSITEKEY')
webbucket = os.getenv('WEBSITEBUCKET')
if len(sys.argv) < 4:
    print('Usage: createDistribMatchingSh day1 day2 outfile')
    exit(1)
matchstart = int(sys.argv[1])
matchend = int(sys.argv[2])
outfname = sys.argv[3]

startdt = datetime.datetime.now() + datetime.timedelta(days=-matchstart)
enddt = datetime.datetime.now() + datetime.timedelta(days=-matchend)
print(startdt, enddt)
startdtstr = startdt.strftime('%Y%m%d-080000')
enddtstr = enddt.strftime('%Y%m%d-080000')
rundatestr = enddt.strftime('%Y%m%d')

yr = enddt.year
ym = enddt.strftime('%Y%m')

execmatchingsh = outfname 
with open(execmatchingsh, 'w') as outf:
    outf.write('#!/bin/bash\n')
    outf.write('source /home/ec2-user/venvs/wmpl/bin/activate\n')
    outf.write('export PYTHONPATH=/home/ec2-user/src/WesternMeteorPyLib:/home/ec2-user/src/ukmon_pylib/ukmon_pylib\n')
    outf.write('cd /home/ec2-user/ukmon-shared/RMSCorrelate\n')
    outf.write('df -h . \n')

    outf.write('echo syncing the data from shared S3\n')
    outf.write(f'source {shkey}\n')
    outf.write(f'time aws s3 sync {shbucket}/matches/RMSCorrelate/ . --exclude "*" --include "UK*" --quiet\n')
    outf.write(f'aws s3 cp {shbucket}/matches/distrib/processed_trajectories.json processed_trajectories.json --quiet\n')

    outf.write('echo starting correlator to update existing matches and create candidates\n')
    outf.write('mkdir -p candidates\n')
    outf.write('rm candidates/*.pickle\n')
    outf.write(f'time python -m wmpl.Trajectory.CorrelateRMS /home/ec2-user/data/RMSCorrelate/ -i 1 -l -r \"({startdtstr},{enddtstr})\"\n')

    outf.write('echo backing up the database to trajdb\n')
    outf.write(f'cp processed_trajectories.json trajdb/processed_trajectories.json.{rundatestr}\n')
    outf.write('Syncing the database back to shared S3\n')
    outf.write(f'source {shkey}\n')
    outf.write(f'aws s3 cp processed_trajectories.json {shbucket}/matches/distrib/processed_trajectories.json --quiet\n')

    outf.write('echo distributing candidates and launching containers\n')
    outf.write('source ~/.ssh/marks-keys\n')
    outf.write(f'time python -m traj.distributeCandidates {rundatestr} ./candidates {shbucket}/matches/distrib\n')

    outf.write('echo syncing any updated trajectories to the website and shared S3\n')
    for d in range(matchend, matchstart+1):
        thisdt=datetime.datetime.now() + datetime.timedelta(days=-d)
        yr = thisdt.year
        mth = thisdt.month
        dy = thisdt.day
        trajloc=f'trajectories/{yr}/{yr}{mth:02d}/{yr}{mth:02d}{dy:02d}'
        targloc=f'reports/{yr}/orbits/{yr}{mth:02d}/{yr}{mth:02d}{dy:02d}'
        outf.write(f'source {webkey}\n')
        outf.write(f'aws s3 sync {trajloc} {webbucket}/{targloc} --quiet\n')
        outf.write(f'source {shkey}\n')
        outf.write(f'aws s3 sync {trajloc} {shbucket}/matches/RMSCorrelate/{trajloc} --exclude "*" --include "*.pickle" --include "*report.txt" --quiet\n')

    outf.write('echo done\n')
