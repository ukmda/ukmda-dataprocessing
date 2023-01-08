import numpy as np
import pandas as pd
import datetime
import argparse
import json
import os
import glob
from datetime import timezone
import boto3
import shutil

from fileformats import CameraDetails as cd
from wmpl.Utils.Pickling import loadPickle

from wmpl.Utils.Earth import greatCircleDistance
from wmpl.Utils.TrajConversions import geo2Cartesian, raDec2AltAz, altAz2RADec
from wmpl.Utils.TrajConversions import raDec2ECI, datetime2JD
from wmpl.Utils.Math import vectNorm, angleBetweenVectors, vectorFromPointDirectionAndAngle

#from wmpl.Utils.TrajConversions import jd2Date, cartesian2Geo
#from wmpl.Utils.Math import vectMag, findClosestPoints, generateDatetimeBins, meanAngle, angleBetweenSphericalCoords

from fileformats.ftpDetectInfo import loadFTPDetectInfo, writeNewFTPFile


class localPlateparDummy:
    def __init__(self, **entries):
        """ This class takes a platepar dictionary and converts it into an object. """
        self.__dict__.update(entries)


class localTrajectoryConstraints(object):
    def __init__(self):
        self.min_meas_pts = 4
        self.max_toffset = 10.0
        self.min_station_dist = 5.0
        self.max_station_dist = 600.0
        self.min_qc = 3.0
        self.max_vel_percent_diff = 25.0
        self.v_avg_min = 3.0
        self.v_avg_max = 73.0
        self.max_begin_ht = 150
        self.min_begin_ht = 50.0
        self.max_end_ht = 130.0
        self.min_end_ht = 20.0
        self.force_hb_gt_he = True
        self.mag_filter_endpoints = 3
        self.max_merge_radiant_angle = 15
        self.geometric_uncert = True
        self.low_qc_threshold = 15.0
        self.low_qc_mc_runs = 20
        self.save_plots = False
        self.max_arcsec_err = 180.0
        self.min_arcsec_err = 30.0
        self.bad_station_obs_ang_limit = 2.0


class EventChecker(object):
    def __init__(self, traj_constraints):
        self.traj_constraints = traj_constraints

    def checkFOVOverlap(self, rp, tp):
        #
        # Check if fields of view overlap
        #
        reference_fov = np.radians(np.sqrt(rp.fov_v**2 + rp.fov_h**2))
        test_fov = np.radians(np.sqrt(tp.fov_v**2 + tp.fov_h**2))

        lat1, lon1, elev1 = np.radians(rp.lat), np.radians(rp.lon), rp.elev
        lat2, lon2, elev2 = np.radians(tp.lat), np.radians(tp.lon), tp.elev

        azim1, alt1 = raDec2AltAz(np.radians(rp.RA_d), np.radians(rp.dec_d), rp.JD, lat1, lon1)
        azim2, alt2 = raDec2AltAz(np.radians(tp.RA_d), np.radians(tp.dec_d), tp.JD, lat2, lon2)

        ref_jd = datetime2JD(datetime.datetime.utcnow())

        reference_stat_eci = np.array(geo2Cartesian(lat1, lon1, elev1, ref_jd))
        test_stat_eci = np.array(geo2Cartesian(lat2, lon2, elev2, ref_jd))

        # Compute ECI vectors of the FOV centre
        ra1, dec1 = altAz2RADec(azim1, alt1, ref_jd, lat1, lon1)
        reference_fov_eci = vectNorm(np.array(raDec2ECI(ra1, dec1)))
        ra2, dec2 = altAz2RADec(azim2, alt2, ref_jd, lat2, lon2)
        test_fov_eci = vectNorm(np.array(raDec2ECI(ra2, dec2)))

        # Compute ECI coordinates at different heights along the FOV line and check for FOV overlap
        # The checked heights are 50, 70, 95, and 115 km (ordered by overlap probability for faster 
        # execution)
        for height_above_ground in [95000, 70000, 115000, 50000]:
            # Compute points in the middle of FOVs of both stations at given heights
            reference_fov_point = reference_stat_eci + reference_fov_eci*(height_above_ground \
                - elev1)/np.sin(alt1)
            test_fov_point = test_stat_eci + test_fov_eci*(height_above_ground - elev2)/np.sin(alt2)

            # Check if the middles of the FOV are in the other camera's FOV
            if (angleBetweenVectors(reference_fov_eci, test_fov_point - reference_stat_eci) <= reference_fov/2) \
                or (angleBetweenVectors(test_fov_eci, reference_fov_point - test_stat_eci) <= test_fov/2):
                return True

            # Compute vectors pointing from one station's point on the FOV line to the other
            reference_to_test = vectNorm(test_fov_point - reference_fov_point)
            test_to_reference = -reference_to_test

            # Compute vectors from the ground to those points
            reference_fov_gnd = reference_fov_point - reference_stat_eci
            test_fov_gnd = test_fov_point - test_stat_eci

            # Compute vectors moved towards the other station by half the FOV diameter
            reference_moved = reference_stat_eci + vectorFromPointDirectionAndAngle(reference_fov_gnd, \
                reference_to_test, reference_fov/2)
            test_moved = test_stat_eci + vectorFromPointDirectionAndAngle(test_fov_gnd, test_to_reference, \
                test_fov/2)

            # Compute the vector pointing from one station to the moved point of the other station
            reference_to_test_moved = vectNorm(test_moved - reference_stat_eci)
            test_to_reference_moved = vectNorm(reference_moved - test_stat_eci)

            # Check if the FOVs overlap
            if (angleBetweenVectors(reference_fov_eci, reference_to_test_moved) <= reference_fov/2) \
                or (angleBetweenVectors(test_fov_eci, test_to_reference_moved) <= test_fov/2):
                #print('FOVs overlap')
                return True
        return False


    def stationRangeCheck(self, rp, tp):
        # Compute the distance between stations (km)
        dist = greatCircleDistance(np.radians(rp.lat), np.radians(rp.lon), np.radians(tp.lat), \
            np.radians(tp.lon))
        if (dist < self.traj_constraints.min_station_dist) \
            or (dist > self.traj_constraints.max_station_dist):
            return False
        else:
            return True


def loadPlatepar(ppdir, statid):
    # Load a platepar into the dummy structure
    ppfil = os.path.join(ppdir, f'{statid}.json')
    ppj = json.load(open(ppfil, 'r'))
    return localPlateparDummy(**ppj)


def checkTwoStations(datadir, stat1, stat2):
    # 
    # Check if two stations overlap
    #
    trajcons = localTrajectoryConstraints() # default set of constraints
    checker = EventChecker(traj_constraints=trajcons)
    ppdir = os.path.join(datadir, 'consolidated','platepars')
    p1 = loadPlatepar(ppdir, stat1)
    p2 = loadPlatepar(ppdir, stat2)
    fovcheck = checker.checkFOVOverlap(p1, p2)
    rangecheck = checker.stationRangeCheck(p1, p2)
    if fovcheck is False or rangecheck is False:
        return False
    return True


def checkClanfieldOverlaps(datadir, stat2):
    # 
    # Check all clanfield station overlas with stat2
    #
    trajcons = localTrajectoryConstraints() # default set of constraints
    checker = EventChecker(traj_constraints=trajcons)
    ppdir = os.path.join(datadir, 'consolidated','platepars')
    try:
        p2 = loadPlatepar(ppdir, stat2)
    except:
        return False
    print('testing', stat2)
    for stat1 in ['UK9988','UK9989','UK9990']:
        p1 = loadPlatepar(ppdir, stat1)
        fovcheck = checker.checkFOVOverlap(p1, p2)
        rangecheck = checker.stationRangeCheck(p1, p2)
        if fovcheck is True and rangecheck is True:
            return True
    return False


def getOverlappingStations(datadir, stationid):
    #
    # Check all overlaps for all stations
    #
    trajcons = localTrajectoryConstraints() # default set of constraints
    checker = EventChecker(traj_constraints=trajcons)
    ppdir = os.path.join(datadir, 'consolidated','platepars')
    rp = loadPlatepar(ppdir, stationid)
    ppfs = glob.glob1(ppdir, '*.json')
    overlaps=[]
    for ppf in ppfs: 
        ppfname, _ = os.path.splitext(ppf)
        if ppfname == stationid:
            continue
        tp = loadPlatepar(ppdir, ppfname)
        fovcheck = checker.checkFOVOverlap(rp, tp)
        distcheck = checker.stationRangeCheck(rp, tp)    
        if fovcheck is True and distcheck is True:
            overlaps.append(ppfname)
    return overlaps


def loadUFOdata(datadir, startdt, enddt, loc_cam):
    # 
    # load the simple CSV data for a specific camera between two dates
    #
    yr = startdt.year
    ufofile =  os.path.join(datadir, 'consolidated', f'M_{yr}-unified.csv')    
    # cols=['LocalTime','Loc_Cam','Y(UT)','M(UT)','D(UT)','H(UT)','M','S', 'Dir1', 'Alt1', 'Ra1', 'Dec1', 'Ra2', 'Dec2']
    cfd = pd.read_csv(ufofile, skipinitialspace=True)
    cfd['Dtstamp']=[datetime.datetime.strptime(x, '%Y%m%d_%H%M%S').replace(tzinfo=timezone.utc).timestamp() for x in cfd.LocalTime]
    cfd = cfd[cfd.Dtstamp > startdt.timestamp()]
    cfd = cfd[cfd.Dtstamp < enddt.timestamp()]
    cfd = cfd[cfd.Loc_Cam == loc_cam]
    return cfd


def loadSingleData(datadir, camlist, startdt, enddt):
    #
    # Load consolidated RMS single-station data for a list of cameras between two dates
    #
    yr = startdt.year
    snglfile = os.path.join(datadir, 'single', f'singles-{yr}.parquet.snap')
    cols=['Dtstamp','Filename','ID']
    filt=None
    data = pd.read_parquet(snglfile, columns=cols, filters=filt)
    # filter by overlaps and daterange
    data = data[data.ID.isin(camlist)]
    data = data[data.Dtstamp > startdt.timestamp()]
    data = data[data.Dtstamp < enddt.timestamp()]
    return data


def getAllPickles(datadir, dtstr):
    #
    # Download all the orbit pickle files for a given date pattern (eg 202207)
    #
    archbucket = 'ukmon-shared'
    outdir = os.path.join(datadir, 'orbits','pickles', str(dtstr))
    os.makedirs(outdir, exist_ok=True)

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(archbucket)
    
    files = [os.key for os in bucket.objects.filter(Prefix=f'matches/RMSCorrelate/trajectories/{dtstr[:4]}/{dtstr}/')]
    pickfiles = [file for file in files if '.pickle' in file]

    for pf in pickfiles:
        _, outfname = os.path.split(pf)
        targfile = os.path.join(outdir, outfname)
        s3.meta.client.download_file(archbucket, pf, targfile)    
    return 


def getStatsAndImgs(datadir, dtstr):
    #
    # Extract station details and image names from all pickles matching a date pattern 
    # and write a list to a file used_{dtstr}.csv
    #
    outfname = os.path.join(datadir, 'orbits',f'used_{dtstr}.csv')
    with open(outfname, 'w') as outf:
        pickdir = os.path.join(datadir, 'orbits','pickles', str(dtstr))
        pickfiles = glob.glob(os.path.join(pickdir, '*.pickle'))
        for pf in pickfiles:
            traj = loadPickle(*os.path.split(pf))
            try:
                for obs in traj.observations:
                    statid = obs.station_id
                    if obs.comment is not None:
                        js = json.loads(obs.comment)
                        ffname = js['ff_name']
                    else:
                        _, pn = os.path.split(pf)
                        ffname = f'FF_{statid}_{pn[:15]}_approx.fits'
                    outf.write(f'{statid}, {ffname}\n')
            except:
                print('traj object contains no observations')
    return len(pickfiles)
    

def findUnused(datadir, startdt, enddt):
    #
    # Load the single-station data, and filter out any detections that were 
    # already involved in a match, by comparing to the used_{dtstr}.csv file
    # created by getStatsAndImgs()
    #
    yr = startdt[:4]
    snglfile = os.path.join(datadir, 'single', f'singles-{yr}.parquet.snap')
    data = pd.read_parquet(snglfile)
    edt = datetime.datetime.strptime(enddt,'%Y%m')
    sdt = datetime.datetime.strptime(startdt,'%Y%m')
    data = data[data.Dtstamp < edt.timestamp()]
    fltdata = data[data.Dtstamp >= sdt.timestamp()]

    smth = sdt.month
    emth = edt.month
    if edt.year > sdt.year:
        emth += 12
    used = pd.DataFrame()
    for m in range (smth, emth):
        yy = sdt.year
        mm = m
        if mm > 12: 
            mm -= 12
            yy += 1
        tdt = datetime.datetime(yy, mm, 1)
        fname = os.path.join(datadir, 'orbits', f'used_{tdt.strftime("%Y%m")}.csv')
        newused = pd.read_csv(fname, header=None, skipinitialspace=True)
        used = pd.concat([used, newused])

    fltdata = fltdata[~fltdata.Filename.isin(list(used[1]))]
    # print(len(fltdata))
    uniqueids = fltdata.ID.unique()
    # print(uniqueids)
    overlapping=[]
    for id in uniqueids:
        if checkClanfieldOverlaps(datadir, id) is True:
            overlapping.append(id)
    fltdata = fltdata[fltdata.ID.isin(overlapping)]
    fltdata.to_parquet(f'all_unused.parquet-{startdt}-{enddt}.snap')
    return fltdata


def getRequiredFTPs(datadir, fltdata):
    #
    # Load the list of unused single-station detections, and download the 
    # FTP and platepars containing them
    #
    archbucket = 'ukmon-shared'
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(archbucket)
    targfldr = os.path.join(datadir, 'historic')
    fns = [fn[3:18] for fn in fltdata.Filename]    
    uniquefns = list(set(fns))
    uniquefns.sort()
    for fldr in uniquefns:
        camid = fldr[:6]
        srcpatt = f'matches/RMSCorrelate/{camid}/{fldr}'
        print(f'looking for {srcpatt}')
        files = [os.key for os in bucket.objects.filter(Prefix=srcpatt)]
        for pf in files:
            srcdir, outfname = os.path.split(pf)
            _, fldr = os.path.split(srcdir)
            outdir = os.path.join(targfldr,camid, fldr)
            os.makedirs(outdir, exist_ok=True)
            targfile = os.path.join(outdir, outfname)
            try: 
                s3.meta.client.download_file(archbucket, pf, targfile)    
            except:
                print(f'unable to download {pf}')
       

def updateFTPForUnused(datadir, fltdata):
    #
    # Read in FTP files downloaded by getRequiredFTPs, filter out events not in
    # the all_unused file, and write the FTPdetect out again, renaming the old one first
    #
    unusedimgs=fltdata.Filename.unique()
    ftpdir = os.path.join(datadir, 'historic')
    ftplist = [os.path.join(dp, f) for dp, dn, filenames in os.walk(ftpdir) for f in filenames if os.path.splitext(f)[1] == '.txt' and f[:3]=='FTP' and 'uncalibrated' not in f]
    for ftpfile in ftplist:
        outdir, fname = os.path.split(ftpfile)
        newname = os.path.join(outdir, f'old_{fname}')
        if os.path.isfile(newname):
            continue 
        metlist = loadFTPDetectInfo(ftpfile, join_broken_meteors=False)
        if len(metlist) == 0:
            continue
        adjmetlist = [met for met in metlist if met.ff_name in unusedimgs]
        writeNewFTPFile(ftpfile, adjmetlist)
    return 


def prepDataForRange(startdt, enddt):
    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    sdt = datetime.datetime.strptime(startdt, '%Y%m')
    edt = datetime.datetime.strptime(enddt, '%Y%m')
    smth = sdt.month
    emth = edt.month
    for m in range (smth, emth+1):
        tdt = datetime.datetime(sdt.year, m, 1)
        dtstr = tdt.strftime('%Y%m')
        #getAllPickles(datadir, dtstr)
        getStatsAndImgs(datadir, dtstr)
    fltdata = findUnused(datadir, startdt, enddt)
    getRequiredFTPs(datadir, fltdata)
    updateFTPForUnused(datadir, fltdata)



if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='check a station for overlaps')

    arg_parser.add_argument('stations', type=str, help='Comma-separated list of stations: single station means compare to all')

    cml_args = arg_parser.parse_args()

    stats = cml_args.stations.split(',')

    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    ppdir = os.path.join(datadir, 'consolidated','platepars')
    if len(stats) > 1:
        trajcons = localTrajectoryConstraints() # default set of constraints
        checker = EventChecker(traj_constraints=trajcons)
        rp = loadPlatepar(ppdir, stats[0])
        tp = loadPlatepar(ppdir, stats[1])
        fovcheck = checker.checkFOVOverlap(rp, tp)
        distcheck = checker.stationRangeCheck(rp, tp)    
        if fovcheck is True and distcheck is True:
            print(f'{stats[0]} overlaps with {stats[1]}')
    else:
        ci = cd.SiteInfo()
        loc_cam =  ci.getCameraLocAndDir(stats[0])
        overlaps = getOverlappingStations(datadir, stats[0])
        print(f'{stats[0]} overlaps with {len(overlaps)} stations')

        startdt = datetime.datetime(2022,7,1)
        enddt = datetime.datetime(2022,11,1)
        cfd = loadUFOdata(datadir, startdt, enddt, loc_cam)
        sngls = loadSingleData(datadir, overlaps, startdt, enddt)

        keepers = []
        for idx,rw in cfd.iterrows():
            tmpd = sngls[abs(sngls.Dtstamp - rw.Dtstamp) < 5]
            tmpd = tmpd.drop_duplicates()
            if len(tmpd) > 0:
                cfdsubset = {'Loc_Cam': rw.Loc_Cam, 'Dtstamp': rw.Dtstamp}
                keepers.append({'cfd': cfdsubset, 'sngl': tmpd})

