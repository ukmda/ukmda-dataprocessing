#
# testing the trajectory solver for UFO data
#
import sys
import os
import re
import numpy as np
import fnmatch
from UFOHandler import ReadUFOAnalyzerXML as ua
# sys.path.append('e:/dev/meteorhunting/WesternMeteorPyLib')
import wmpl.Trajectory.Trajectory as tra
import wmpl.Utils.TrajConversions as trajconv
import configparser as cfg


def find_files(path: str, glob_pat: str, ignore_case: bool = False):
    rule = re.compile(fnmatch.translate(glob_pat), re.IGNORECASE) if ignore_case \
        else re.compile(fnmatch.translate(glob_pat))
    return [n for n in os.listdir(os.path.expanduser(path)) if rule.match(n)]


def ufoTrajSolver(outdir, fnames):
    """
    Calculate trajectory and orbit for UFO-Analyser based output.

    Arguments:
        outdir: [string] where to put the reports and graphs

        fnames: [list of strings] list of two or more A.XML files

    example usage:

    python ufoTrajSolver c:\temp M20201011_123456_AliceA.xml M20201011_12344_BobA.xml M20201011_12347_JimA.xml
    python ufoTrajSolver c:\temp folder_with_axmls
    """
    verbose = False
    monte_carlo = False
    max_toff = 5  # need at least 5s for UFO data !
    etv = True

    config = cfg.ConfigParser()
    config.read('orbitsolver.ini')

    if config['orbitcalcs']['verbose'] in ['True', 'TRUE', 'true']:
        verbose = True
    if config['orbitcalcs']['use_mc'] in ['True', 'TRUE', 'true']:
        monte_carlo = True

    # if there's only one filename, assume its a folder containing the data
    if len(fnames) == 1:
        pth = fnames[0]
        fnames = find_files(pth, '*.xml', True)

    num = len(fnames)
    stations = []
    lat = np.empty(num)
    lon = np.empty(num)
    ele = np.empty(num)
    tt = []
    ang1 = []
    ang2 = []
    mag = []
    fcount = np.empty(num)

    dd = np.empty(num, dtype='object')
    i = 0
    for fn in fnames:
        print(fn)
        fullname = os.path.join(pth, fn)
        dd[i] = ua.UAXml(fullname)
        i = i + 1

    # date from  1st station, used to create output folder and set reference point
    dtim = dd[0].getDateTime()
    fname = dtim.strftime('%Y%m%d_%H%M%S')
    outdir = os.path.join(outdir, fname)

    # Reference julian date. This shouldbe close to the start-time of the meteor, hence using dtim
    # note: processing will adjust this to match the earliest start time of any events
    # so the JD in the report may not exactly match this value
    reftime = dtim.timestamp()
    jdt_ref = trajconv.datetime2JD(dtim)

    # Inputs are RA/Dec or Alt/Az as read from UFOA data
    # useful options are 1=RA/Dec, 2=az/ev measured N->E/Horiz up
    meastype = 2

    # read data from each station
    for i in range(num):
        # read station location data and convert to radians
        station, _, _, lat[i], lon[i], ele[i] = dd[i].getStationDetails()
        stations.append(station)
        lon[i] = np.radians(lon[i])
        lat[i] = np.radians(lat[i])

        # read meteor time, magnitude, RA/Dec or Alt/Az and convert to radians
        _, stt, sra, sdec, smag, fcount[i] = dd[i].getPathVector(0, equat=meastype)
        tt.append(stt)
        ang1.append(sra)
        ang2.append(sdec)
        mag.append(smag)

        ang1[i] = np.radians(ang1[i])
        ang2[i] = np.radians(ang2[i])

        # convert times to offsets from ref time
        tt[i] = tt[i] - reftime

    # Init new trajectory solving/ MC is much slower but a little more accurate
    traj_solve = tra.Trajectory(jdt_ref, meastype=meastype,
        save_results=True, monte_carlo=monte_carlo, show_plots=False,
        output_dir=outdir, verbose=verbose, max_toffset=max_toff, estimate_timing_vel=etv)

    # Set input points for the sites
    for i in range(num):
        traj_solve.infillTrajectory(ang1[i], ang2[i], tt[i], lat[i], lon[i], ele[i],
            station_id=stations[i], magnitudes=mag[i])

    # and now solve it. This routine also creates all the output files
    traj_solve.run()


if __name__ == "__main__":

    if len(sys.argv) > 2:
        args = sys.argv[2:]
        ufoTrajSolver(sys.argv[1], args)
    else:
        # TEST CASE ###
        ##########################################################################################################

        # import time
        # from wmpl.Utils.TrajConversions import equatorialCoordPrecession_vect, J2000_JD

        # TEST EVENT
        ###############
        # Reference julian date
        jdt_ref = 2458601.365760937799

        # Inputs are RA/Dec
        meastype = 1

        # Measurements
        station_id1 = "RU0001"
        time1 = np.array([0.401190, 0.441190, 0.481190, 0.521190, 0.561190, 0.601190, 0.641190, 0.681190,
                        0.721190, 0.761190, 0.801190, 0.841190, 0.881190, 0.921190, 0.961190, 1.001190,
                        1.041190, 1.081190, 1.121190, 1.161190, 1.201190, 1.241190, 1.281190, 1.321190,
                        1.361190, 1.401190, 1.441190, 1.561190, 1.601190, 1.641190, 1.721190, 1.761190,
                        1.841190])
        ra1 = np.array([350.35970, 350.71676, 351.29184, 351.58998, 352.04673, 352.50644, 352.91289, 353.37336,
                        353.80532, 354.23339, 354.69277, 355.07317, 355.49321, 355.93473, 356.32148, 356.74755,
                        357.13866, 357.51363, 357.89944, 358.34052, 358.72626, 359.11597, 359.53391, 359.88343,
                        000.35106, 000.71760, 001.05526, 002.17105, 002.58634, 002.86315, 003.58752, 003.90806,
                        004.48084])
        dec1 = np.array([+74.03591, +73.94472, +73.80889, +73.73877, +73.59830, +73.46001, +73.35001, +73.22812,
                        +73.10211, +72.98779, +72.84568, +72.72924, +72.59691, +72.46677, +72.33622, +72.18147,
                        +72.04381, +71.91015, +71.77648, +71.63370, +71.47512, +71.32664, +71.16185, +71.03236,
                        +70.84506, +70.67285, +70.54194, +70.01219, +69.80856, +69.69043, +69.38316, +69.23522,
                        +68.93025])

        station_id2 = "RU0002"
        time2 = np.array([0.000000, 0.040000, 0.080000, 0.120000, 0.160000, 0.200000, 0.240000, 0.280000,
                        000.320000, 0.360000, 0.400000, 0.440000, 0.480000, 0.520000, 0.560000, 0.600000,
                        000.640000, 0.680000, 0.720000, 0.760000, 0.800000, 0.840000, 0.880000, 0.920000,
                        000.960000, 1.000000, 1.040000, 1.080000, 1.120000, 1.160000, 1.200000, 1.240000,
                        001.280000, 1.320000, 1.360000, 1.400000, 1.440000, 1.480000, 1.520000, 1.560000,
                        001.600000, 1.640000, 1.680000, 1.720000, 1.760000, 1.800000, 1.840000, 1.880000,
                        001.920000, 1.960000, 2.000000, 2.040000, 2.080000, 2.120000, 2.160000, 2.200000,
                        002.240000, 2.280000, 2.320000, 2.360000, 2.400000, 2.440000, 2.480000, 2.520000])
        ra2 = np.array([081.27325, 81.20801, 81.06648, 81.03509, 80.93281, 80.87338, 80.74776, 80.68456,
                        080.60038, 80.52306, 80.45021, 80.35990, 80.32309, 80.21477, 80.14311, 80.06967,
                        079.98169, 79.92234, 79.84210, 79.77507, 79.72752, 79.62422, 79.52738, 79.48236,
                        079.39613, 79.30580, 79.23434, 79.20863, 79.12019, 79.03670, 78.94849, 78.89223,
                        078.84252, 78.76605, 78.69339, 78.64799, 78.53858, 78.53906, 78.47469, 78.39496,
                        078.33473, 78.25761, 78.23964, 78.17867, 78.16914, 78.07010, 78.04741, 77.95169,
                        077.89130, 77.85995, 77.78812, 77.76807, 77.72458, 77.66024, 77.61543, 77.54208,
                        077.50465, 77.45944, 77.43200, 77.38361, 77.36004, 77.28842, 77.27131, 77.23300])
        dec2 = np.array([+66.78618, +66.66040, +66.43476, +66.21971, +66.01550, +65.86401, +65.63294, +65.43265,
                        +65.25161, +65.01655, +64.83118, +64.62955, +64.45051, +64.23361, +64.00504, +63.81778,
                        +63.61334, +63.40714, +63.19009, +62.98101, +62.76420, +62.52019, +62.30266, +62.05585,
                        +61.84240, +61.60207, +61.40390, +61.22904, +60.93950, +60.74076, +60.53772, +60.25602,
                        +60.05801, +59.83635, +59.59978, +59.37846, +59.10216, +58.88266, +58.74728, +58.45432,
                        +58.18503, +57.97737, +57.72030, +57.55891, +57.31933, +56.98481, +56.85845, +56.58652,
                        +56.36153, +56.15409, +55.88252, +55.66986, +55.46593, +55.20145, +54.91643, +54.69826,
                        +54.49443, +54.25651, +54.06386, +53.86395, +53.70069, +53.47312, +53.33715, +53.20272])

        # Convert measurement to radians
        ra1 = np.radians(ra1)
        dec1 = np.radians(dec1)

        ra2 = np.radians(ra2)
        dec2 = np.radians(dec2)

        # SITES INFO

        lon1 = np.radians(37.315140)
        lat1 = np.radians(44.890740)
        ele1 = 26.00

        lon2 = np.radians(38.583580)
        lat2 = np.radians(44.791620)
        ele2 = 240.00

        ###

        # Init new trajectory solving
        traj_solve = tra.Trajectory(jdt_ref, meastype=meastype, save_results=True, monte_carlo=False, show_plots=False)

        # Set input points for the first site
        traj_solve.infillTrajectory(ra1, dec1, time1, lat1, lon1, ele1, station_id=station_id1)

        # Set input points for the second site
        traj_solve.infillTrajectory(ra2, dec2, time2, lat2, lon2, ele2, station_id=station_id2)

        traj_solve.run()

        # TEST
        print('saving results')
        fig_pickle_dict = traj_solve.savePlots('c:/temp/test', 'myfile', show_plots=False, ret_figs=False)
