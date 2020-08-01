import os, sys
import curateCamera as cc
import configparser as cfg
import ReadUFOCapXML

if __name__ == '__main__':
    path = sys.argv[1]

    config=cfg.ConfigParser()
    cfgfile=os.path.join(path, 'testing.ini')
    config.read(cfgfile)
    cc.badfilepath=config['cleaning']['badfolder']
    logfilepath=cc.badfilepath
    cc.MAXRMS=float(config['cleaning']['maxrms'])
    cc.MINLEN=int(config['cleaning']['minlen'])
    cc.MAXLEN=int(config['cleaning']['maxlen'])
    cc.MAXOBJS=int(config['cleaning']['maxobjs'])
    if config['cleaning']['movefiles'] in ['True', 'TRUE','true']:
        cc.movfiles=True
    else:
        cc.movfiles=False

    cc.maxrms=1
    cc.debug = False
    print('Processing '+path+'; cc.movefiles='+str(cc.movfiles))
    print( cc.MAXOBJS,    cc.MAXRMS,     cc.MINLEN) 

    cc.ProcessADay(path, '*', cc.badfilepath, logfilepath)
