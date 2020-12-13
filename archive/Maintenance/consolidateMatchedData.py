# python routine to move A.XML files to a single location

import numpy
import boto3
import csv
import datetime
import sys
import os

sorteidxtype = numpy.dtype([('tstamp', 'f8'), ('localtime', 'S16'),
    ('loccam', 'S16'), ('dir1', 'f8'), ('alt1', 'f8')])


def findSection(fname, tstamp, cam, allcams, lati, longi, alti):
    with open(fname, 'r', newline='') as inf:
        lines = inf.readlines()
    barefname = os.path.basename(fname)
    frags = barefname.split('_')
    dataname = 'data_' + frags[1] + '_' + frags[2] + '_' + frags[3] + '.txt'
    statname = 'stat_' + frags[1] + '_' + frags[2] + '_' + frags[3] + '.txt'
    dtimestmp = ' '
    for i in range(len(lines)):
        li = lines[i]
        if li[:3] == 'FF_':
            bits = li.split('_')
            dt = bits[2]
            tm = bits[3]
            dtimestmp = bits[2] + '_' + bits[3]
            us = int(bits[4]) * 1000
            yr = int(dt[:4])
            mt = int(dt[4:6])
            dy = int(dt[6:])
            sec = int(tm[4:6])

            evttstamp = datetime.datetime(year=yr, month=mt, day=dy,
                hour=int(tm[:2]), minute=int(tm[2:4]), second=sec,
                microsecond=us) + datetime.timedelta(seconds=10)
            if (tstamp - evttstamp.timestamp()) < 10:
                print('found the event at ', evttstamp)
                break

    event = open(dataname, 'w', newline='\n')
    li = lines[i - 1]  # gone one line too far so backup and get the dashes
    event.write(li)
    for k in range(i, len(lines)):
        li = lines[k]
        if li[:3] == '---':
            break
        event.write(li)
    event.close()
    with open(statname, 'w', newline='\n') as f:
        # CAMS format expects west positive, altitide in km
        li = '{:s} {:f} {:f} {:f}'.format(cam, lati, -longi, alti / 1000.0)
        f.write(li)
    return dataname, statname, dtimestmp


def getCameraDetails():
    # fetch camera details from the CSV file
    fldrs = []
    cams = []
    lati = []
    alti = []
    longi = []
    camtyp = []
    fullcams = []
    camfile = 'camera-details.csv'

    s3 = boto3.resource('s3')
    s3.meta.client.download_file('ukmon-shared', 'consolidated/' + camfile, camfile)
    with open(camfile, 'r') as f:
        r = csv.reader(f)
        for row in r:
            if row[0][:1] != '#':
                if row[1] == '':
                    fldrs.append(row[0])
                else:
                    fldrs.append(row[0] + '/' + row[1])
                if int(row[11]) == 1:
                    cams.append(row[2] + '_' + row[3])
                else:
                    cams.append(row[2])
                fullcams.append(row[0] + '_' + row[3])
                longi.append(float(row[8]))
                lati.append(float(row[9]))
                alti.append(float(row[10]))
                camtyp.append(int(row[11]))
    os.remove(camfile)
    return cams, fldrs, lati, longi, alti, camtyp, fullcams


def getCamLocation(c1, allcams, latis, longis, altis):
    i1 = allcams.index(c1)
    lati = latis[i1]
    longi = longis[i1]
    alti = altis[i1]
    return lati, longi, alti


def getRMSIndexFile(yr, mth):
    # fetch consolidated file and fetch out required details
    idxfile = 'P_' + yr + '-unified.csv'
    sortedidx = 'SP_' + yr + '.csv'

    grp = []
    localtime = []
    loccam = []
    dtstamp = []
    dir1 = []
    alt1 = []
    ctyp = []

    print('getting index file for ', yr, mth)
    s3 = boto3.resource('s3')
    s3.meta.client.download_file('ukmon-shared', 'consolidated/' + idxfile, idxfile)

    with open(idxfile, 'r') as f:
        r = csv.reader(f)
        for row in r:
            if row[0] != 'Ver':
                hrs = int(row[4])
                mins = int(row[5])
                secs = float(row[6])
                if int(secs) == 60:
                    secs = 59.0
                    us = 999999
                else:
                    us = (secs - int(secs)) * 1000000

                curmth = int(row[2])
                dt = datetime.datetime(int(row[1]), int(row[2]), int(row[3]),
                    hrs, mins, int(secs), int(us))
                synthlt = dt.strftime('%Y%m%d_%H%M%S')
                if mth is None:
                    dtstamp.append(dt.timestamp())
                    dir1.append(row[9])
                    alt1.append(row[10])
                    grp.append(row[0])   # not used
                    localtime.append(synthlt)
                    loccam.append(row[17])
                    ctyp.append(2)
                else:
                    if mth == curmth:
                        dtstamp.append(dt.timestamp())
                        dir1.append(row[9])
                        alt1.append(row[10])
                        grp.append(row[0])  # not used
                        localtime.append(synthlt)
                        loccam.append(row[17])
                        ctyp.append(2)

    os.remove(idxfile)
    # create a 2-d array and save it so we can read it in the right format
    meteors = numpy.column_stack((dtstamp, localtime, loccam, dir1, alt1, ctyp))
    with open(sortedidx, 'w', newline='') as fout:
        r = csv.writer(fout)
        r.writerows(meteors)

    # uniquify the data by reading into a list, converting the list to a set
    # then sorting it and writing it back to the file
    linelist = [line.rstrip('\n') for line in open(sortedidx, 'r')]
    newlist = sorted(set(linelist[1:]))

    # don't try to analyse an empty dataset!
    if len(newlist) == 0:
        print("nothing to search for matches")
        os.remove(sortedidx)
        return newlist

    with open(sortedidx, 'w') as fout:
        fout.write('\n'.join(newlist))

    # reload the meteor data into an ndarray so we can match[] on it
    meteors = numpy.loadtxt(sortedidx, delimiter=',', skiprows=1, dtype=sorteidxtype)
    os.remove(sortedidx)
    return meteors


def getUFOIndexFile(yr, mth):
    # fetch consolidated file and fetch out required details
    idxfile = 'M_' + yr + '-unified.csv'
    sortedidx = 'S_' + yr + '.csv'

    grp = []
    localtime = []
    loccam = []
    dtstamp = []
    dir1 = []
    alt1 = []
    ctyp = []

    print('getting index file for ', yr, mth)
    s3 = boto3.resource('s3')
    s3.meta.client.download_file('ukmon-shared', 'consolidated/' + idxfile, idxfile)

    with open(idxfile, 'r') as f:
        r = csv.reader(f)
        for row in r:
            if row[0] != 'Ver':
                hrs = int(row[11])
                mins = int(row[12])
                secs = float(row[13])
                if int(secs) == 60:
                    secs = 59.0
                    us = 999999
                else:
                    us = (secs - int(secs)) * 1000000

                curmth = int(row[9])
                dt = datetime.datetime(int(row[8]), int(row[9]), int(row[10]),
                    hrs, mins, int(secs), int(us))
                if mth is None:
                    dtstamp.append(dt.timestamp())
                    dir1.append(row[14])
                    alt1.append(row[15])
                    grp.append(row[1])
                    localtime.append(row[2])
                    loccam.append(row[6])
                    ctyp.append(1)
                else:
                    if mth == curmth:
                        dtstamp.append(dt.timestamp())
                        dir1.append(row[14])
                        alt1.append(row[15])
                        grp.append(row[1])
                        localtime.append(row[2])
                        loccam.append(row[6])
                        ctyp.append(1)

    os.remove(idxfile)
    # create a 2-d array and save it so we can read it in the right format
    meteors = numpy.column_stack((dtstamp, localtime, loccam, dir1, alt1, ctyp))
    with open(sortedidx, 'w', newline='') as fout:
        r = csv.writer(fout)
        r.writerows(meteors)

    # uniquify the data by reading into a list, converting the list to a set
    # then sorting it and writing it back to the file
    linelist = [line.rstrip('\n') for line in open(sortedidx, 'r')]
    newlist = sorted(set(linelist[1:]))

    # return an empty list if we have one
    if len(newlist) == 0:
        os.remove(sortedidx)
        return newlist

    with open(sortedidx, 'w') as fout:
        fout.write('\n'.join(newlist))

    # reload the meteor data into an ndarray so we can match[] on it
    meteors = numpy.loadtxt(sortedidx, delimiter=',', skiprows=1, dtype=sorteidxtype)
    os.remove(sortedidx)
    return meteors


def copyFile(loctime, loccam, tm, cams, fldrs, errf, camtyps, latis, longis, altis, fullcams):
    s3 = boto3.resource('s3')
    api_client = s3.meta.client
    bucket_name = 'ukmon-shared'

    loccam = loccam.decode('utf-8').strip()
    loctime = loctime.decode('utf-8')

    tmstr = datetime.datetime.fromtimestamp(tm).strftime('%Y%m%d_%H%M%S')
    idx = cams.index(loccam)
    pth = 'archive/' + fldrs[idx] + '/'
    camtyp = camtyps[idx]
    fullcam = fullcams[idx]

    ymstr = str(loctime)[:4] + '/' + str(loctime)[:6]
    ymds = ymstr + '/' + str(loctime)[:8] + '/'

    if camtyp == 1:
        fnam = 'M' + loctime + '_' + loccam + 'A.XML'
        destpath = 'matches/' + ymstr + '/' + tmstr + '/' + fnam

        # UFO data may be held in a folder by date of event
        # or in a folder datestamped with the day that capture began
        # so we need to look in D and D-1
        try:
            fnam = 'M' + loctime + '_' + loccam + 'A.XML'
            srcpath = pth + ymds + fnam
            api_client.copy_object(Bucket=bucket_name,
                Key=destpath, CopySource={'Bucket': bucket_name, 'Key': srcpath})
            print('d-0 ', fnam, tmstr)
        except:
            try:
                msg = 'unable to open ' + srcpath + ', trying D-1'
                yr = int(loctime[:4])
                mt = int(loctime[4:6])
                dy = int(loctime[6:8])
                prevdt = datetime.datetime(year=yr, month=mt, day=dy) - datetime.timedelta(days=1)
                ymd2 = prevdt.strftime('%Y') + '/' + prevdt.strftime('%Y%m') + '/' + prevdt.strftime('%Y%m%d') + '/'
                srcpath = pth + ymd2 + fnam
                api_client.copy_object(Bucket=bucket_name,
                    Key=destpath, CopySource={'Bucket': bucket_name, 'Key': srcpath})
                print('d-1 ', fnam, tmstr)
            except:
                msg = 'unable to open ' + srcpath
                errf.write(msg + '\n')
                print(msg)
        try:
            fnam = 'M' + loctime + '_' + loccam + 'P.jpg'
            destpath = 'matches/' + ymstr + '/' + tmstr + '/' + fnam
            api_client.copy_object(Bucket=bucket_name,
                Key=destpath, CopySource={'Bucket': 'ukmon-live', 'Key': fnam})
            print('d-0 ', fnam, tmstr)
            fnam = 'M' + loctime + '_' + loccam + '.mp4'
            destpath = 'matches/' + ymstr + '/' + tmstr + '/' + fnam
            api_client.copy_object(Bucket=bucket_name,
                Key=destpath, CopySource={'Bucket': 'ukmon-live', 'Key': fnam})
            print('d-0 ', fnam, tmstr)
        except:
            msg = 'unable to copy ' + fnam
            errf.write(msg + '\n')
            print(msg)

    else:
        s3 = boto3.client('s3')
        lati, longi, alti = getCamLocation(loccam, cams, latis, longis, altis)
        hr = datetime.datetime.fromtimestamp(tm).hour
        if hr < 12:
            yr = int(loctime[:4])
            mt = int(loctime[4:6])
            dy = int(loctime[6:8])
            prevdt = datetime.datetime(year=yr, month=mt, day=dy) - datetime.timedelta(days=1)
            ymd2 = prevdt.strftime('%Y') + '/' + prevdt.strftime('%Y%m') + '/' + prevdt.strftime('%Y%m%d') + '/'
            srcpath = pth + ymd2
        else:
            srcpath = pth + ymds
        s3res = s3.list_objects_v2(Bucket=bucket_name, Prefix=srcpath)
        if 'Contents' not in s3res:
            print('no contents found')
        else:
            for key in s3res['Contents']:
                ftpf = key['Key']
                fnam = ftpf[len(srcpath):]
                if fnam[:6] == 'FTPdet':
                    break
            barefnam = os.path.basename(fnam)
            s3.download_file(Bucket=bucket_name, Key=ftpf, Filename=barefnam)
            dataname, statname, dtimestmp = findSection(barefnam, tm, loccam, cams, lati, longi, alti)

            destpath = 'matches/' + ymstr + '/' + tmstr + '/' + dataname
            s3.upload_file(Bucket=bucket_name, Key=destpath, Filename=dataname)
            destpath = 'matches/' + ymstr + '/' + tmstr + '/' + statname
            s3.upload_file(Bucket=bucket_name, Key=destpath, Filename=statname)
            os.remove(barefnam)
            os.remove(dataname)
            os.remove(statname)
            print('d-0 ', fnam, tmstr)
            try:
                # HACK FOR TACKLEY CAMERA PRIOR TO END NOV 2020
                switchtime = datetime.datetime(2020, 11, 25, 20, 0, 0, 0)
                if fullcam[:7] == 'Tackley' and datetime.datetime.fromtimestamp(tm) < switchtime:
                    fullcam = 'Tackley'
                fnam = 'M' + dtimestmp + '_' + fullcam + '_' + loccam + 'P.jpg'
                destpath = 'matches/' + ymstr + '/' + tmstr + '/' + fnam
                api_client.copy_object(Bucket=bucket_name,
                    Key=destpath, CopySource={'Bucket': 'ukmon-live', 'Key': fnam})
                print('d-0 ', fnam, tmstr)
                fnam = 'M' + loctime + '_' + fullcam + '_' + loccam + '.mp4'
                destpath = 'matches/' + ymstr + '/' + tmstr + '/' + fnam
                api_client.copy_object(Bucket=bucket_name,
                    Key=destpath, CopySource={'Bucket': 'ukmon-live', 'Key': fnam})
                print('d-0 ', fnam, tmstr)
            except:
                msg = 'unable to copy ' + fnam
                errf.write(msg + '\n')
                print(msg)
        return


def FindMatches(yr, mth=None):
    print('getting camera details file')
    cams, fldrs, lati, longi, alti, camtyps, fullcams = getCameraDetails()

    print('getting UFO index file')
    meteors1 = getUFOIndexFile(yr, mth)

    print('getting RMS index file')
    meteors2 = getRMSIndexFile(yr, mth)

    meteors = numpy.append(meteors1, meteors2)
    meteors.sort(order='tstamp')

    # don't try to analyse an empty dataset!
    if len(meteors) == 0:
        print("no data returned to to search for matches in")
        return

    wholefile = 'MERGED_' + yr + '-unified.csv'
    with open(wholefile, 'w') as fout:
        for li in meteors:
            fout.write('{:.2f},{:s},{:s},{:.4f},{:.4f}\n'.format(li['tstamp'],
                li['localtime'], li['loccam'], li['dir1'], li['alt1']))

    # create logfile
    errfname = 'missing-data-report.txt'
    errf = open(errfname, 'w')

    # search for matches
    lasttm = 0
    for rw in meteors:
        tm = rw['tstamp']

        cond = (abs(meteors['tstamp'] - tm) < 5.0)
        matchset = meteors[cond]

        # go through to make sure we aren't including the same station twice
        skipme = False
        nummatches = len(matchset)
        ignore = numpy.zeros(nummatches)
        if nummatches > 1:
            for i in range(nummatches):
                # d = datetime.datetime.fromtimestamp(matchset[i]['tstamp']).strftime('%Y%m%d_%H%M%S')
                # print(nummatches, matchset[i]['loccam'], ignore[i], d)
                for j in range(i + 1, nummatches):
                    if matchset[i]['loccam'][:6].upper() == matchset[j]['loccam'][:6].upper():
                        ignore[j] = 1
                    lat1, long1, _ = getCamLocation(matchset[i]['loccam'].decode('utf-8').strip(), cams, lati, longi, alti)
                    lat2, long2, _ = getCamLocation(matchset[j]['loccam'].decode('utf-8').strip(), cams, lati, longi, alti)
                    if abs(long1 - long2) < 0.01 and abs(lat1 - lat2) < 0.01:
                        ignore[j] = 1
                    # if ignore[j] == 0:
                        # d = datetime.datetime.fromtimestamp(matchset[j]['tstamp']).strftime('%Y%m%d_%H%M%S')
                        # print('    ', matchset[j]['loccam'], ignore[j], d)

            if sum(ignore) > nummatches - 2:
                # print('skipping ', nummatches, sum(ignore))
                skipme = True

            # got at least a distinct pair and we're not rematching the last matches
            if len(matchset) > 1 and skipme is False and abs(lasttm - tm) > 4.99999:
                print('got', len(matchset), 'matches')
                lasttm = tm
                numpy.sort(matchset)
                print('=============')
                for i in range(nummatches):
                    if ignore[i] == 0:
                        el = matchset[i]
                        print(el['localtime'], el['loccam'])
                        copyFile(el['localtime'], el['loccam'], tm, cams, fldrs, errf, camtyps, lati, longi, alti, fullcams)

    # upload logfile
    errf.close()
    s3 = boto3.client('s3')
    bucket_name = 'ukmon-shared'
    key = 'matches/' + errfname
    s3.upload_file(Bucket=bucket_name, Key=key, Filename=errfname)
    os.remove(errfname)


if __name__ == '__main__':
    mth = None
    if len(sys.argv) == 3:
        mth = int(sys.argv[2])

    FindMatches(sys.argv[1], mth)
