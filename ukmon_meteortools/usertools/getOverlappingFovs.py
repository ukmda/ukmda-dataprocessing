# Copyright (C) 2018-2023 Mark McIntyre
# 
#
import os
import sys
import glob


from utils import munchKML
from shapely.geometry import Point


def pointInsideFov(latDegs,lngDegs, kmlFilename):

    c1, p1 = munchKML(kmlFilename, True)
    pt = Point(latDegs, lngDegs)
    return p1.contains(pt)


def checkKMLOverlap(kmfile1, kmfile2):
    _,p1 = munchKML(kmfile1, True)
    _,p2 = munchKML(kmfile2, True)
    return p1.intersects(p2)


def getOverlapWith(srcfolder, kmlpattern='*-25km.kml', refcam='UK0006'):
    kmllist = glob.glob1(srcfolder, kmlpattern)
    currmatches=[]
    refkml = f'{refcam}{kmlpattern[1:]}'
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



def getOverlappingCameras(srcfolder, kmlpattern='*-25km.kml'):
    kmllist = glob.glob1(srcfolder, kmlpattern)
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
