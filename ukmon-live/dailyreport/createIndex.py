# create an initial index file for the ukmon-live stream
#
import os
import datetime
import math
import boto3
# import numpy as np
import ReadUFOCapXML
# Polynomial = np.polynomial.Polynomial


def AddToIndex(fname, idxfile, pth):
    dd = ReadUFOCapXML.UCXml(os.path.join(pth, fname))
    pathx, pathy, bri, _ = dd.getPath()
    bri = max(bri)
    rms = 0  # not calculating this any more
#    if(len(pathx) > 3):
#        rms = 0
#        cmin, cmax = min(pathx), max(pathx)
#        _, stats = Polynomial.fit(pathx, pathy, 1, full=True, window=(cmin, cmax),
#            domain=(cmin, cmax))
#        resid, _, _, _ = stats
#        rms = np.sqrt(resid[0] / len(pathx))
#        if rms > 1:
#            cmin, cmax = min(pathy), max(pathy)
#            _, stats = Polynomial.fit(pathy, pathx, 1, full=True, window=(cmin, cmax),
#                domain=(cmin, cmax))
#            resid, _, _, _ = stats
#            rms2 = np.sqrt(resid[0] / len(pathy))
#            rms = min(rms2, rms)
#    else:
#        rms = 0
#        bri = 0

    dmy = fname[1:9]
    hms = fname[10:16]
    stat = fname[17:fname.rfind('.')]
    sid = stat[:stat.rfind('_')]
    if(sid == 'Lockyer2' or sid == 'Lockyer1'):
        sid = 'Lockyer'
    if(sid == 'Exeter2' or sid == 'EXETER1'):
        sid = 'Exeter'
    lid = stat[stat.rfind('_') + 1:]

    strtowrite = dmy + ',' + hms + ',' + sid + ',' + lid + ',{:.2f},{:.2f}\n'.format(bri, rms)
    idxfile.write(strtowrite)
    return


def createIndex(doff=1):
    client = boto3.client('sts')
    response = client.get_caller_identity()['Account']
    if response == '317976261112':
        target = 'mjmm-live'
    else:
        target = 'ukmon-live'

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


def lambda_handler(event, context):
    # get day offset to process
    try:
        offs = int(os.environ['OFFSET'])
    except:
        offs = 1

    createIndex(offs)


if __name__ == '__main__':
    a = 1
    b = 2
    lambda_handler(a, b)
    exit()
