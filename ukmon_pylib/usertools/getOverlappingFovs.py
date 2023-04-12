# Copyright (C) 2018-2023 Mark McIntyre
# 
#
import os
import sys
import glob


from utils.kmlHandlers import munchKML
from shapely.geometry import Point


def pointInsideFov(lat,lng, k1):
    c1, p1 = munchKML(k1, True)
    pt = Point(lat, lng)
    return p1.contains(pt)


def checkKMLOverlap(k1, k2):
    c1,p1 = munchKML(k1, True)
    c2,p2 = munchKML(k2, True)
    return p1.intersects(p2)


def getOverlapWith(srcfolder, kmlpat, refcam):
    kmllist = glob.glob1(srcfolder, kmlpat)
    currmatches=[]
    refkml = f'{refcam}{kmlpat[1:]}'
    currmatches.append(refcam[:6])
    print('checking ', refkml)
    for testkml in kmllist:
        if testkml != refkml:
            testcam,_ = os.path.splitext(testkml)
            #print(testkml)
            #print('comparing to ', testcam)
            if checkKMLOverlap(os.path.join(srcfolder, refkml), os.path.join(srcfolder, testkml)) is True:
                currmatches.append(testcam[:6])
    return currmatches



def getOverlappingCameras(srcfolder, kmlpat):
    kmllist = glob.glob1(srcfolder, kmlpat)
    kmllist2 = kmllist
    matches = []

    for refkml in kmllist:
        currmatches=[]
        refcam,_ = os.path.splitext(refkml)
        currmatches.append(refcam[:6])
        #print('checking ', refcam)
        for testkml in kmllist2:
            if testkml != refkml:
                testcam,_ = os.path.splitext(testkml)
                #print('comparing to ', testcam)
                if checkKMLOverlap(os.path.join(srcfolder, refkml), os.path.join(srcfolder, testkml)) is True:
                    currmatches.append(testcam[:6])
        matches.append(currmatches)
    return matches


if __name__ == '__main__':
    src = sys.argv[1]
    targ = sys.argv[2]
    matches = getOverlappingCameras(src, '*-25km.kml')
    print(matches)
