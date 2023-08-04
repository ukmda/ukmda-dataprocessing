# Copyright (C) 2018-2023 Mark McIntyre 

# create an initial index file for the ukmon-live stream
#
import os
import datetime
import math
import boto3
import ReadUFOCapXML


def AddToIndex(fname, idxfile, pth):
    dd = ReadUFOCapXML.UCXml(os.path.join(pth, fname))
    pathx, pathy, bri, _ = dd.getPath()
    bri = int(max(bri))

    dmy = fname[1:9]
    hms = fname[10:16]
    stat = fname[17:fname.rfind('.')]
    sid = stat[:stat.rfind('_')]
    lid = stat[stat.rfind('_') + 1:]

    strtowrite = dmy + ',' + hms + ',' + sid + ',' + lid + ',{:d}\n'.format(bri)
    idxfile.write(strtowrite)
    return


def createIndex(target, doff=1):
    try:
        tmppth = os.environ['TMP']
    except:
        tmppth = '/tmp'

    # download the current index file
    s3 = boto3.client('s3')
    tod = datetime.datetime.today() - datetime.timedelta(days=doff)
    tmpf = 'idx{:04d}{:02d}.csv'.format(tod.year, math.ceil(tod.month / 3))
    idxfile = os.path.join(tmppth, tmpf)
    try:
        s3.download_file(target, tmpf, idxfile)
    except:
        pass
    f = open(idxfile, "a+")

    # find pertinent files
    pref = 'M{:04d}{:02d}{:02d}'.format(tod.year, tod.month, tod.day)
    flist = s3.list_objects_v2(Bucket=target, Prefix=pref)
    if 'Contents' not in flist:  # no matching files
        return

    for key in flist['Contents']:
        xmlname = key['Key']
        if xmlname[len(xmlname) - 3:] == 'xml':
            s3.download_file(target, xmlname, os.path.join(tmppth, xmlname))
            print(xmlname)
            AddToIndex(xmlname, f, tmppth)
            os.remove(os.path.join(tmppth, xmlname))

    f.close()

    # sort and uniquify the data
    linelist = [line.rstrip('\n') for line in open(idxfile, 'r')]
    linelist = sorted(set(linelist))
    with open(idxfile, 'w') as fout:
        fout.write('\n'.join(linelist))
        fout.write('\n')

    # send it back to S3
    s3.upload_file(Bucket=target, Key=tmpf, Filename=idxfile)
    return


def purgeOlderFiles(target):
    print('purging older bad data')
    s3 = boto3.client('s3')
    # get purge limit
    try:
        doff = int(os.environ['PURGE']) + 1
    except:
        doff = 22

    tod = datetime.datetime.today() - datetime.timedelta(days=doff)

    # find pertinent files
    for subfldr in ['/', '/badline/', '/fitfail/', '/flash/',
            '/nopaths/', '/noxml/', '/rmshigh/', '/toomany/', '/tooslow/']:
        fldr = 'live-bad-files' + subfldr
        pref = fldr + 'M{:04d}{:02d}{:02d}'.format(tod.year, tod.month, tod.day)
        flist = s3.list_objects_v2(Bucket=target, Prefix=pref)
        if 'Contents' not in flist:  # no matching files
            print('no matches', pref)
        else:
            for key in flist['Contents']:
                fname = key['Key']
                print('deleting', fname)
                s3.delete_object(Bucket=target, Key=fname)


def lambda_handler(event, context):
    livetarget = os.getenv('UKMONLIVEBUCKET', default='s3://ukmon-shared')[5:]
    archtarget = os.getenv('UKMONSHAREDBUCKET', default='s3://ukmda-shared')[5:]
    doff = int(os.getenv('OFFSET', default='1'))
    # update index for requested date and today
    print('DailyCheck: updating indexes')
    createIndex(livetarget, doff)
    createIndex(livetarget, doff - 1)

    purgeOlderFiles(archtarget)


if __name__ == '__main__':
    a = 1
    b = 2
    lambda_handler(a, b)
    exit()
