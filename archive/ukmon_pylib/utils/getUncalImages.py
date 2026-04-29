# Copyright (C) 2018-2023 Mark McIntyre
#

import os 


def getUncalibratedImageList(dtstr=None):
    datadir=os.getenv('DATADIR', default=os.path.expanduser('~/prod/data'))
    if dtstr is not None:
        logfile = os.path.join(datadir, '..', 'logs', f'matchJob.log.{dtstr}')
    else:
        logfile = os.path.join(datadir, '..', 'logs', 'matchJob.log')
    flines = open(logfile, 'r').readlines()
    uncal = [f for f in flines if 'not recalibrated' in f]
    imglist = [x.split('Skipping ')[1].split(',')[0] for x in uncal]
    with open(os.path.join(datadir, 'single', 'used', f'uncal_{dtstr}.txt'), 'w') as outf:
        for li in imglist:
            outf.write(f'{li}\n')
    return imglist
