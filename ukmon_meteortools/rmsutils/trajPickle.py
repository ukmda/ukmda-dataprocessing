import pickle
import tempfile
import pandas as pd
import numpy as np
import requests
import os
import json
# imports are required to load the picklefiles
try:
    from wmpl.Trajectory.CorrelateRMS import TrajectoryReduced, DatabaseJSON # noqa: F401
    from wmpl.Trajectory.CorrelateRMS import MeteorObsRMS, PlateparDummy, MeteorPointRMS # noqa: F401
except:
    print('WMPL not available')

from ukmon_meteortools.usertools.getLiveImages import _download
from ukmon_meteortools.fileformats import trackCsvtoKML


def getTrajPickle(trajname):
    """ Retrieve a the pickled trajectory for a matched detection 
    
    Arguments:  
        trajname:   [string] Name of the trajectory eg 20230502_025228.374_UK_BE

    Returns:
        WMPL traj object

    Notes:
        WMPL must be in the $PYTHONPATH for this function to be available

    """
    apiurl = 'https://api.ukmeteornetwork.co.uk/pickle/getpickle'
    fmt = 'pickle'
    apicall = f'{apiurl}?reqval={trajname}&format={fmt}'
    matchpickle = pd.read_json(apicall, lines=True)
    if 'url' in matchpickle:
        outdir = tempfile.mkdtemp()
        _download(matchpickle.url[0], outdir, matchpickle.filename[0])

        localfile = os.path.join(outdir, matchpickle.filename[0])
        with open(localfile, 'rb') as f:
            traj = pickle.load(f, encoding='latin1')
        try:
            os.remove(localfile)
        except:
            print(f'unable to remove {localfile}')
    else:
        traj = None
    return traj


def trajectoryKML(trajname, outdir=None):
    """
    Create a 3-d KML file showing the trajectory of a meteor, which can be 
    loaded into Google Maps. 
    
    Arguments:  
        trajname:   [string] trajectory name eg 20230213_025913.678_UK
        outdir:     [string] where to save the file. Defaults to current location  

    Returns:  
        kmlfile:    name of the saved KML file  
    """
    apiurl = 'https://api.ukmeteornetwork.co.uk/pickle/getpickle'
    fmt = 'json'
    apicall = f'{apiurl}?reqval={trajname}&format={fmt}'
    res = requests.get(apicall, stream=True)
    if res.status_code == 200:
        data=b''
        for chunk in res.iter_content(chunk_size=4096):
            data = data + chunk
        jsd = json.loads(data)    
        lats = []
        lons = []
        hts = [] 
        rngs = []
        for js in jsd['observations']:
            k = list(js.keys())[0]
            thisstat = js[k]
            lats = lats + thisstat['model_lat']
            lons = lons + thisstat['model_lon']
            hts = hts + thisstat['model_ht']
            rngs = rngs + thisstat['model_range']
        df = pd.DataFrame({"lats": np.degrees(lats), "lons": np.degrees(lons), "alts": hts, "ranges": rngs})
        df = df.sort_values(by=['ranges', 'lats'])
        outfname = os.path.join(outdir, f'{trajname}.kml')
        if outdir is None:
            outdir = '.'
            os.makedirs(outdir, exist_ok=True)
        trackCsvtoKML(trajname, df, saveOutput=True, outdir=outdir)
        return outfname
    else:
        print('no match')
        return None
