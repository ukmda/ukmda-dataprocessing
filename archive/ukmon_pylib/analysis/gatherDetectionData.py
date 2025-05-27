#
# Collect data for a potential match at a specific time
#
# Copyright (C) 2018-2023 Mark McIntyre
# 
import os 
import sys
import datetime

from meteortools.ukmondb import getECSVs, getLiveJpgs, getFBfiles, getDetections


def getUncalibratedImageList(dtstr=None):
    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    logfile = os.path.join(datadir, '..', 'logs', 'matchJob.log')
    flines = open(logfile, 'r').readlines()
    uncal = [f for f in flines if 'not recalibrated' in f]
    imglist = [x.strip(' ').split(' ')[1][:-1] for x in uncal]
    with open(os.path.join(datadir, 'single', 'used', f'uncal_{dtstr}.txt'), 'w') as outf:
        for li in imglist:
            outf.write(f'{li}\n')
    return imglist


def getRawData(idlist, outpth):
    for _,row in idlist.iterrows():
        stat =row.ID
        dts = datetime.datetime.strptime(row.Dtstamp, '%Y%m%d_%H%M%S')
        dt = dts.strftime('%Y-%m-%dT%H:%M:%S')
        fboutdir = os.path.join(outpth, stat)
        dtstr = row.Filename[10:25]
        getLiveJpgs(dtstr, outpth, False)
        getFBfiles(f'{stat}_{dtstr}', fboutdir)
        getECSVs(stat, dt, True, fboutdir)
    return 


if __name__ == '__main__':
    outpth = f'./{sys.argv[1]}'
    os.makedirs(outpth, exist_ok=True)
    idlist = getDetections(sys.argv[1])
    if not isinstance(idlist, bool):
        getRawData(idlist, outpth)
        ids = list(idlist.ID)
        with open(os.path.join(outpth, 'ids.txt'), 'w') as outf:
            outf.writelines(line + '\n' for line in ids)
        print(ids)
    else:
        print('no matches')
