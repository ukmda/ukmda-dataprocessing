import xmltodict
from shapely.geometry import Polygon
import csv
import simplekml
import numpy as np
import pandas as pd
import os
import sys
import boto3

try:
    from wmpl.Utils.Pickling import loadPickle
    gotpickler = True
except:
    gotpickler = False


def munchKML(kmlFilename, return_poly=False):
    with open(kmlFilename) as fd:
        x = xmltodict.parse(fd.read())
        cname = x['kml']['Folder']['name']
        coords = x['kml']['Folder']['Placemark']['MultiGeometry']['Polygon']['outerBoundaryIs']['LinearRing']['coordinates']
        coords = coords.split('\n')
        if return_poly is False:
            lats = []
            lngs = []
            for lin in coords:
                s = lin.split(',')
                lngs.append(float(s[0]))
                lats.append(float(s[1]))
            return cname, lats, lngs
        else:
            ptsarr=[]
            for lin in coords:
                s = lin.split(',')
                ptsarr.append((float(s[0]), float(s[1])))
            polyg = Polygon(ptsarr)
            return cname, polyg 


def trackCsvtoKML(trackcsvfile, trackdata=None):
    kml=simplekml.Kml()
    kml.document.name = trackcsvfile
    if trackdata is None:
        inputfile = csv.reader(open(trackcsvfile))
        for row in inputfile:
            #columns are lat, long, height, times
            kml.newpoint(name='', coords=[(row[1], row[0], row[2])])
    else:
        for i,r in trackdata.iterrows():
            kml.newpoint(name='', coords=[(r[1], r[0], r[2])], extrude=1, altitudemode='absolute')
    outname = trackcsvfile.replace('.csv','.kml')
    kml.save(outname)
    return kml


def getTrackDetails(traj):
    lats = []
    lons = []
    alts = [] 
    lens = []
    # Go through observation from all stations
    for obs in traj.observations:
        # Go through all observed points
        for i in range(obs.kmeas):
            lats.append(np.degrees(obs.model_lat[i]))
            lons.append(np.degrees(obs.model_lon[i]))
            alts.append(obs.model_ht[i])
            lens.append(obs.time_data[i])
    df = pd.DataFrame({"lats": lats, "lons": lons, "alts": alts, "times": lens})
    df = df.sort_values(by=['times', 'lats'])
    return df


def getTrajPickle(trajname):
    tmpdir = os.getenv('TMP', default='/tmp')
    s3 = boto3.client('s3')
    srcbucket = 'ukmon-shared'
    orb = trajname
    picklefile = orb[:15] + '_trajectory.pickle'
    kmlfile = orb[:15] + '.kml'
    yr = picklefile[:4]
    ym = picklefile[:6]
    ymd = picklefile[:8]
    fname = f'matches/RMSCorrelate/trajectories/{yr}/{ym}/{ymd}/{orb}/{picklefile}'
    localfile = os.path.join(tmpdir, picklefile)
    s3.download_file(srcbucket, fname, localfile)
    traj = loadPickle(*os.path.split(localfile))
    try:
        os.remove(localfile)
    except:
        print(f'unable to remove {localfile}')
    return traj, kmlfile


if __name__ == '__main__':
    ext = os.path.splitext(sys.argv[1])
    if ext == 'csv':
        trackCsvtoKML(sys.argv[1])
    else:
        if gotpickler is False:
            print('WMPL not available, aborting')
        else:
            traj, kmlfile = getTrajPickle(sys.argv[1])
            tdets = getTrackDetails(traj)
            trackCsvtoKML(kmlfile, tdets)
