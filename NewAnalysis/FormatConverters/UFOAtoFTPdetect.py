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
import UFOHandler.ReadUFOAnalyzerXML as UA

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
    listOfFiles = os.listdir(fldr)
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


def writeFTPHeader(ftpf, metcount, stime, fldr):
    """
    Create the header of the FTPDetect file
    """
    l1 = 'Meteor Count = {:06d}\n'.format(metcount)
    ftpf.write(l1)
    ftpf.write('-----------------------------------------------------\n')
    ftpf.write('Processed with UFOAnalyser\n')
    ftpf.write('-----------------------------------------------------\n')
    l1 = 'FF  folder = {:s}\n'.format(fldr)
    ftpf.write(l1)
    l1 = 'CAL folder = {:s}\n'.format(fldr)
    ftpf.write(l1)
    ftpf.write('-----------------------------------------------------\n')
    ftpf.write('FF  file processed\n')
    ftpf.write('CAL file processed\n')
    ftpf.write('Cam# Meteor# #Segments fps hnr mle bin Pix/fm Rho Phi\n')
    ftpf.write('Per segment:  Frame# Col Row RA Dec Azim Elev Inten Mag\n')


def writeOneMeteor(ftpf, metno, sta, evttime, fcount, fps, fno, ra, dec, az, alt, b, mag, lid):
    """
    Write one meteor event into the file in FTPDetectInfo style
    """
    ftpf.write('-------------------------------------------------------\n')
    ms = '{:03d}'.format(int(evttime.microsecond / 1000))
    lid = lid.replace('_', '')
    fname = 'FF_' + lid + '_' + evttime.strftime('%Y%m%d_%H%M%S_') + ms + '_0000000.fits\n'
    ftpf.write(fname)
    ftpf.write('UFO FRIPON DATA recalibrated on: ')
    ftpf.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f UTC\n'))
    li = sta + ' 0001 {:04d} {:04.2f} '.format(fcount, fps) + '000.0 000.0  00.0 000.0 0000.0 0000.0\n'
    ftpf.write(li)
    for i in range(len(fno)):
        #    204.4909 0422.57 0353.46 262.3574 +16.6355 267.7148 +23.0996 000120 3.41
        li = '{:08.4f} {:07.2f} {:07.2f} '.format(fno[i] - fno[0], 0, 0)  # UFO is timestamped as at the first detection
        li += '{:s} {:s} {:s} {:s} '.format('{:.4f}'.format(ra[i]).zfill(8),
            '{:+.4f}'.format(dec[i]).zfill(8),
            '{:.4f}'.format(az[i]).zfill(8),
            '{:+.4f}'.format(alt[i]).zfill(8))
        li += '{:06d} {:.2f}\n'.format(int(b[i]), mag[i])
        ftpf.write(li)


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
    Read all the A.XML files and create an RMS-style ftpdetect file plus station info file
    Then check for RMS-style data and append it onto the files
    """
    axmls, metcount, stime = loadAXMLs(fldr)

    # create an empty station info file
    createStationHeader(fldr)

    # create and populate the ftpdetectinfo file
    ftpfile = os.path.join(fldr, FTPFILE)
    with open(ftpfile, 'w') as ftpf:
        writeFTPHeader(ftpf, metcount, stime, fldr)
        metno = 1
        for thisxml in axmls:
            evttime = thisxml.getDateTime()
            sta, lid, sid, lat, lng, alt = thisxml.getStationDetails()
            fps, cx, cy, isintl = thisxml.getCameraDetails()
            createStationInfo(fldr, sta, lat, lng, alt)
            if isintl == 1:
                fps *= 2
            numobjs = thisxml.getObjectCount()
            # print(evttime, sta, lid, sid, numobjs)

            for i in range(numobjs):
                fno, tt, ra, dec, mag, fcount, alt, az, b, lsum = thisxml.getPathVector(i)
                metno += 1
                writeOneMeteor(ftpf, metno, sta, evttime, fcount, fps, fno, ra, dec, az, alt, b, mag, lid)
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


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage python UFOtoFTPdetect.py somefolder')
        print('  will convert all UFO A.xml files in somefolder to a single FTPDetectInfo file')
    else:
        convertFolder(sys.argv[1])
