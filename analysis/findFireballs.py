#
# python script to find fireballs amongst the UFO data and copy the data to the fireballs folder
#
import os, sys

import configparser as cfg
import ReadUFOAnalyzerXML
import fnmatch
import datetime
import shutil, glob

def copyFiles(srcpath, fname, destpath):
    fldrname=fname[:16]
    fldrname=os.path.join(destpath, fldrname)
    try:
        os.mkdir(fldrname)
    except:
        pass

    l=len(fname)
    allf=os.path.join(srcpath, fname[:l-5]+'*')
    for fl in glob.glob(allf):
        shutil.copy(fl, fldrname)
    return

def CheckIfFireball(srcpath, fname, destpath):
    xmlname = fname[:len(fname)-5]+'A.xml'  
    xmlname=os.path.join(srcpath, xmlname)
    dd=ReadUFOAnalyzerXML.UAXml(xmlname)
    nobjs = dd.getObjectCount()
    for objno in range(nobjs):
        _, _, _, _, mag, fcount = dd.getObjectBasics(objno)
        if mag < -3.99 :
            print(fname, mag, fcount)
            copyFiles(srcpath, fname, destpath)
    return 


def ProcessADay(srcpath, destpath):
    try: 
        listOfFiles = os.listdir(srcpath)
    except:
        print('nothing to analyse')
        return 
    listOfFiles.sort()
    pattern='M*P.jpg'
    for entry in listOfFiles:
        if fnmatch.fnmatch(entry, pattern):
            x=entry.find('UK00')
            if x== -1 :
                CheckIfFireball(srcpath, entry, destpath)
    return

def ProcessAMonth(srcpath, destpath):
    try: 
        listOfFiles = os.listdir(srcpath)
    except:
        print('nothing to analyse')
        return 
    for entry in listOfFiles:
        if os.path.isdir(os.path.join(srcpath,entry)):
            print('processing '+entry)
            ProcessADay(os.path.join(srcpath,entry), destpath)
    return 

if __name__ == '__main__':

    config=cfg.ConfigParser()
    config.read(sys.argv[1])
    ym=sys.argv[2]

    srcpath=config['camera']['localfolder']
    destpath=os.path.join(srcpath, '../fireballs')
    yy=ym[:4]
    srcpath=os.path.join(srcpath, yy, ym)
    print('Processing ' + srcpath + '; saving data in ' + destpath)
    ProcessAMonth(srcpath, destpath)

