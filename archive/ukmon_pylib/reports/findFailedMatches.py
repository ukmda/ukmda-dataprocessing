# Copyright (C) 2018-2023 Mark McIntyre
#
# generate report of failed matches so i can quickly report on why something didn't solve
#

import os
import sys
import glob


def saveData(observation, repfile):
    for li in observation:
        repfile.write(li)
    #print(observation)
    return 


def processOneLog(logfile, repfile):
    lis = open(logfile, 'r').readlines()

    obs = False
    observation = []
    for li in lis:
        if 'Observations ' in li:
            obs = True
        if obs is True:
            observation.append(li)
        if 'Saving trajectory:' in li or 'Updating database' in li:
            obs = False
            observation = []
        if 'Updating database' in li or 'added to fails' in li:
            if obs is True:
                #print('got fail')
                observation.append('--------------\n\n')
                saveData(observation, repfile)
            obs = False
            observation = []
        if "SOLVING RUN DONE" in li:
            break

    return


if __name__ == '__main__':
    repdt = sys.argv[1]
    datadir = os.getenv('DATADIR', default='.')
    os.makedirs(os.path.join(datadir, 'failed'), exist_ok=True)
    reportfile=open(os.path.join(datadir, 'failed', f'{repdt}_failed.txt'), 'w')

    srcdir = os.getenv('SRC', default='.')
    logdir = os.path.join(srcdir, 'logs','distrib')
    logs = glob.glob(f'{repdt}*.log', root_dir=logdir)
    for logf in logs:
        #print(logf)
        processOneLog(os.path.join(logdir, logf), reportfile)
    reportfile.close()
