# 
# 
#
#from genericpath import exists
import os
import sys
import glob
import shutil

from utils.makeCoverageMap import munchKML


def checkKMLOverlap(k1, k2):
    c1,p1=munchKML(k1, True)
    c2,p2=munchKML(k2, True)
    return p1.intersects(p2)


def getOverlappingCameras(srcfolder, kmlpat):

    kmllist = glob.glob1(srcfolder, kmlpat)
    kmllist2 = kmllist
    matches = []

    for refkml in kmllist:
        currmatches=[]
        refcam,_ = os.path.splitext(refkml)
        currmatches.append(refcam)
        #print('checking ', refcam)
        for testkml in kmllist2:
            if testkml != refkml:
                testcam,_ = os.path.splitext(testkml)
                #print('comparing to ', testcam)
                if checkKMLOverlap(refkml, testkml) is True:
                    currmatches.append(testcam)
        matches.append(currmatches)

    return matches


if __name__ == '__main__':
    src = sys.argv[1]
    targ = sys.argv[2]
    matches = getOverlappingCameras(src, '*-25km.kml')
    #for li in matches:
    #    print(len(li), li)
    #    # only one entry means no matches with this camera
    #    if len(li) > 1: 
    #        print('some matches')
    #        targpth = os.path.join(targ, li[0])

    #        if not os.path.exists(targpth):
    #            os.mkdir(targpth)
    #        files=glob.glob1(targpth, '*')
    #        for f in files:
    #            os.remove(os.path.join(targpth, f))

    #        for cam in li:
    #            srcfil = os.path.join(src, cam + '.kml')
    #            shutil.copy(srcfil, targpth)
    #    else:
    #        print('no matches with camera', li[0])
