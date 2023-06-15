# Copyright (C) 2018-2023 Mark McIntyre
import numpy as np
import json
import os 
import pandas as pd

from ukmon_meteortools.fileformats import trackCsvtoKML
from wmpl.Utils.Pickling import loadPickle


def pickleToKml(picklename, outdir=None):
    """Create a KML file of the trajectory in a solution pickle
     
    Arguments:  
        picklename: [string] full path to the solution pickle file  

    Keyword Args:  
        outdir: [string] where to save the KML. Default same place as pickle. 
    
    Returns:   
        the KML file as a tuple  
    """
    pickpath, trajname = os.path.split(picklename)
    data = loadPickle(pickpath, trajname).toJson()
    jsd = json.loads(data)
    lats = []
    lons = []
    hts = [] 
    times = []
    for js in jsd['observations']:
        k = list(js.keys())[0]
        thisstat = js[k]
        lats += thisstat['model_lat']
        lons += thisstat['model_lon']
        hts += thisstat['model_ht']
        times += thisstat['time_data']
    df = pd.DataFrame({"lats": np.degrees(lats), "lons": np.degrees(lons), "alts": hts, "times": times})
    df = df.sort_values(by=['times', 'lats'])
    os.makedirs(outdir, exist_ok=True)
    return trackCsvtoKML(trajname.replace('.pickle', 'csv'), df, saveOutput=True, outdir=outdir)