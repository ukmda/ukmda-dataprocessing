#
# python module to find and copy the JPG files if we have 'em
#

import os
import sys
import shutil
import fnmatch
import datetime
import fileformats.CameraDetails as cdet


def getListOfFiles(fldr, cams, camfldrs, srcpth):
    """
    get the names of the A.XML files and hence the list of JPGs
    """
    jpgs = []
    fullpaths = []
    listOfFiles = os.listdir(fldr)
    # initialise the values
    yr, ym, ymd = '2020', '202001', '20200101'
    for entry in listOfFiles:
        if fnmatch.fnmatch(entry, '*A.XML'):
            basenam = entry[: len(entry) - 5]
            jpgname = basenam + 'P.jpg'
            jpgs.append(jpgname)

            bits = basenam.split('_')
            ymd = bits[0]
            yr = ymd[1:5]
            ym = ymd[1:7]
            ymd = ymd[1:]
            loccam = bits[2] + '_'
            if len(bits) == 4:
                loccam = loccam + bits[3]
            try:
                idx = cams.index(loccam)
            except:
                idx = 0
            pth = os.path.join(srcpth, camfldrs[idx])
            fullpaths.append(pth)
    return jpgs, fullpaths, yr, ym, ymd


def collectJPGS(afldr, targpath):
    srcpath = '/home/ec2-user/ukmon-shared/archive'

    cinfo = cdet.SiteInfo()
    cams, camfldrs = cinfo.getAllCamsAndFolders()
    
    jpgs, fullpaths, yr, ym, ymd = getListOfFiles(afldr, cams, camfldrs, srcpath)
    for fil, pth in zip(jpgs, fullpaths):
        print(pth, fil)
        fname = os.path.join(pth, yr, ym, ymd, fil)
        try:
            # print('trying', fname)
            shutil.copy(fname, targpath)
            msg = 'copied ' + fname + ' to ' + targpath
            print(msg)
        except:
            try:
                d = datetime.datetime.strptime(ymd, '%Y%m%d')
                d -= datetime.timedelta(days=1)
                yr2 = d.strftime('%Y')
                ym2 = d.strftime('%Y%m')
                ymd2 = d.strftime('%Y%m%d')
                fname = os.path.join(pth, yr2, ym2, ymd2, fil)
                shutil.copy(fname, targpath)
                msg = 'copied ' + fname + ' to ' + targpath
                print(msg)
            except:
                print(fil, ' not found')


if __name__ == "__main__":
    collectJPGS(sys.argv[1], sys.argv[2])
