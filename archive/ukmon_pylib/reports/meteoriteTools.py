# Find cameras near to a point and other tools relevant to meteorite finds

# Copyright (C) 2018-2023 Mark McIntyre

import json 
import os
import pandas as pd
import numpy as np

from reports.CameraDetails import loadLocationDetails
from meteortools.utils.Math import greatCircleDistance


def stationsNearPoint(lat, lon, dist):
    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    srcfile = os.path.join(datadir, 'admin', 'cameraLocs.json')
    jsdata = json.load(open(srcfile))
    camlocs = pd.DataFrame(jsdata).transpose()
    camlocs.drop(columns=['ele','az','alt','fov_h','fov_v','rot'], inplace=True)

    camlocs['dist'] = [greatCircleDistance(np.radians(statlat), np.radians(statlon), 
                                            np.radians(lat),np.radians(lon)) 
                                            for statlat,statlon in zip(camlocs.lat, camlocs.lon)]

    nearby = camlocs[camlocs.dist < dist]

    caminfo = loadLocationDetails()
    caminfo = caminfo[caminfo.active==1]
    caminfo.set_index('stationid', inplace=True)
    caminfo.drop(columns=['active','oldcode','direction','created','site','camtype'], inplace=True)    

    camlist = nearby.merge(caminfo, how='left', left_index=True, right_index=True)
    camlist.drop(columns=['lat','lon','dist'], inplace=True)
    camlist.drop_duplicates(inplace=True)
    return camlist
