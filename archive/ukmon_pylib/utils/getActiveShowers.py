# Copyright (C) 2018-2023 Mark McIntyre
#
# simple script to get the active shower list from the IMO working list

import datetime
import numpy as np
import pandas as pd
import os
import json
import ephem

from wmpl.Utils.TrajConversions import datetime2JD, jd2Date
from wmpl.Utils.SolarLongitude import solLon2jdVSOP, jd2SolLonVSOP # good enough for our purposes here

def getActiveShowers(targdate, aslist=False, inclMinor=False, inclSpo=False, showall=False, tolerance=1):
    """
    Return a list of showers active at the specified date  

    Arguments:  
        targdate:   [str] Date in YYYYMMDD format  

    Keyword Arguments:  
        retlist:    [bool] False return a list if True otherwise print to console 
        inclMinor:  [bool] False, include minor showers if True
        inclSpo:    [bool] False, include 'spo' if True
        tolerance:  [int] default 1, number of days either side of the date to check

    Returns:  
        If retlist is true, returns a python list of shower short-codes eg ['PER','LYR']  

    """
    sl = _loadShowerTable()
    mmlist = _loadMajorMinor()
    testdate = datetime.datetime.strptime(targdate, '%Y%m%d').replace(tzinfo=datetime.timezone.utc)
    sollon = np.degrees(jd2SolLonVSOP(datetime2JD(testdate)))
    sl1 = sl[sl.la_sun > sollon - tolerance]
    sl1 = sl1[sl1.la_sun < sollon + tolerance]
    sl1.drop_duplicates('IAU_code', inplace=True)

    if showall:
        listofshowers = list(sl1.IAU_code)
    else:
        listofshowers = []
        if not inclMinor:
            for _,rw in sl1.iterrows():
                if rw.IAU_code in mmlist['major']:
                    listofshowers.append(rw.IAU_code)
        else:
            for _,rw in sl1.iterrows():
                if rw.IAU_code in mmlist['major'] or rw.IAU_code in mmlist['minor']:
                    listofshowers.append(rw.IAU_code)

    if inclSpo:
        listofshowers.append('spo')

    if aslist:
        return listofshowers
    else:
        print(' '.join(listofshowers))


def getShowerDets(shwr, asstring=False):
    """ Get details of a shower 
    
    Arguments:  
        shwr:   [string] three-letter shower code eg PER  
    Keyword Arguments:
        stringFmt [bool] default False, return a string rather than a list
        dataPth   [string] path to the datafiles. Default None means data read from internal files. 
         
    Returns:  
        either a tuple of (id, full name, peak solar longitude, peak date mm-dd)  
        or a string "peak sollon, name, peak date,  shower code"

    """
    sl = _loadShowerTable()
    thisshower = sl[sl.IAU_code == shwr]

    if len(thisshower) > 0:
        id = int(thisshower.iloc[0]['IAU_no'])
        name = thisshower.iloc[0]['name']
        if name is None or str(name) == 'nan':
            name = getAltShwrName(shwr)
        pkdtstr = thisshower.iloc[0]['peak']
        if pkdtstr is None or str(pkdtstr) == 'nan':
            sollon = getAltShwrPeak(shwr)
            lve = ephem.previous_vernal_equinox(ephem.Date(datetime.datetime.now(datetime.timezone.utc)))
            pkdt = ephem.to_timezone(ephem.date(lve + sollon), tzinfo=datetime.timezone.utc)
        else:        
            pkdt = datetime.datetime.strptime(f'{datetime.datetime.now().year} {pkdtstr}','%Y %b %d')
            pksollong = np.degrees(jd2SolLonVSOP(datetime2JD(pkdt)))

        dtstr = pkdt.strftime('%m-%d')
    else:
        id = 0
        name = 'Unknown'
        pksollong = 0
        dtstr = 'Unknown'

    pksollong = round(pksollong,1)
    if not asstring:
        return  (id, name, pksollong, dtstr)
    else:
        # note, different order and return values
        return f'{pksollong},{name},{dtstr},{shwr}'


def getShowerPeak(shwr):
    """ Get date of a shower peak in MM-DD format
    
    Arguments:  
        shwr:   [string] three-letter shower code eg PER  
         
    Returns:  
        peak date mm-dd  
    """
    _, _, _, pk = getShowerDets(shwr)
    return pk


def getShowerStartEnd(shwr, start=True):
    """ Get approx start/end dates of a shower 
    
    Arguments:  
        shwr:   [string] three-letter shower code eg PER  

    Keyword Arguments:
        start:  [bool] true if requesting the start date, otherwise you'll get the end date
         
    Returns:  
        dtval:  [datetime] approx start or end date of the shower

    """
    sl = _loadShowerTable()
    thisshower = sl[sl.IAU_code == shwr]

    reqfield = 'start' if start else 'end'
    if len(thisshower) > 0:
        reqdtstr = thisshower.iloc[0][reqfield]
        if reqdtstr is None or str(reqdtstr) == 'nan':
            reqsl = thisshower.iloc[0]['la_sun'] if start else thisshower.iloc[-1]['la_sun']
            lve = ephem.previous_vernal_equinox(ephem.Date(datetime.datetime.now(datetime.timezone.utc)))
            reqdt = ephem.to_timezone(ephem.date(lve + reqsl), tzinfo=datetime.timezone.utc)
        else:
            reqdt = datetime.datetime.strptime(f'{datetime.datetime.now(datetime.timezone.utc).year} {reqdtstr}','%Y %b %d').replace(tzinfo=datetime.timezone.utc)

        return reqdt
    

def getAltShwrName(shwr, dir_path=None):
    if not dir_path:
        dir_path = os.path.join(os.getenv('WMPL_LOC', default=os.path.expanduser('~/src/WesternMeteorPyLib/')), 'wmpl','share')
    srcfile = os.path.join(dir_path, 'streamfulldata.csv')
    rawdf = pd.read_csv(os.path.expanduser(srcfile), sep='|', header=None)
    usefuldf = pd.concat([rawdf[3],rawdf[4]], axis=1)
    usefuldf.rename(columns={3:'IAU_code',4:'name'}, inplace=True)
    usefuldf.drop_duplicates(inplace=True)
    match = usefuldf[usefuldf.IAU_code==shwr]
    if len(match) > 0:
        shower_name = match.iloc[0]['name'].strip()
    else:
        shower_name = f'{shwr} unknown'
    return shower_name


def getAltShwrPeak(shwr, dir_path=None):
    if not dir_path:
        dir_path = os.path.join(os.getenv('WMPL_LOC', default=os.path.expanduser('~/src/WesternMeteorPyLib/')), 'wmpl','share')
    srcfile = os.path.join(dir_path, 'streamfulldata.csv')
    rawdf = pd.read_csv(os.path.expanduser(srcfile), sep='|', header=None)
    usefuldf = pd.concat([rawdf[3],rawdf[6], rawdf[7]], axis=1)
    usefuldf.rename(columns={3:'IAU_code',7:'la_sun'}, inplace=True)
    match = usefuldf[usefuldf.IAU_code==shwr]
    match = match[match[6] > -1]
    if len(match) > 0:
        sollon = match.iloc[-1]['la_sun']
    else:
        sollon = None
    return sollon


def _loadMajorMinor(dir_path=None):
    if not dir_path:
        dir_path = os.path.join(os.getenv('DATADIR', default=os.path.expanduser('~/prod/data')), 'share')
    return json.load(open(os.path.join(dir_path,'majorminor.json')))


def _loadShowerTable(dir_path=None, file_name=None, forceRedo=False):
    if not dir_path:
        dir_path = os.path.join(os.getenv('DATADIR', default=os.path.expanduser('~/prod/data')), 'share')
        file_name = 'gmn_shower_table_20230518.txt'
    if not os.path.isfile(os.path.join(dir_path, 'combined_shower_table.parquet')) or forceRedo:
        gmn_shower_list = []
        lis = open(os.path.join(dir_path, file_name), encoding='cp1252').readlines()
        lis = [x for x in lis if x[0]!='#']
        for line in lis:
            if len(line) < 10:
                    continue
            la_sun, L_g, B_g, v_g, dispersion, IAU_no, IAU_code = line.strip().split()
            gmn_shower_list.append([
                float(la_sun), 
                np.radians(float(L_g)),
                np.radians(float(B_g)), 
                1000*float(v_g), 
                np.radians(float(dispersion)), 
                int(IAU_no), 
                IAU_code]
            )
        df = pd.DataFrame(gmn_shower_list, columns=['la_sun', 'L_g', 'B_g', 'v_g', 'dispersion', 'IAU_no', 'IAU_code'])

        imodf = pd.read_xml(os.path.join(dir_path, 'IMO_Working_Meteor_Shower_List.xml'))
        imodf.set_index('IAU_code', inplace=True)
        df = df.join(imodf, on='IAU_code')
        df.to_parquet(os.path.join(dir_path, 'combined_shower_table.parquet'))
    else:
        df = pd.read_parquet(os.path.join(dir_path, 'combined_shower_table.parquet'))
    return df
