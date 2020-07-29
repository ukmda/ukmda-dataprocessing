import os, sys
import curateCamera as cc
import configparser as cfg
import ReadUFOCapXML

if __name__ == '__main__':
    path = sys.argv[1]

    config=cfg.ConfigParser()
    config.read('testing.ini')
    cc.badfilepath=config['cleaning']['badfolder']
    logfilepath=cc.badfilepath
    if config['cleaning']['movefiles'] in ['True', 'TRUE','true']:
        cc.movfiles=True
    else:
        cc.movfiles=False

    cc.maxrms=1
    cc.debug = False
    print('Processing '+path+'; cc.movefiles='+str(cc.movfiles))
#    xmlname='c:/users/mark/videos/astro/meteorcam/livebad/maybe/M20200429_002513_Bideford_SE.xml'
#    dd=ReadUFOCapXML.UCXml(xmlname)
#    nobjs, objlist = dd.getNumObjs()
#    for i in range(nobjs):
#        pathx,pathy,bri = dd.getPathv2(objlist[i])
#        print (pathx,pathy)

    cc.ProcessADay(path, '*', cc.badfilepath, logfilepath)
