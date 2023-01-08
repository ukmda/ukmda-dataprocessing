#
# Python module to convert UFO data to RMS format
#
# Usage: python UFOAtoFTPdetect myfolder
#   will create an ftpdetect and stationinfo file for every A.xml file in "myfolder"
#

import os
import sys
import shutil
import fnmatch
import datetime
import boto3
import tempfile
from fileformats import ReadUFOAnalyzerXML as UA
from fileformats import CameraDetails as cdet
from fileformats.ftpDetectInfo import writeFTPHeader, writeOneMeteor

CAMINFOFILE = 'CameraSites.txt'
CAMOFFSETSFILE = 'CameraTimeOffsets.txt'
FTPFILE = 'FTPdetectinfo_UFO.txt'


def loadRMSdata(fldr):
    rmsdata = []
    stations = []
    listOfFiles = os.listdir(fldr)
    for entry in listOfFiles:
        if fnmatch.fnmatch(entry, 'data*.txt'):
            fullname = os.path.join(fldr, entry)
            rmsdata.append(fullname)
        if fnmatch.fnmatch(entry, 'stat*.txt'):
            fullname = os.path.join(fldr, entry)
            stations.append(fullname)
    return rmsdata, stations


def loadAXMLs(fldr):
    """
    Load all the A.xml files in the given folder
    """
    axmls = []
    try:
        listOfFiles = os.listdir(fldr)
    except Exception:
        print('not a folder')
        return axmls, 0, 0
    pattern = '*A.XML'
    metcount = 0
    evttime = datetime.datetime.now()
    for entry in listOfFiles:
        if fnmatch.fnmatch(entry, pattern):
            fullname = os.path.join(fldr, entry)
            xmlf = UA.UAXml(fullname)
            axmls.append(xmlf)
            metcount += xmlf.getObjectCount()
            evttime = xmlf.getDateTime()
    return axmls, metcount, evttime


def createStationHeader(fldr):
    statinfo = os.path.join(fldr, CAMINFOFILE)
    statf = open(statinfo, 'w')
    statf.write('# CAMS compatible station info file\n')
    statf.write('# station_id, lat(+N degs), long (+W degs), Altitude (km)\n')
    statf.close()


def createStationInfo(fldr, sta, lat, lng, alt):
    """
    Create CAMS style station info file. For some reason CAMS uses km as the altitude.
    Lati and Longi are in degrees, North positive but WEST positive so not standard
    """
    statinfo = os.path.join(fldr, CAMINFOFILE)
    # sta = sta.replace('_', '')
    with open(statinfo, 'a') as statf:
        dets = '{:s} {:.4f} {:.4f} {:.3f}\n'.format(sta, lat, -lng, alt / 1000.0)
        statf.write(dets)


def convertFolder(fldr):
    """
    Read all the A.XML files and create an RMS ftpdetect file plus station info file
    Then check for any RMS data and append it onto the files
    """
    axmls, metcount, stime = loadAXMLs(fldr)

    # create an empty station info file
    createStationHeader(fldr)

    # create and populate the ftpdetectinfo file
    ftpfile = os.path.join(fldr, FTPFILE)
    with open(ftpfile, 'w') as ftpf:
        writeFTPHeader(ftpf, metcount, fldr)
        metno = 1
        for thisxml in axmls:
            evttime = thisxml.getDateTime()
            sta, lid, sid, lat, lng, alt = thisxml.getStationDetails()
            fps, cx, cy, isintl = thisxml.getCameraDetails()
            lid = lid + sid
            lid = lid.replace('_','')
            createStationInfo(fldr, sta, lat, lng, alt)
            if isintl == 1:
                fps *= 2
            numobjs = thisxml.getObjectCount()
            # print(evttime, sta, lid, sid, numobjs)

            for i in range(numobjs):
                fno, tt, ra, dec, mag, fcount, alt, az, b, lsum = thisxml.getPathVector(i)
                metno = 1
                writeOneMeteor(ftpf, metno, sta, evttime, fcount, fps, fno, ra, dec, az, alt, b, mag)
                # print(fno, tt, ra, dec, alt, az, b, mag)

    rmsdata, statfiles = loadRMSdata(fldr)
    with open(os.path.join(fldr, FTPFILE), 'a') as wfd:
        for f in rmsdata:
            print(os.path.basename(f))
            with open(f, 'r') as fd:
                shutil.copyfileobj(fd, wfd)
    with open(os.path.join(fldr, CAMINFOFILE), 'a') as wfd:
        for f in statfiles:
            with open(f, 'r') as fd:
                shutil.copyfileobj(fd, wfd)
                wfd.write('\n')

    return


def convertUFOFolder(fldr, outfldr, statid=None, ymd=None):
    """
    Read all the A.XML files and create an RMS ftpdetect file and platepars file
    """
    print('reading from', fldr)
    axmls, metcount, stime = loadAXMLs(fldr)
    if len(axmls) == 0:
        print('no a.xml files found')
        return 

    if ymd is None:
        _, ymd = os.path.split(fldr)

    _, lid, sid, lat, lon, elev = axmls[0].getStationDetails()
    if lid == 'Blackfield' and sid == '':
        sid = 'c1'

    if statid is None:
        ci = cdet.SiteInfo()
        statid = ci.getDummyCode(lid, sid)
        if statid == 'Unknown':
            statid = 'XX9999'

    arcdir = statid + '_' + ymd + '_180000_000000'
    ftpfile = 'FTPdetectinfo_' + arcdir + '.txt'

    if statid is None:
        fulloutfldr = os.path.join(outfldr,statid, arcdir)
        print('writing to', fulloutfldr)
        os.makedirs(fulloutfldr, exist_ok=True)
    else:
        fulloutfldr = outfldr

    ppfname = os.path.join(fulloutfldr, 'platepars_all_recalibrated.json')
    plateparfile = open(ppfname, 'w')
    plateparfile.write('{\n')

    # create and populate the ftpdetectinfo file
    ftpfile = os.path.join(fulloutfldr, ftpfile)
    #print(f'writing to {ppfname} and {ftpfile}')
    with open(ftpfile, 'w') as ftpf:
        writeFTPHeader(ftpf, metcount, fldr)
        entrycount = 1
        metno = 1
        for thisxml in axmls:
            if entrycount > 1: 
                plateparfile.write(',\n')
            evttime = thisxml.getDateTime()
            fps, cx, cy, isintl = thisxml.getCameraDetails()
            if isintl == 1:
                fps *= 2
            numobjs = thisxml.getObjectCount()

            for i in range(numobjs):
                fno, tt, ra, dec, mag, fcount, alt, az, b, lsum = thisxml.getPathVector(i)
                metno = 1
                writeOneMeteor(ftpf, metno, statid, evttime, fcount, fps, fno, ra, dec, az, alt, b, mag)
            entrycount += 1
            pp = thisxml.makePlateParEntry(statid)
            plateparfile.write(pp)

    plateparfile.write('\n}\n')
    plateparfile.close()
    createConfigFile(fulloutfldr, statid, lat, lon, elev)
    return


def createConfigFile(pth, statid, lat, lon, elev):
    cfgfile = os.path.join(pth, '.config')
    with open(cfgfile, 'w') as outf:
        outf.write('; this_is_a_dummy_config_file_for_ftptoukmon\n')
        outf.write(f'StationID: {statid}\n')
        outf.write(f'latitude: {lat}\n')
        outf.write(f'longitude: {lon}\n')
        outf.write(f'elevation: {elev}\n')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage python UFOtoFTPdetect.py srcfolder targfolder')
        print('  will convert all UFO A.xml files in srcfolder to a single FTPDetectInfo file in targfolder')
        print('Usage python UFOtoFTPdetect.py yyyymmdd numdays')
        print('  will convert all UFO data for all UFO cameras for the given date range')
    else:
        try:
            print('its a range')
            s3 = boto3.resource('s3')
            start_dt = sys.argv[1]
            if len(sys.argv) > 2:
                numdays = int(sys.argv[2])
            else:
                numdays = 1
            start_ymd = datetime.datetime.strptime(start_dt, '%Y%m%d')
            start_yr = start_ymd.year
            start_ym = start_ymd.strftime('%Y%m')

            archbucket = os.getenv('UKMONSHAREDBUCKET', default='s3://ukmon-shared')
            if archbucket[:5] == 's3://':
                archbucket = archbucket[5:]
            outroot = 'matches/RMSCorrelate'
            ci = cdet.SiteInfo()
            ufos = ci.getUFOCameras(True)

            for dd in range(0, numdays):
                thisdt = start_ymd + datetime.timedelta(days=dd)
                yr = thisdt.year
                ym = thisdt.strftime('%Y%m')
                yd = thisdt.strftime('%Y%m%d')
                print(yr, ym, yd)
                for cam in ufos:
                    tmpdir = tempfile.mkdtemp()
                    site = cam['Site']
                    camid = cam['CamID']
                    dum = cam['dummycode']
                    thispth = 'archive/{}/{}/{}/{}/{}/'.format(site, camid, yr, ym, yd)
                    print(thispth)
                    objlist = s3.meta.client.list_objects_v2(Bucket=archbucket,Prefix=thispth)
                    if objlist['KeyCount'] > 0:
                        keys = objlist['Contents']
                        for k in keys:
                            fname = k['Key']
                            if 'A.XML' in fname:
                                _, fn = os.path.split(fname)
                                locfname = os.path.join(tmpdir, fn)
                                s3.meta.client.download_file(archbucket, fname, locfname)
                    while objlist['IsTruncated'] is True:
                        contToken = objlist['NextContinuationToken'] 
                        objlist = s3.meta.client.list_objects_v2(Bucket=archbucket,Prefix=thispth, ContinuationToken=contToken)
                        if objlist['KeyCount'] > 0:
                            keys = objlist['Contents']
                            for k in keys:
                                fname = k['Key']
                                if 'A.XML' in fname:
                                    _, fn = os.path.split(fname)
                                    locfname = os.path.join(tmpdir, fn)
                                    s3.meta.client.download_file(archbucket, fname, locfname)

                    convertUFOFolder(tmpdir, tmpdir, dum, yd)
                    arcdir = dum + '_' + yd + '_180000_000000'
                    ftpfile = 'FTPdetectinfo_' + arcdir + '.txt'

                    if os.path.isfile(os.path.join(tmpdir, 'platepars_all_recalibrated.json')):
                        idxname = os.path.join(tmpdir, '.config')
                        key = f'{outroot}/{dum}/{arcdir}/.config'
                        extraargs = {'ContentType': 'text/plain'}
                        print(f'uploading {key}')
                        s3.meta.client.upload_file(idxname, archbucket, key, ExtraArgs=extraargs) 

                        idxname = os.path.join(tmpdir, 'platepars_all_recalibrated.json')
                        key = f'{outroot}/{dum}/{arcdir}/platepars_all_recalibrated.json'
                        extraargs = {'ContentType': 'application/json'}
                        print(f'uploading {key}')
                        s3.meta.client.upload_file(idxname, archbucket, key, ExtraArgs=extraargs) 

                        idxname = os.path.join(tmpdir, ftpfile)
                        key = f'{outroot}/{dum}/{arcdir}/{ftpfile}'
                        print(f'uploading {key}')
                        extraargs = {'ContentType': 'text/plain'}
                        s3.meta.client.upload_file(idxname, archbucket, key, ExtraArgs=extraargs) 
                    shutil.rmtree(tmpdir)

        except:
            print('its a folder')
            convertUFOFolder(sys.argv[1], sys.argv[2])
