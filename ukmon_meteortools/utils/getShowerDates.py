# Copyright (C) 2018-2023 Mark McIntyre
#
# simple script to get the active shower list from the IMO working list

import numpy as np
import sys
import os
import datetime

from ukmon_meteortools.utils import jd2Date, sollon2jd
try:
    from UpdateOrbitFiles import updateOrbitFiles ## to update WMPL raw data files
    gotupdater = True
except:
    gotupdater = False


def _loadFullData(pth=None):
    return _loadDataFile(1, pth)


def _loadLookupTable(pth=None):
    return _loadDataFile(2, pth)


def _loadJenniskensShowers(dir_path, file_name):
    """ Load the showers from the Jenniskens et al. (2018) table and init MeteorShower objects. """
    jenniskens_shower_list = []
    with open(os.path.join(dir_path, file_name), encoding='cp1252') as f:
        data_start = 0
        for line in f:
            if "====================================" in line:
                data_start += 1
                continue
            if data_start < 2:
                continue
            line = line.replace('\n', '').replace('\r', '')
            if not line:
                continue
            if "[FINAL]" in line:
                break
            l0, L_l0, B_g, v_g, IAU_no = line.split()
            jenniskens_shower_list.append([np.radians(float(l0)), np.radians(float(L_l0)), 
                np.radians(float(B_g)), 1000*float(v_g), int(IAU_no)])
    return np.array(jenniskens_shower_list)


def _refreshShowerData():
    if gotupdater is True:
        updateOrbitFiles()
    abs_path = os.getenv('WMPL_LOC', default='/home/ec2-user/src/WesternMeteorPyLib')
    jenniskens_shower_table_file = os.path.join(abs_path, 'wmpl', 'share', 'ShowerLookUpTable.txt')
    jenniskens_shower_table_npy = os.path.join(abs_path, 'wmpl', 'share', 'ShowerLookUpTable.npy')
    jenniskens_shower_list = _loadJenniskensShowers(*os.path.split(jenniskens_shower_table_file))
    np.save(jenniskens_shower_table_npy, jenniskens_shower_list)
    iau_shower_table_file = os.path.join(abs_path, 'wmpl', 'share', 'streamfulldata.csv')
    iau_shower_table_npy = os.path.join(abs_path, 'wmpl', 'share', 'streamfulldata.npy')
    iau_shower_list = np.loadtxt(iau_shower_table_file, delimiter="|", usecols=range(20), dtype=str)
    np.save(iau_shower_table_npy, iau_shower_list)


def _loadDataFile(typ, pth=None):
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
    """ Get details of a shower 
    
    Arguments:  
        shwr:   [string] three-letter shower code eg PER  
         
    Returns:  
        (id, full name, peak solar longitude, peak date mm-dd)  
    """
    sfd = _loadFullData()
    sfdfltr = sfd[sfd[:,3] == shwr]
    mtch = [sh for sh in sfdfltr if sh[6] != '-2']
    if len(mtch) == 0:
        return 0, 'Unknown', 0, 'Unknown'

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
    """ Get date of a shower peak in MM-DD format
    
    Arguments:  
        shwr:   [string] three-letter shower code eg PER  
         
    Returns:  
        peak date mm-dd  
    """
    _, _, _, pk = getShowerDets(shwr)
    return pk

 
if __name__ == '__main__':
    if sys.argv[1] == 'refresh':
        _refreshShowerData()
        exit(0)
    else:
        id, nam, sl, dt = getShowerDets(sys.argv[1])
        print('{},{},{},{}'.format(sl, dt, nam, sys.argv[1]))
