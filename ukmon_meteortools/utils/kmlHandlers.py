import xmltodict
from shapely.geometry import Polygon
import csv
import simplekml
import numpy as np
import pandas as pd
import os
import sys
import pickle
import tempfile
from ukmon_meteortools.usertools.getLiveImages import _download


def munchKML(kmlFilename, return_poly=False):
    """ Load a KML file and return either a list of lats and longs, or a Shapely polygon  
    
    Arguments:  
        kmlFilename:    [string] full path to the KML file to consume   
        return_poly:    [bool] return a Shapely polygon? Default False  

    
    Returns:  
        if return_poly is false, returns a tuple of (cameraname, lats, longs) where lats and longs are lists of the 
        latitudes and longitudes in the KML file.  

        If return_poly is true, returns a tuple of (cameranamem, shapely Polygon)  
    """

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


def trackCsvtoKML(trackcsvfile, trackdata=None, saveOutput=True):
    """ 
    Either reads a CSV file containing lat, long, height, time of an event and 
    creates a 3d KML file from it or, if trackdata is populated, converts a Pandas dataframe containing 
    the same data. Output is written to disk unless saveOutput is false.  
    
    Arguments:  
        trackcsvfile:   [string] full path to the file to read from  
        trackdata:      [array] pandas dataframe containing the data. Default None  
        saveOutput:     [bool] write the KML file to disk. Default true  

    Returns:  
        the KML file as a tuple  
        """
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
    if saveOutput:
        kml.save(outname)
    return kml


def getTrackDetails(traj):
    """ Get track details from a WMPL trajectory object  
    
    Arguments:  
        traj:       a WMPL trajectory object containing observations  

    Returns:  
        a Pandas dataframe containing the lat, long, alt and time of each point on the trajectory, sorted by time. 
    """
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
    """ Retrieve a the pickled trajectory for a matched detection 
    
    Arguments:  
        trajname:   [string] Name of the trajectory eg 20230502_025228.374_UK_BE

    Returns:
        tuple containing (traj object, kml filename)  


    """
    apiurl = 'https://api.ukmeteornetwork.co.uk/pickle/getpickle'
    fmt = 'pickle'
    apicall = f'{apiurl}?reqval={trajname}&format={fmt}'
    matchpickle = pd.read_json(apicall, lines=True)
    if 'url' in matchpickle:
        outdir = tempfile.mkdtemp()
        _download(matchpickle['url'], outdir, matchpickle['filename'])

        localfile = os.path.join(outdir, matchpickle['filename'])
        with open(localfile, 'rb') as f:
            traj = pickle.load(f, encoding='latin1')
        try:
            os.remove(localfile)
        except:
            print(f'unable to remove {localfile}')
    else:
        traj = None
    kmlfile = trajname[:15] + '.kml'
    return traj, kmlfile


if __name__ == '__main__':
    ext = os.path.splitext(sys.argv[1])
    if ext == 'csv':
        trackCsvtoKML(sys.argv[1])
    else:
        traj, kmlfile = getTrajPickle(sys.argv[1])
        tdets = getTrackDetails(traj)
        trackCsvtoKML(kmlfile, tdets)
