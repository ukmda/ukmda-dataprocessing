# UKMONLiveLineChecker.py
#
# python script to validate data before uploading to ukon live

import os, sys
import fnmatch
import datetime
import shutil, glob
import ReadUFOCapXML
import numpy as np
Polynomial = np.polynomial.Polynomial
import configparser as cfg
#import matplotlib.pyplot as plt

badfilepath=''
maxrms=1
interactive=False
movfiles=False
debug=False

def valid_date(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    if len(s) ==8:
        return True
    return False

def monotonic(x):
    dx = np.diff(x)
    return np.all(dx <= 0) or np.all(dx >= 0)

#def ShowGraph(xmlname, pathx, pathy, A0=0, m=0, msg='', cx=720, cy=576):
#    if interactive == False:
#        return
#    fity=np.empty(len(pathx))
#    for i in range(len(pathx)):
#        fity[i]=A0+m*pathx[i]
#    plt.plot(pathx, pathy, pathx, fity)
#    #plt.axis([min(pathx)-20, max(pathx)+20,min(pathy)-20,max(pathy)+20])
#    plt.axis([0,cx,0,cy])
#    plt.title(xmlname+'\n'+msg)
#    plt.show()

def AddToRemoveList(fname, errf, movebad=False, msg='', nobjs=0,maxbri=0):
    _,fn=os.path.split(fname)
    l=len(fn)
    jpgname=fn[:l-4]+'*'
    l=len(fname)
    allf=fname[:l-4]+'*'
    if movebad==True:
        for fl in glob.glob(allf):
            shutil.move(fl, badfilepath)
    else:
        pass
        #print('would have moved {:s} to {:s}'.format(jpgname, os.path.join(badfilepath, jpgname)))
    msg = msg + ',{:d},{:d}'.format(nobjs, int(maxbri))
    print(fn+ ',' +msg)
    if errf is not None :
        errf.write(fn+ ',' + msg + '\n')

def CheckifValidMeteor(jpgname, errf, goodf):

    xmlname = jpgname[:len(jpgname)-5]+".xml"
    if(os.path.isfile(xmlname) == False):
        msg='noxml, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(0, 0, 0, 0, 0, 0, 0, 0)
        AddToRemoveList(xmlname, errf, movfiles, msg, 0, 0)
        return False

    dd=ReadUFOCapXML.UCXml(xmlname)
    fps, cx, cy = dd.getCameraDetails()
    nobjs, objlist = dd.getNumObjs()
    #print(nobjs, objlist)
    isgood=0
    if nobjs==0:
        msg='nopaths, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(0, 0, 0, 0, 0, 0, 0, 0)
        AddToRemoveList(xmlname, errf, movfiles, msg, 0, 0)
        return False
    goodmsg=''
    _,fn=os.path.split(xmlname)
    for i in range(nobjs):
        pathx, pathy, bri = dd.getPathv2(objlist[i])
        res, msg= CheckALine(pathx, pathy, xmlname, errf, goodf, fps, cx, cy)
        print (msg)
        if res==1:
            goodmsg = msg
        isgood = isgood + res
        
    if isgood == 0:    
        AddToRemoveList(xmlname, errf, movfiles, msg, nobjs, max(bri))
        return False
    else:
        goodmsg = goodmsg + ',{:d}, {:d}'.format(nobjs, int(max(bri)))
        goodf.write(fn +',' + goodmsg +'\n')
        print(fn +',' + goodmsg)
        return True    

def leastsq1(x, y):
    a = np.vstack([x, np.ones(len(x))]).T
    return np.dot(np.linalg.inv(np.dot(a.T, a)), np.dot(a.T, y))
    
def CheckALine(pathx, pathy, xmlname, errf, goodf, fps, cx, cy):
    dist=0
    app_m=0
    m=0
    ym=0
    xm=0
    vel=0
    rms=0

    # we expect meteor paths to be monotonic in X or Y or both
    # A path that darts about is unlikely to be analysable
    badline=False
    if  monotonic(pathx)==False and  monotonic(pathy) == False:
        if debug==True:
            print (pathx, pathy)
        badline=True

    # RMS ignores paths of less than 6 frames
    # lets try with 4 for now
    l=len(pathx)
    if l > 4 and badline == False:
        try:
            cmin, cmax = min(pathx), max(pathx)
            pfit, stats = Polynomial.fit(pathx, pathy, 1, full=True, window=(cmin, cmax),
                domain=(cmin, cmax))
            _, m = pfit
            if (pathx[-1]-pathx[0]) !=0:
                app_m = (pathy[-1]-pathy[0])/(pathx[-1]-pathx[0])
            resid, _, _, _ = stats
            rms = np.sqrt(resid[0]/len(pathx))

            # if the line is nearly vertical, a fit of y wil be a poor estimate
            # so before discarding the data, try swapping the axes
            if rms > maxrms:
                cmin, cmax = min(pathy), max(pathy)
                pfit, stats = Polynomial.fit(pathy, pathx, 1, full=True, window=(cmin, cmax),
                    domain=(cmin, cmax))
                _, m = pfit
                resid, _, _, _ = stats
                rms2 = np.sqrt(resid[0]/len(pathy))
                if (pathy[-1]-pathy[0]) != 0:
                    app_m = (pathx[-1]-pathx[0])/(pathy[-1]-pathy[0])
                rms2 = min(rms2, rms)
                rms = min(rms2,rms)
        except:
            msg='fitfail, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel)
            return 0, msg

        # work out the length of the line; very short lines are statistically unreliable
        p1=np.c_[pathx[0],pathy[0]]
        p2=np.c_[pathx[-1],pathy[-1]]
        dist=np.linalg.norm(p2-p1)
        vel=dist*2*fps/l
        # very low RMS is improbable but lets allow it for now
        if rms > maxrms :
            msg='plane, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel)
            return 0, msg
            #ShowGraph(fname, pathx, pathy, A0, m, msg)
        else:
            xm = int(max(pathx))
            if xm > cx/2:
                xm = int(min(pathx))
            ym = int(min(pathy))
            if ym > cy/2:
                ym = int(min(pathy))
            if dist < 5 :
                msg='flash, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel)
                return 0, msg
                #ShowGraph(fname, pathx, pathy, A0, m, msg, cx, cy)
            else:
                msg='meteor, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel)
                return 1, msg
            #ShowGraph(fname, pathx,pathy, A0,m, msg, cx, cy)
    else:
        if badline==True:
            msg='badline, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(len(pathx), rms, int(xm), int(ym),m, app_m, dist, vel)
        else:
            msg='flash, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(len(pathx), rms, int(xm), int(ym),m, app_m, dist, vel)
        return 0, msg
        #ShowGraph(fname, pathx, pathy, 0, 0, msg)
    msg='flash, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(len(pathx), 0,0,0,0,0,0,0)
    return 0, msg

def ProcessADay(path, ymd, badfilepath, logfilepath):
    try: 
        listOfFiles = os.listdir(path)
    except:
        print('nothing to analyse')
        return 
    listOfFiles.sort()
    pattern='M{:s}*P.jpg'.format(ymd)
    errf=open(os.path.join(logfilepath, 'bad.txt'),'a+')
    goodf=open(os.path.join(logfilepath, 'good.txt'),'a+')
    for entry in listOfFiles:
        if fnmatch.fnmatch(entry, pattern):
            x=entry.find('UK00')
            if x== -1 :
                CheckifValidMeteor(os.path.join(path, entry), errf, goodf)
    errf.close()
    goodf.close()
    return

if __name__ == '__main__':
    if len(sys.argv) <3:
        print('\nusage: python curateCamera.py camera_name yyyymmdd')
        print('eg python curateCamera.py tackley_tc 20200712')
        print('Reads config from an inifile -read example inifile for more info\n')
    else: 
        # args should be id yyyymmdd
        cloc=sys.argv[1]
        ymd=sys.argv[2]
        if valid_date(ymd) == True:
            infname=cloc+'.ini'
            config=cfg.ConfigParser()
            config.read(infname)
            srcpath=config['camera']['localfolder']
            badfilepath=config['cleaning']['badfolder']
            logfilepath=badfilepath
            maxrms=int(config['cleaning']['maxrms'])
            if config['cleaning']['debug'] in ['True', 'TRUE','true']:
                debug=True
            else:
                debug=False
            if config['cleaning']['movefiles'] in ['True', 'TRUE','true']:
                movfiles=True
            else:
                movfiles=False
                
            yyyy=ymd[:4]
            yymm=ymd[:6]
            path=os.path.join(srcpath,yyyy,yymm,ymd)
            try:
                os.mkdir(badfilepath)
            except:
                pass
            try:
                os.mkdir(logfilepath)
            except:
                pass
            print('Processing '+ymd+'; movefiles='+str(movfiles))
            ProcessADay(path, ymd, badfilepath, logfilepath)
        else:
            print('Invalid date, must be YYYYMMDD')

