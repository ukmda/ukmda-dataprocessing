#
# python module to read RMS data and convert it to UA format
# so that it can be combined with UFO data
#

import sys
import os
import numpy as np
import pandas
import fileformats.RMSFormats as rmsf


def matchShowerNames(UAdata, rmsshwr):
    # this is VERY slow, need a better approach than iteration
    for i in range(len(rmsshwr)):
        shwr = rmsshwr[i]['Shwr']
        if shwr == 'SPO':
            shwr = 'spo'
        else:
            shwr = 'J8_' + shwr
        UAd=UAdata[(UAdata['Y(UT)']==rmsshwr[i]['Yr']) &
            (UAdata['M(UT)']==rmsshwr[i]['Mth']) &
            (UAdata['D(UT)']==rmsshwr[i]['Day']) &
            (UAdata['H(UT)']==rmsshwr[i]['Hr']) &
            (UAdata['M']==rmsshwr[i]['Min']) &
            (abs(UAdata['S']-rmsshwr[i]['Sec']) < 0.01) &
            (UAdata['Loc_Cam']==rmsshwr[i]['ID'])]
        if len(UAd) > 0:
            UAdata.at[UAd.index[0],'Group'] = shwr
            print('shower is', UAdata.at[UAd.index[0],'Group'])
        else:
            print('no match')
    return


def RMStoUFOA(rmssingle, rmsassoc, rmsuafile, templatedir):
    
    # load the RMS data
    print('loading the data')
    rmsdata = np.loadtxt(rmssingle, delimiter=',', skiprows=1, dtype=rmsf.R90CSV)
    rmsshwr = np.loadtxt(rmsassoc, delimiter=',', skiprows=1, dtype=rmsf.assocCSV)
    print('uniquifying and sorting it')
    rmsdata = np.unique(rmsdata)
    rmsshwr = np.unique(rmsshwr)
    rmsdata.sort(order=['Yr', 'Mth', 'Day', 'Hr', 'Min', 'Sec', 'Loc_Cam'])
    rmsshwr.sort(order=['Yr', 'Mth', 'Day', 'Hr', 'Min', 'Sec', 'ID'])

    # create arrays of zeros to put in the unused columns
    print('create array of zeros')
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
    print('creating the timestr array')
    for v in hms:
        timestr.append(v.zfill(6))
    localtime = np.core.defchararray.add(ymd, uscore)
    localtime = np.core.defchararray.add(localtime, timestr)

    # read the header in
    print('reading the header')
    tmpl = os.path.join(templatedir, 'UA_header.txt')
    with open(tmpl, 'r') as f:
        hdr = f.readline()

    hdrlst=hdr.strip().split(',')
    # write out the converted data
    print('create output array')
    UAdata = pandas.DataFrame({hdrlst[0]: rmsdata['Ver']})
    UAdata[hdrlst[1]] = shwr
    UAdata[hdrlst[2]] = localtime
    UAdata[hdrlst[3]] = rmsdata['Mag']
    UAdata[hdrlst[4]] = rmsdata['Dur']
    UAdata[hdrlst[5]] = zeros # AV not available from RMS
    UAdata[hdrlst[6]] = rmsdata['Loc_Cam']
    UAdata[hdrlst[7]] = rmsdata['TZ']
    UAdata[hdrlst[8]] = rmsdata['Yr']
    UAdata[hdrlst[9]] = rmsdata['Mth']
    UAdata[hdrlst[10]] = rmsdata['Day']
    UAdata[hdrlst[11]] = rmsdata['Hr']
    UAdata[hdrlst[12]] = rmsdata['Min']
    UAdata[hdrlst[13]] = rmsdata['Sec']
    UAdata[hdrlst[14]] = rmsdata['Dir1']
    UAdata[hdrlst[15]] = rmsdata['Alt1']
    UAdata[hdrlst[16]] = rmsdata['Ra1']
    UAdata[hdrlst[17]] = rmsdata['Dec1']
    UAdata[hdrlst[18]] = rmsdata['Ra2']
    UAdata[hdrlst[19]] = rmsdata['Dec2']
    # remaining values are UFO-specific and not used by RMS/WMPL
    for i in range(20,47):
        if hdrlst[i]==' ': 
            hdrlst[i]='Fld'+str(i)
        UAdata[hdrlst[i]] = zeros

    # fill in shower names
    print('find matching shower names')
    matchShowerNames(UAdata, rmsshwr)

    # deal with cases where secs > 59.99 and got rounded up to 60
    # bit of a hack, needs fixed properly #FIXME
    u=UAdata[UAdata['S']>59.99]
    if len(u)>0:
        lt = UAdata.at[u.index[0],'LocalTime']
        UAdata.at[u.index[0],'LocalTime'] = lt[:-2] + '59'

    print('save back to file')
    UAdata.to_csv(rmsuafile, index=False)

    return 0


if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('usage: python RMStoUFOA.py configfile RMS-singles RMS-assocs RMS-UA-singles templatedir')
        exit(1)
    else:
        rmssingles = sys.argv[1]
        rmsassocs = sys.argv[2]
        rmsuafile = sys.argv[3]
        templatedir = sys.argv[4]
        
        ret = RMStoUFOA(rmssingles, rmsassocs, rmsuafile, templatedir)
        exit(ret)
