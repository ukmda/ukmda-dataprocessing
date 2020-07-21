# UKMONLiveLineChecker.py
#
# python script to validate data before uploading to ukon live

# AWS python libraries
import boto3

import os, sys, fnmatch, subprocess, datetime
import ReadUFOCapXML
import numpy as np
Polynomial = np.polynomial.Polynomial
import configparser as cfg
import matplotlib.pyplot as plt

badfilepath=''

maxrms=1
interactive=False
movfiles=False

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

def syscmd(cmd, encoding=''):
    """
    Runs a command on the system, waits for the command to finish, and then
    returns the text output of the command. If the command produces no text
    output, the command's return code will be returned instead.
    """
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        close_fds=True)
    p.wait()
    output = p.stdout.read()
    if len(output) > 1:
        if encoding: return output.decode(encoding)
        else: return output
    return p.returncode

def ShowGraph(xmlname, pathx, pathy, A0=0, m=0, msg='', cx=720, cy=576):
    if interactive == False:
        return
    fity=np.empty(len(pathx))
    for i in range(len(pathx)):
        fity[i]=A0+m*pathx[i]
    plt.plot(pathx, pathy, pathx, fity)
    #plt.axis([min(pathx)-20, max(pathx)+20,min(pathy)-20,max(pathy)+20])
    plt.axis([0,cx,0,cy])
    plt.title(xmlname+'\n'+msg)
    plt.show()

def AddToRemoveList(fname, outf, errf, addtoerrf=0, movebad=False, msg='', yymmdd='999999'):
    l=len(fname)
    jpgname=fname[:l-4]+'*.*'
    if movebad==True:
        if sys.platform =='linux':
            _=syscmd('mv '+jpgname +' '+ badfilepath)
        else:
            _=syscmd('move '+jpgname +' '+ badfilepath)

    if yymmdd!='000000':
        _,fn=os.path.split(fname)
        if outf is not None: 
            outf.write('aws s3 rm s3://ukmon-live/'+fn+'\n')
        jpgn=fn[:len(fn)-4]+'P.jpg'
        if outf is not None: 
            outf.write('aws s3 rm s3://ukmon-live/'+jpgn+'\n')
    if addtoerrf ==1:
        _,fn=os.path.split(fname)
        errf.write(fn+ ',' + msg + '\n')

def CheckifValidMeteor(jpgname, outf, errf, goodf, ymd):
    # initialise fit variables
    dist=0
    app_m=0
    m=0
    ym=0
    xm=0
    vel=0
    rms=0

    xmlname = jpgname[:len(jpgname)-5]+".xml"
    _, fname=os.path.split(xmlname)
    if(os.path.isfile(xmlname) == False):
        msg='noxml, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(0, rms, xm, ym, m, app_m, dist, vel)
        print (fname, msg )
        AddToRemoveList(xmlname,outf, errf, 1, movfiles, msg, yymmdd=ymd)
        return

    dd=ReadUFOCapXML.UCXml(xmlname)
    fps, cx, cy = dd.getCameraDetails()
    pathx, pathy, _ = dd.getPath()

    # we expect meteor paths to be monotonic in X or Y or both
    # A path that darts about is unlikely to be analysable
    badline=False
    if  monotonic(pathx)==False and  monotonic(pathy) == False:
        badline=True

    # RMS ignores paths of less than 6 frames
    # lets try with 4 for now
    l=len(pathx)
    if l > 3 and badline == False:
        try:
            cmin, cmax = min(pathx), max(pathx)
            pfit, stats = Polynomial.fit(pathx, pathy, 1, full=True, window=(cmin, cmax),
                domain=(cmin, cmax))
            A0, m = pfit
            app_m = (pathy[-1]-pathy[0])/(pathx[-1]-pathx[0])
            resid, _, _, _ = stats
            rms = np.sqrt(resid[0]/len(pathx))
            # if the line is nearly vertical, a fit of y wil be a poor estimate
            # so before discarding the data, try swapping the axes
            if rms > maxrms:
                cmin, cmax = min(pathy), max(pathy)
                pfit, stats = Polynomial.fit(pathy, pathx, 1, full=True, window=(cmin, cmax),
                    domain=(cmin, cmax))
                A0, m = pfit
                resid, _, _, _ = stats
                rms = np.sqrt(resid[0]/len(pathy))
                app_m = (pathx[-1]-pathx[0])/(pathy[-1]-pathy[0])

            # work out the length of the line; very short lines are statistically unreliable
            p1=np.c_[pathx[0],pathy[0]]
            p2=np.c_[pathx[-1],pathy[-1]]
            dist=np.linalg.norm(p2-p1)
            vel=dist*2*fps/l

            # very low RMS is improbable but lets allow it for now
            if rms > maxrms :
                msg='plane, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel)
                print (fname, msg )
                AddToRemoveList(xmlname, outf, errf, 1, movfiles, msg, yymmdd=ymd)
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
                    print (fname, msg )
                    AddToRemoveList(xmlname, outf, errf, 1, movfiles, msg, yymmdd=ymd)
                    #ShowGraph(fname, pathx, pathy, A0, m, msg, cx, cy)
                    return
                msg='meteor, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel)
                print (fname, msg)
                goodf.write(fname +',' + msg +'\n')
                ShowGraph(fname, pathx,pathy, A0,m, msg, cx, cy)

        except:
            msg='fitfail, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel)
            print(fname, msg)
            AddToRemoveList(xmlname, outf, errf, 1, movfiles, msg, yymmdd=ymd)
            #ShowGraph(fname, pathx, pathy, 0, 0, msg, cx, cy)
    else:
        if badline==True:
            msg='badline, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(len(pathx), rms, int(xm), int(ym),m, app_m, dist, vel)
        else:
            msg='flash, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(len(pathx), rms, int(xm), int(ym),m, app_m, dist, vel)
        print(fname, msg)
        AddToRemoveList(xmlname, outf, errf, 1, movfiles, msg, yymmdd=ymd)
        #ShowGraph(fname, pathx, pathy, 0, 0, msg)


def SendToLive(xmlname):
    bucket='ukmon-live'
    AWS_ACCESS_KEY_ID = ''
    AWS_SECRET_ACCESS_KEY = ''
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
    s3 = session.resource('s3')
    inf=xmlname
    _, targf=os.path.split(xmlname)
    s3.meta.client.upload_file(Filename=inf, Bucket=bucket, Key=targf)

def ProcessADay(path, ymd, actionscript, badfilepath, logfilepath):
#    print(path, ymd)
    if actionscript is not None:
        outf=open(actionscript, 'a+')
        outf.write('#!/bin/bash\n')
    else:
        outf=None
    errf=open(os.path.join(logfilepath, 'bad.txt'),'a+')
    goodf=open(os.path.join(logfilepath, 'good.txt'),'a+')
    listOfFiles = os.listdir(path)
    listOfFiles.sort()
    pattern='M{:s}*P.jpg'.format(ymd)
    #print('checking {:s} {:d} files'.format(pattern, len(listOfFiles)))
    for entry in listOfFiles:
        if fnmatch.fnmatch(entry, pattern):
            x=entry.find('UK00')
            if x== -1 :
                CheckifValidMeteor(os.path.join(path, entry), outf, errf, goodf, ymd)
    if actionscript is not None:
        outf.close()
    errf.close()
    goodf.close()

if __name__ == '__main__':
    if len(sys.argv) ==1:
        print('usage:\n python curateUkmonLive.py live')
        print('or\n python curateUkmonLive.py CC yyyymmdd')
    else:
        if sys.argv[1]=='live':
            config=cfg.ConfigParser()
            pth, _ = os.path.split(os.path.realpath(__file__))
            cfgfile=os.path.join(pth, 'live.ini')
            print(cfgfile)
            config.read(cfgfile)
            path=config['live']['src']
            badfilepath=config['live']['bad']
            logfilepath=config['live']['log']
            actionscript=config['live']['actionscript']
            daystodo=int(config['live']['days'])
            maxrms=int(config['live']['maxrms'])
            if config['live']['interactive'] == 'Yes':
                interactive=True
            if config['live']['movefiles'] == 'Yes':
                movfiles=True

            try:
                os.remove(actionscript)
            except:
                pass
            print('Processing {:d} days; movefiles='.format(daystodo)+str(movfiles))
            if len(sys.argv) >2:
                ymd=sys.argv[2]
                ProcessADay(path, ymd, actionscript, badfilepath, logfilepath)   
            else:
                for i in range(0,daystodo+1):
                    dd=datetime.date.today()-datetime.timedelta(days=i)
                    ymd='{:04d}{:02d}{:02d}'.format(dd.year, dd.month, dd.day)
                    cmdstr='aws s3 cp s3://ukmon-live/ '+ path + ' --exclude "*" --include "M'+ymd+'*" --recursive'
                    #print(cmdstr)
                    os.system(cmdstr)
                    ProcessADay(path, ymd, actionscript, badfilepath, logfilepath)   
        else: 
            # args should be id yyyymmdd
            cloc=sys.argv[1]
            ymd=sys.argv[2]
            if valid_date(ymd) == True:
                infname='tackley_'+cloc+'.ini'
                config=cfg.ConfigParser()
                config.read(infname)
                srcpath=config['camera']['localfolder']
                badfilepath=config['cleaning']['badfolder']
                logfilepath=badfilepath
                maxrms=int(config['cleaning']['maxrms'])
                if config['cleaning']['movefiles'] == 'No':
                    movfiles=False
                else:
                    movfiles=True
                    
                yyyy=ymd[:4]
                yymm=ymd[:6]
                path=os.path.join(srcpath,yyyy,yymm,ymd)
                minmth=0
                minday=0
                actionscript=None 
                try:
                    os.mkdir(badfilepath)
                except:
                    pass
                print('Processing '+ymd+'; movefiles='+str(movfiles))
                ProcessADay(path, ymd, actionscript, badfilepath, logfilepath)
            else:
                print('Invalid date, must be YYYYMMDD')

