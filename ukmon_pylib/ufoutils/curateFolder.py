# Copyright (C) 2018-2023 Mark McIntyre

#
# Python script to curate a named folder
#

import os
import sys
import configparser as cfg

from ufoutils import curateCamera as cc
from ufoutils import curateEngine as ce


def main(path, altfolder=None, badfolder=None):
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

    # we can override the ini file by passing in an alternate folder
    if altfolder is not None:
        path = altfolder
    if badfolder is not None:
        cc.badfilepath = badfolder

    logfilepath = cc.badfilepath
    ce.MAXRMS = float(config['cleaning']['maxrms'])
    ce.MINLEN = int(config['cleaning']['minlen'])
    ce.MAXLEN = int(config['cleaning']['maxlen'])
    ce.MAXBRI = int(config['cleaning']['maxbri'])
    ce.MAXOBJS = int(config['cleaning']['maxobjs'])
    if config['cleaning']['debug'] in ['True', 'TRUE', 'true']:
        ce.debug = True
    else:
        ce.debug = False
    if config['cleaning']['movefiles'] in ['True', 'TRUE', 'true']:
        movfiles = True
    else:
        movfiles = False

    if config['cleaning']['useSubfolders'] in ['True', 'TRUE', 'true']:
        useSubfolders = True
    else:
        useSubfolders = False

    print('Processing ' + path + '; cc.movefiles=' + str(movfiles))

    cc.ProcessADay(path, '*', cc.badfilepath, logfilepath, movfiles, useSubfolders)


if __name__ == '__main__':
    main(sys.argv[1])
