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
    with open(logfile, 'r') as inf:
        lis = inf.readlines()

    obs = False
    observation = []
    for li in lis:
        if 'Observations:' in li:
            obs = True
        if obs is True:
            observation.append(li)
        if 'Shower:' in li:
            obs = False
            observation = []
        if '-----------------------' in li:
            if obs is True:
                saveData(observation, repfile)
            obs = False
            observation = []

    return


if __name__ == '__main__':
    repdt = sys.argv[1]
    datadir = os.getenv('DATADIR', default='.')
    os.makedirs(os.path.join(datadir, 'failed'), exist_ok=True)
    reportfile=open(os.path.join(datadir, 'failed', f'{repdt}_failed.txt'), 'w')

    srcdir = os.getenv('SRC', default='.')
    logdir = os.path.join(srcdir, 'logs','distrib')
    logs = glob.glob1(logdir, f'{repdt}*.log')
    for logf in logs:
        processOneLog(os.path.join(logdir, logf), reportfile)
    reportfile.close()
