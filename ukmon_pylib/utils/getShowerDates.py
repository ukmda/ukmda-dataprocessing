#
# simple script to get the active shower list from the IMO working list

import numpy as np
import sys
import os
import datetime

from wmpl.Utils.TrajConversions import jd2Date
from utils.convertSolLon import sollon2jd


def loadFullData(pth=None):
    return loadDataFile(1, pth)


def loadLookupTable(pth=None):
    return loadDataFile(2, pth)


def loadDataFile(typ, pth=None):
    if typ == 1:
        fname='streamfulldata.npy'
    elif typ == 2:
        fname='ShowerLookupTable.npy'
    else:
        return 'invalid type code'

    if pth is None:
        if sys.platform == 'win32':
            pth = 'e:/dev/meteorhunting/WesternMeteorPyLib/wmpl/share'
        else:
            pth = '/home/ec2-user/src/WesternMeteorPyLib/wmpl/share'
    dfil = np.load(os.path.join(pth, fname))
    return dfil


def getShowerDets(shwr):
    sfd = loadFullData()
    sfdfltr = sfd[sfd[:,3] == shwr]
    mtch = [sh for sh in sfdfltr if sh[6] != '-2']
    id = int(mtch[-1][1])
    nam = mtch[-1][4].strip()
    pksollong = float(mtch[-1][7])
    dt = datetime.datetime.now()
    yr = dt.year
    mth = dt.month
    jd = sollon2jd(yr, mth, pksollong)
    pkdt = jd2Date(jd, dt_obj=True)
    return id, nam, pksollong, pkdt.strftime('%m-%d')


def getShowerPeak(shwr):
    _, _, _, pk = getShowerDets(shwr)
    return pk

 
if __name__ == '__main__':
    id, nam, sl, dt = getShowerDets(sys.argv[1])
    print('{},{},{},{}'.format(sl, dt, nam, sys.argv[1]))
