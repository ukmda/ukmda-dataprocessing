from fileformats.extractRawDataOneEvent import filterFTPforSpecificTime
from fileformats.ftpDetectInfo import loadFTPDetectInfo
import shutil
import filecmp

def test_filter():
    ftpfile = './testFilter/FTPdetectinfo_UK006S_20230112_170327_316507.txt'
    dtstr = '20230113_021451'
    print(dtstr, ftpfile)
    newname, nummets = filterFTPforSpecificTime(ftpfile, dtstr)
    assert(nummets == 1)


def test_reset():
    shutil.copy('./testFilter/FTPdetectinfo_UK006S_20230112_170327_316507.txt.old',
                './testFilter/FTPdetectinfo_UK006S_20230112_170327_316507.txt')
    assert(filecmp.cmp('./testFilter/FTPdetectinfo_UK006S_20230112_170327_316507.txt.old',
                './testFilter/FTPdetectinfo_UK006S_20230112_170327_316507.txt') is True)
    