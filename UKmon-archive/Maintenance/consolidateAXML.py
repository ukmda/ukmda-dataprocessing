# python routine to move A.XML files to a single location

import numpy
import boto3
import csv
import datetime
import sys

sorteidxtype = numpy.dtype([('tstamp', 'f8'), ('localtime', 'S16'),
    ('loccam', 'S16'), ('dir1', 'f8'), ('alt1', 'f8')])


def copyFile(loctime, loccam, tm, cams, fldrs, errf):
    s3 = boto3.resource('s3')
    api_client = s3.meta.client
    bucket_name = 'ukmon-shared'

    loccam = loccam.decode('utf-8').strip()
    loctime = loctime.decode('utf-8')

    tmstr = datetime.datetime.fromtimestamp(tm).strftime('%Y%m%d_%H%M%S')
    idx = cams.index(loccam)
    pth = 'archive/' + fldrs[idx] + '/'

    ymds = str(loctime)[:4] + '/' + str(loctime)[:6] + '/' + str(loctime)[:8] + '/'

    fnam = 'M' + loctime + '_' + loccam + 'A.XML'
    destpath = 'matches/' + tmstr + '/' + fnam

    try:
        fnam = 'M' + loctime + '_' + loccam + 'A.XML'
        srcpth = pth + ymds + fnam
        api_client.copy_object(Bucket=bucket_name,
            Key=destpath, CopySource={'Bucket': bucket_name, 'Key': srcpth})
        print('o')
    except:
        try:
            msg = 'unable to open ' + srcpth + ', trying T-1'
            # UFO data may be held in a folder by date
            # or in a folder datestamped with the day that capture began
            yr = int(loctime[:4])
            mt = int(loctime[4:6])
            dy = int(loctime[6:8])
            prevdt = datetime.datetime(year=yr, month=mt, day=dy) - datetime.timedelta(days=1)
            ymd2 = prevdt.strftime('%Y') + '/' + prevdt.strftime('%Y%m') + '/' + prevdt.strftime('%Y%m%d') + '/'
            srcpth = pth + ymd2 + fnam
            api_client.copy_object(Bucket=bucket_name,
                Key=destpath, CopySource={'Bucket': bucket_name, 'Key': srcpth})
            # print('copied ', key, ' to ', destpath)
            print('x')
        except:
            msg = 'unable to open ' + srcpth
            errf.write(msg + '\n')
            print(msg)


def FindMatches(yr):
    # fetch camera details from the CSV file
    camfile = 'camera-details.csv'
    fldrs = []
    cams = []

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
                cams.append(row[2] + '_' + row[3])

    # print(cams)
    # fetch consolidated file and fetch out required details
    idxfile = 'M_' + yr + '-unified.csv'
    sortedidx = 'S_' + yr + '.csv'

    grp = []
    localtime = []
    loccam = []
    dtstamp = []
    dir1 = []
    alt1 = []

    s3 = boto3.resource('s3')
    s3.meta.client.download_file('ukmon-shared', 'consolidated/' + idxfile, idxfile)

    with open(idxfile, 'r') as f:
        r = csv.reader(f)
        for row in r:
            if row[0] != 'Ver':
                grp.append(row[1])
                localtime.append(row[2])
                loccam.append(row[6])
                hrs = int(row[11])
                mins = int(row[12])
                secs = float(row[13])
                if int(secs) == 60:
                    secs = 59.0
                    us = 999999
                else:
                    us = (secs - int(secs)) * 1000000

                dt = datetime.datetime(int(row[8]), int(row[9]), int(row[10]),
                    hrs, mins, int(secs), int(us))
                dtstamp.append(dt.timestamp())
                dir1.append(row[14])
                alt1.append(row[15])

    # create a 2-d array and save it so we can read it in the right format
    meteors = numpy.column_stack((dtstamp, localtime, loccam, dir1, alt1))
    with open(sortedidx, 'w', newline='') as fout:
        r = csv.writer(fout)
        r.writerows(meteors)

    # uniquify the data by reading into a list, converting the list to a set
    # then sorting it and writing it back to the file
    linelist = [line.rstrip('\n') for line in open(sortedidx, 'r')]
    newlist = sorted(set(linelist[1:]))
    with open(sortedidx, 'w') as fout:
        fout.write('\n'.join(newlist))

    # reload the meteor data into an ndarray so we can match[] on it
    meteors = numpy.loadtxt(sortedidx, delimiter=',', skiprows=1, dtype=sorteidxtype)

    # create logfile
    errfname = 'missing-data-report.txt'
    errf = open(errfname, 'w')

    # search for matches
    lasttm = 0
    for rw in meteors:
        tm = rw['tstamp']
        loccam = rw['loccam']

        cond = (abs(meteors['tstamp'] - tm) < 5) & (meteors['loccam'] != loccam)
        matchset = meteors[cond]

        # got one match and we're not rematching the last matches
        if len(matchset) > 1 and abs(lasttm - tm) > 4.99999:
            lasttm = tm
            numpy.sort(matchset)
            print('=============')
            for el in matchset:
                # print(el['tstamp'], el['localtime'], el['loccam'],
                #    el['dir1'], el['alt1'])
                copyFile(el['localtime'], el['loccam'], tm, cams, fldrs, errf)

    # upload logfile
    errf.close()
    s3 = boto3.client('s3')
    bucket_name = 'ukmon-shared'
    key = 'matches/' + errfname
    s3.upload_file(Bucket=bucket_name, Key=key, Filename=errfname)


if __name__ == '__main__':
    FindMatches(sys.argv[1])
