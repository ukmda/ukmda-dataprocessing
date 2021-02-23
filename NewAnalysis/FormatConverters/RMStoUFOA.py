#
# python module to read RMS data and convert it to UA format
# so that it can be combined with UFO data
#

import sys
import os
import numpy as np
import Formats.RMSFormats as rmsf
import configparser as cfg

# for numpy.savetxt
fmtstr='%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s'


def matchShowerNames(UAdata, rmsshwr):
    i=0
    for i in range(len(UAdata)):
        li = UAdata[i]
        yr = li[8].astype('i4')
        mo = li[9].astype('i4')
        dy = li[10].astype('i4')
        hr = li[11].astype('i4')
        mi = li[12].astype('i4')
        se = li[13].astype('f8')
        matchcond = np.logical_and(rmsshwr['Yr'] == yr, np.logical_and(rmsshwr['Mth'] == mo, 
            np.logical_and(rmsshwr['Day'] == dy, np.logical_and(rmsshwr['Hr'] ==hr, 
            np.logical_and(rmsshwr['Min'] == mi, abs(rmsshwr['Sec'] - se) < 0.2)))))
        match=rmsshwr[matchcond]
        if len(match) > 0:
            ids=match['Shwr']
            #if len(match)>1:
            #    print(len(match), 'matches')
            #    print(ids)
            if ids[0] == 'SPO':
                UAdata[i][1]='spo'
            else:
                UAdata[i][1]='J8_'+ids[0]
    return


def RMStoUFOA(configfile, rmssingle, rmsassoc, rmsuafile, templatedir):
    config=cfg.ConfigParser()
    config.read(configfile)
    
    # load the RMS data
    rmsdata = np.loadtxt(rmssingle, delimiter=',', skiprows=1, dtype=rmsf.R90CSV)
    rmsshwr = np.loadtxt(rmsassoc, delimiter=',', skiprows=1, dtype=rmsf.assocCSV)
    rmsdata = np.unique(rmsdata)
    rmsshwr = np.unique(rmsshwr)
    rmsdata.sort(order=['Yr', 'Mth', 'Day', 'Hr', 'Min', 'Sec', 'Loc_Cam'])
    rmsshwr.sort(order=['Yr', 'Mth', 'Day', 'Hr', 'Min', 'Sec', 'ID'])

    # create arrays of zeros to put in the unused columns
    zeros=np.zeros(len(rmsdata))

    # create array for shower names
    shwr=np.chararray(len(rmsdata), itemsize=8)
    shwr[:]='J8_TBC'
    shwr=shwr.decode('utf-8')

    # also need an underscore character for assembling the LocalTime field
    uscore=np.chararray(len(rmsdata))
    uscore[:]='_'
    uscore=uscore.decode('utf-8')

    # create a localtime in the required format
    ymd = (rmsdata['Yr']*10000+rmsdata['Mth']*100+rmsdata['Day']).astype('U8')
    hms = (rmsdata['Hr']*10000+rmsdata['Min']*100+rmsdata['Sec'])
    hms =np.floor(hms).astype('i4').astype('U8')
    timestr=[]
    for v in hms:
        timestr.append(v.zfill(6))
    localtime = np.core.defchararray.add(ymd, uscore)
    localtime = np.core.defchararray.add(localtime, timestr)

    # read the header in
    tmpl = os.path.join(templatedir, 'UA_header.txt')
    with open(tmpl, 'r') as f:
        hdr = f.readline()

    # write out the converted data
    UAdata = np.column_stack((rmsdata['Ver'],shwr, localtime, rmsdata['Mag'], rmsdata['Dur'], zeros,
        rmsdata['Loc_Cam'], rmsdata['TZ'], rmsdata['Yr'], rmsdata['Mth'], rmsdata['Day'],
        rmsdata['Hr'], rmsdata['Min'], rmsdata['Sec'],
        rmsdata['Dir1'], rmsdata['Alt1'], rmsdata['Ra1'],rmsdata['Dec1'],
        rmsdata['Ra2'],rmsdata['Dec2'],
        zeros, zeros, zeros, zeros, zeros, zeros, zeros, zeros, zeros, zeros, zeros, zeros,
        zeros, zeros, zeros, zeros, zeros, zeros, zeros, zeros, zeros, zeros, zeros, zeros, 
        zeros, zeros, zeros))

    # fill in shower names
    matchShowerNames(UAdata, rmsshwr)

    np.savetxt(rmsuafile, 
        UAdata, fmt=fmtstr, header=hdr, comments='')
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('usage: python RMStoUFOA.py configfile RMS-singles RMS-assocs RMS-UA-singles templatedir')
        exit(1)
    else:
        ret = RMStoUFOA(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
        exit(ret)
