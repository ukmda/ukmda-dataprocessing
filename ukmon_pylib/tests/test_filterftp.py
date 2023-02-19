from fileformats.extractRawDataOneEvent import filterFTPforSpecificTime

def test_filter():
    ftpfile = './testFilter/FTPdetectinfo_UK006S_20230112_170327_316507.txt'
    dtstr = '20230113_021451'
    print(dtstr, ftpfile)
    x = filterFTPforSpecificTime(ftpfile, dtstr)
    assert(x < 3)


