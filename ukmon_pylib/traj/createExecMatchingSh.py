#
# Python script to create execMatching shell script to be run on the calc engine
#

import os
import sys
import datetime


shkey = os.getenv('UKMONSHAREDKEY')
shbucket = os.getenv('UKMONSHAREDBUCKET')
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
    outf.write(f'source {shkey}\n')
    outf.write('cd /home/ec2-user/data/RMSCorrelate\n')
    outf.write(f'python -m wmpl.Trajectory.AggregateAndPlot  ./trajectories/{yr} -p -s 30')
    outf.write(f'python -m wmpl.Trajectory.AggregateAndPlot  ./trajectories/{yr}/{ym} -p -s 30')
    outf.write(f'mkdir -p ./trajectories/{yr}/plots')
    outf.write(f'mv ./trajectories/{yr}/*.png ./trajectories/{yr}/plots')
    outf.write(f'mv ./trajectories/{yr}/trajectory_summary.txt ./trajectories/{yr}/plots')
    outf.write(f'mkdir -p ./trajectories/{yr}/{ym}/plots')
    outf.write(f'mv ./trajectories/{yr}/{ym}/*.png ./trajectories/{yr}/{ym}/plots')
    outf.write(f'mv ./trajectories/{yr}/{ym}/trajectory_summary.txt ./trajectories/{yr}/{ym}/plots')
    outf.write('df -h . \n')
    
    outf.write('logger -s -t runMatching \"done and syncing back\"\n')
    for d in range(matchend, matchstart+1):
        thisdt=datetime.datetime.now() + datetime.timedelta(days=-d)
        trajloc=f'{thisdt.year}/{thisdt.year}{thisdt.month:02d}/{thisdt.year}{thisdt.month:02d}{thisdt.day:02d}'
        outf.write(f'aws s3 sync trajectories/{trajloc} {shbucket}/matches/RMSCorrelate/trajectories/{trajloc} --quiet\n')

    outf.write(f'aws s3 sync trajectories/{yr}/plots {shbucket}/matches/RMSCorrelate/trajectories/{yr}/plots --quiet\n')
    outf.write(f'aws s3 sync trajectories/{yr}/{ym}/plots {shbucket}/matches/RMSCorrelate/trajectories/{yr}/{ym}/plots --quiet\n')
    outf.write(f'aws s3 cp processed_trajectories.json {shbucket}/matches/RMSCorrelate/processed_trajectories.json.bigserver --quiet\n')

#chmod +x $execMatchingsh
