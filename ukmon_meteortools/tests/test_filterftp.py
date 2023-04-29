from ukmon_meteortools.fileformats.ftpDetectInfo import filterFTPforSpecificTime

import shutil
import filecmp
import os

here = os.path.split(os.path.abspath(__file__))[0]


def test_filterFTPforSpecificTime():
    srcftpfile = os.path.join(here, 'data', 'FTPdetectinfo_UK006S_20230112_170327_316507.txt.orig')
    ftpfile = os.path.join(here, 'data', 'FTPdetectinfo_UK006S_20230112_170327_316507.txt')
    oldftpfile = os.path.join(here, 'data', 'FTPdetectinfo_UK006S_20230112_170327_316507.txt.old')
    shutil.copy(srcftpfile, ftpfile)
    dtstr = '20230112_210240'
    newname, nummets = filterFTPforSpecificTime(ftpfile, dtstr)
    print(newname)
    assert nummets == 1
    assert filecmp.cmp(oldftpfile, srcftpfile) is True
    lis = open(newname, 'r').readlines()
    assert lis[0] == 'Meteor Count = 000001\n'
    os.remove(ftpfile)
    os.remove(oldftpfile)
    os.remove(newname)
    