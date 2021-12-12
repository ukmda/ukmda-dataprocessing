""" 
Create UFO-orbit compatible single-station data from the UKMON single-station data 

parameters:
    YYYY - year to process
    outfile - full path to output file

Consumes:
    UKMON's internal single-station CSV file, generated from singlestation detections
    Note: DATADIR must be exported to the enviroment first

Produces:
    R91 compatible CSV file 
    - note that it has four extra colummns, AV, Shower, filename and datestamp
    - UFOOrbit ignores these
"""

import os
import sys
import pandas as pd

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python UKMONtoUFOcsv.py 2017 outfile')
        exit(0)

    datadir = os.getenv('DATADIR')
    if datadir is None:
        print('define DATADIR first')
        exit(1)

    yr = int(sys.argv[1])
    outfile = sys.argv[2]
    singleFile = os.path.join(datadir, 'single', 'singles-{}.csv'.format(yr))
    sngl = pd.read_csv(singleFile)
    sngl = sngl[sngl['Y']==yr]

    #sngl = sngl.drop(columns =['AngVel','Shwr','Filename','Dtstamp'])
    sngl = sngl.drop_duplicates().sort_values(by=['Y','M','D','h','m','s','ID'])

    sngl.Ver='R91'
    sngl.to_csv(outfile, sep=',', index=False)
