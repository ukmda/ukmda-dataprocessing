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
    print('Usage: createExecMatchingSh day1 day2 outfile')
    exit(1)
matchstart = int(sys.argv[1])
matchend = int(sys.argv[2])
outfname = sys.argv[3]

startdt = datetime.datetime.now() + datetime.timedelta(days=-matchstart)
enddt = datetime.datetime.now() + datetime.timedelta(days=-matchend)
print(startdt, enddt)
startdtstr = startdt.strftime('%Y%m%d-080000')
enddtstr = enddt.strftime('%Y%m%d-080000')

yr = enddt.year
ym = enddt.strftime('%Y%m')

#tmpdir = os.getenv('TMP')
#if tmpdir is None:
#    tmpdir = '/tmp'
execmatchingsh = outfname # os.path.join(tmpdir, outfname)
with open(execmatchingsh, 'w') as outf:
    outf.write('#!/bin/bash\n')
    outf.write('source /home/ec2-user/venvs/wmpl/bin/activate\n')
    outf.write('export PYTHONPATH=/home/ec2-user/src/WesternMeteorPyLib/\n')
    outf.write('cd /home/ec2-user/data/RMSCorrelate\n')
    outf.write('df -h . \n')
    outf.write(f'source {shkey}\n')
    outf.write(f'aws s3 sync {shbucket}/matches/RMSCorrelate/ . --exclude "*" --include "UK*" --quiet\n')
    outf.write('cd /home/ec2-user/src/WesternMeteorPyLib/\n')
    outf.write('logger -s -t runMatching \"starting correlator\"\n')
    outf.write(f'time python -m wmpl.Trajectory.CorrelateRMS /home/ec2-user/data/RMSCorrelate/ -l -r \"({startdtstr},{enddtstr})\"\n')
    outf.write('cd /home/ec2-user/data/RMSCorrelate\n')
    outf.write('logger -s -t runMatching \"creating density plots\"\n')
    outf.write(f'python -m wmpl.Trajectory.AggregateAndPlot  ./trajectories/{yr} -p -s 30\n')
    outf.write(f'python -m wmpl.Trajectory.AggregateAndPlot  ./trajectories/{yr}/{ym} -p -s 30\n')
    outf.write(f'mkdir -p ./trajectories/{yr}/plots\n')
    outf.write(f'mv ./trajectories/{yr}/*.png ./trajectories/{yr}/plots\n')
    outf.write(f'mv ./trajectories/{yr}/trajectory_summary.txt ./trajectories/{yr}/plots\n')
    outf.write(f'mkdir -p ./trajectories/{yr}/{ym}/plots\n')
    outf.write(f'mv ./trajectories/{yr}/{ym}/*.png ./trajectories/{yr}/{ym}/plots\n')
    outf.write(f'mv ./trajectories/{yr}/{ym}/trajectory_summary.txt ./trajectories/{yr}/{ym}/plots\n')
    outf.write('df -h . \n')
    outf.write('logger -s -t runMatching \"done and syncing back\"\n')

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


    outf.write(f'source {shkey}\n')
    outf.write(f'aws s3 sync trajectories/{yr}/plots {shbucket}/matches/RMSCorrelate/trajectories/{yr}/plots --quiet\n')
    outf.write(f'aws s3 sync trajectories/{yr}/{ym}/plots {shbucket}/matches/RMSCorrelate/trajectories/{yr}/{ym}/plots --quiet\n')
    outf.write(f'aws s3 cp processed_trajectories.json {shbucket}/matches/RMSCorrelate/processed_trajectories.json.bigserver --quiet\n')
