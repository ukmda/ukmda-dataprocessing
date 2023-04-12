# script to create test data for WMPL 
# Copyright (C) 2018-2023 Mark McIntyre

import sys
import datetime

from fileformats.ftpDetectInfo import writeNewFTPFile, loadFTPDetectInfo


def filterFTPforSpecificTime(ftpfile, dtstr):
    meteor_list = loadFTPDetectInfo(ftpfile, time_offsets=None, join_broken_meteors=True, locdata=None)
    refdt = datetime.datetime.strptime(dtstr, '%Y%m%d_%H%M%S')
    #print(refdt)
    new_met_list = []
    for met in meteor_list:
        #print(met.ff_name)
        dtpart = datetime.datetime.strptime(met.ff_name[10:25], '%Y%m%d_%H%M%S')
        tdiff = (refdt - dtpart).seconds
        #print(tdiff)
        if abs(tdiff) < 21:
            print('adding one entry')
            new_met_list.append(met)
    newname = writeNewFTPFile(ftpfile, new_met_list)
    return newname, len(new_met_list)


if __name__ == '__main__':
    ftpfile = sys.argv[1]
    dtstr = sys.argv[2]
    filterFTPforSpecificTime(ftpfile, dtstr)
