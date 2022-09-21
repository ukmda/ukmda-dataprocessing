# python module to retrieve data as seen from a specific place


import pandas as pd
import datetime
from datetime import timezone
import numpy as np
import boto3
import json


def filterByDtstamp(df, dt, uncertainty=10):
    dt1 = (dt + datetime.timedelta(minutes=-uncertainty)).replace(tzinfo=timezone.utc).timestamp()
    dt2 = (dt + datetime.timedelta(minutes=+uncertainty)).replace(tzinfo=timezone.utc).timestamp()
    df = df[df.Dtstamp >= dt1]
    df = df[df.Dtstamp <= dt2]
    return df


# bearing of point A from B. All angles in degrees
def bearingBfromA(a_l, a_g, b_l, b_g):
    a_l = np.radians(a_l)
    b_l = np.radians(b_l)
    a_g = np.radians(a_g)
    b_g = np.radians(b_g)
    X = np.cos(b_l) * np.sin(b_g - a_g)
    Y = np.cos(a_l) * np.sin(b_l) - np.sin(a_l) * np.cos(b_l) * np.cos(b_g - a_g)
    bearing = np.arctan2(X, Y)
    if bearing < 0: 
        bearing = 2*np.pi + bearing
    return np.degrees(bearing)


# not fully accurate, using equirectangular approximation
def distanceBfromA(a_l, a_g, b_l, b_g):
    a_l = np.radians(a_l)
    b_l = np.radians(b_l)
    a_g = np.radians(a_g)
    b_g = np.radians(b_g)
    x = (b_g - a_g) * np.cos((a_l + b_l)/2)
    y = (a_l - b_l)
    d = np.sqrt(x*x + y*y)* 6371000
    return d


def camDir(camdb, Filename):
    camid = Filename[3:9]
    camdir = camdb[camid]['az']
    return camdir


def camFoV(camdb, Filename):
    camid = Filename[3:9]
    camfov = camdb[camid]['fov_h']
    return camfov


def isVisible(adash, gdash):
    '''
    formula is 
    adash = looking - cam_dir
    gdash = Az1 - cam_dir
    if adash < 90 and > 270 and adash < gdash then no intersection
    else if adash > gdash then no intersection
    '''
    if adash < 90 or adash > 270:
        if adash < gdash:
            return False
        else:
            return True
    else:
        if adash < gdash:
            return True
        else:
            return False



if __name__ == '__main__':
    lat = 51.89     # observers latitude
    lon = -2.09     # observers longitude
    looking = 190   # direction observer was looking in
    dt = datetime.datetime(2022,8,14,21,0,0) # reported time of event

    yr = dt.year

    s3 = boto3.resource('s3')
    obj = s3.Object('ukmon-shared','admin/cameraLocs.json')
    camdb = json.load(obj.get()['Body']) 

    df = pd.read_parquet(f"s3://ukmon-shared/matches/singlepq/singles-{yr}.parquet.gzip")

    df = filterByDtstamp(df, dt)
    df['cam_dir'] = [bearingBfromA(lat, lon, ll, lg) for ll,lg in zip(df.Lat, df.Long)]
    df['cam_dist'] = [distanceBfromA(lat, lon, ll, lg) for ll,lg in zip(df.Lat, df.Long)]
    df['cam_azi'] = [camDir(camdb, fn) for fn in df.Filename]
    df['cam_fov'] = [camFoV(camdb, fn) for fn in df.Filename]
    df['adash'] = [(looking - cam_dir) for cam_dir in df.cam_dir]
    df['gdash'] = [(az1 - cam_dir) for az1, cam_dir in zip(df.Az1, df.cam_dir)]
    df['isvisible'] = [isVisible(ad, gd) for ad, gd in zip(df.adash, df.gdash)]
