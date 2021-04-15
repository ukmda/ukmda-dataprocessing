#
# Python script to curate a named folder
#

import os
import configparser as cfg

from CameraCurator import curateCamera as cc
from CameraCurator import curateEngine as ce


def main(config_file, path, badfolder=None, log=None):

    config = cfg.ConfigParser()
    config.read(config_file)
        
    if badfolder is not None:
        cc.badfilepath = badfolder
        os.makedirs(badfolder, exist_ok=True)

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

    if log is not None:
        log.info('Processing ' + path + '; cc.movefiles=' + str(movfiles))
    cc.ProcessADay(path, '*', cc.badfilepath, logfilepath, movfiles, useSubfolders, log)
