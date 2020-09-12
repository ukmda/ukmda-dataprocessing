import os, sys
import curateCamera as cc
import configparser as cfg
import ReadUFOCapXML

if __name__ == '__main__':
    path = sys.argv[1]
    config=cfg.ConfigParser()

    # if the argument is an ini file, read from it.
    # otherwise look for a file testing.ini in the target folder
    if path[-4:]=='.ini':
        cfgfile=path
        config.read(cfgfile)
        path=config['camera']['localfolder']
    else:
        cfgfile=os.path.join(path, 'testing.ini')
        config.read(cfgfile)

    cc.badfilepath=config['cleaning']['badfolder']
    logfilepath=cc.badfilepath
    cc.MAXRMS=float(config['cleaning']['maxrms'])
    cc.MINLEN=int(config['cleaning']['minlen'])
    cc.MAXLEN=int(config['cleaning']['maxlen'])
    cc.MAXOBJS=int(config['cleaning']['maxobjs'])
    print(config['cleaning']['debug'])
    if config['cleaning']['debug'] in ['True', 'TRUE','true']:
        cc.debug=True
    else:
        cc.debug=False
    if config['cleaning']['movefiles'] in ['True', 'TRUE','true']:
        cc.movfiles=True
    else:
        cc.movfiles=False

#    cc.maxrms=1
#    cc.debug = False
    print('Processing '+path+'; cc.movefiles='+str(cc.movfiles))
    print( cc.MAXOBJS,    cc.MAXRMS,     cc.MINLEN, cc.debug) 

    cc.ProcessADay(path, '*', cc.badfilepath, logfilepath)
