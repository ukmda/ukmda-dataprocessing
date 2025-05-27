# Find cameras near to a point and other tools relevant to meteorite finds

# Copyright (C) 2018-2023 Mark McIntyre

import sys
import json 
import pandas as pd
import numpy as np
import requests

from meteortools.utils.Math import greatCircleDistance


def stationsNearPoint(lat, lon, dist=75, email_only=True):
    lat = np.radians(lat)
    lon = np.radians(lon)
    res = requests.get('https://archive.ukmeteors.co.uk/browse/cameraLocs.json')
    if res.status_code != 200:
        return None
    jsdata = json.loads(res.text)
    camlocs = pd.DataFrame(jsdata).transpose()
    camlocs.drop(columns=['ele','az','alt','fov_h','fov_v','rot'], inplace=True)
    camlocs['dist'] = [greatCircleDistance(np.radians(statlat), np.radians(statlon), lat, lon) 
                                            for statlat,statlon in zip(camlocs.lat, camlocs.lon)]
    nearby = camlocs[camlocs.dist < dist]
    cams = {}
    for cam in nearby.index:
        res = requests.get(f'https://api.ukmeteors.co.uk/camdetails?camid={cam}')
        if res.status_code == 200:
            dta = json.loads(res.text)
            if len(dta) > 0:
                cams[cam] = {'email': dta[0]['eMail']}
            else:
                cams[cam] = {'email':'unknown'}
        else:
            cams[cam] = {'email':'unknown'}
    camlist = nearby.merge(pd.DataFrame(cams).transpose(), how='left', left_index=True, right_index=True)
    if email_only:
        camlist.drop(columns=['lat','lon','dist'], inplace=True)
        camlist.drop_duplicates(inplace=True)
    return camlist


def getCoordsFromTraj(trajname):
    lat = 0
    lon = 0
    return lat, lon


if __name__ == '__main__':
    lat = float(sys.argv[1])
    lon = float(sys.argv[2])
    dist = float(sys.argv[3])

    print(stationsNearPoint(lat, lon, dist))
