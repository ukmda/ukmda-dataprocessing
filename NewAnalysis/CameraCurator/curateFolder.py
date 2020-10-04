#
# Python script to curate a named folder
#

import os
import sys
import configparser as cfg

from CameraCurator import curateCamera as cc
from CameraCurator import curateEngine as ce


def main(path):
    config = cfg.ConfigParser()

    # if the argument is an ini file, read from it.
    # otherwise look for a file testing.ini in the target folder
    if path[-4:] == '.ini':
        cfgfile = path
        config.read(cfgfile)
        path = config['camera']['localfolder']
    else:
        cfgfile = os.path.join(path, 'testing.ini')
        config.read(cfgfile)

    cc.badfilepath = config['cleaning']['badfolder']
    logfilepath = cc.badfilepath
    ce.MAXRMS = float(config['cleaning']['maxrms'])
    ce.MINLEN = int(config['cleaning']['minlen'])
    ce.MAXLEN = int(config['cleaning']['maxlen'])
    ce.MAXBRI = int(config['cleaning']['maxbri'])
    ce.MAXOBJS = int(config['cleaning']['maxobjs'])
    print(config['cleaning']['debug'])
    if config['cleaning']['debug'] in ['True', 'TRUE', 'true']:
        ce.debug = True
    else:
        ce.debug = False
    if config['cleaning']['movefiles'] in ['True', 'TRUE', 'true']:
        cc.movfiles = True
    else:
        cc.movfiles = False

    if config['cleaning']['useSubfolders'] in ['True', 'TRUE', 'true']:
        cc.useSubfolders = True
    else:
        cc.useSubfolders = False

    print('Processing ' + path + '; cc.movefiles=' + str(cc.movfiles))

    cc.ProcessADay(path, '*', cc.badfilepath, logfilepath)


if __name__ == '__main__':
    main(sys.argv[1])
