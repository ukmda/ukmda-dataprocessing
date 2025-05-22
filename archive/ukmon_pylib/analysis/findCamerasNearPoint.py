# copyright Mark McIntyre, 2024-

# find cameras near to a given point (lat/lon in degrees)

import os
import sys
import json
import numpy as np
import requests

from meteortools.utils.Math import greatCircleDistance


def camerasNearTo(lat, lon, distFromPt):
    l1 = np.radians(lat)
    g1 = np.radians(lon)
    cams = []
    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    camdb = os.path.join(datadir, 'admin', 'cameraLocs.json')
    caminfo = json.load(open(camdb))
    for cam in caminfo:
        l2 = np.radians(caminfo[cam]['lat'])
        g2 = np.radians(caminfo[cam]['lon'])
        dist = greatCircleDistance(l1, g1, l2, g2)
        # print(dist)
        if dist < distFromPt:
            url = f'https://api.ukmeteors.co.uk/camdetails?camid={cam}'
            res = requests.get(url)
            if res.status_code == 200:
                dta = json.loads(res.text)
                cams.append(dta[0]['eMail'])
    cams = list(set(cams))
    camstr = ''
    for cam in cams:
        camstr = camstr + cam + ';'
    return camstr


def getCoordsFromTraj(trajname):
    lat = 0
    lon = 0
    return lat, lon


if __name__ == '__main__':
    lat = float(sys.argv[1])
    lon = float(sys.argv[2])
    dist = float(sys.argv[3])

    print(camerasNearTo(lat, lon, dist))