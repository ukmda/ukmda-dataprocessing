#
# Simple filter of single-station or match data by various criteria
#
import pandas as pd
import argparse
import datetime 
import os
import glob 
import shutil
import matplotlib.pyplot as plt # noqa: F401 pyplot used by AggregateAndPlot functions

from utils.convertSolLon import sollon2jd
from wmpl.Utils.TrajConversions import jd2Date
from wmpl.Trajectory.AggregateAndPlot import loadTrajectoryPickles, generateTrajectoryPlots
from wmpl.Utils.Pickling import loadPickle
from Utils import showerAssociation
import RMS.ConfigReader as cr

from utils.plotRMSOrbits import processFile
import fileformats.CameraDetails as cd


class TrajQualityParams(object):
    def __init__(self):
        # Minimum number of points on the trajectory for the station with the most points
        self. min_traj_points = 6
        # Minimum convergence angle (deg)
        self. min_qc = 5.0
        # Maximum eccentricity
        self. max_e = 1.5
        # Maximum radiant error (deg)
        self. max_radiant_err = 2.0
        # Maximum geocentric velocity error (percent)
        self. max_vg_err = 10.0
        # Begin/end height filters (km)
        self. max_begin_ht = 160
        self. min_end_ht = 20


def writeFTPheader(outf):
    outf.write('Meteor Count = 000000\n')
    outf.write('-----------------------------------------------------\n')
    outf.write('Processed with filterData\n')
    outf.write('-----------------------------------------------------\n')
    outf.write('FF  folder = not used\n')
    outf.write('CAL folder = not used\n')
    outf.write('-----------------------------------------------------\n')
    outf.write('FF  file processed\n')
    outf.write('CAL file processed\n')
    outf.write('Cam# Meteor# #Segments fps hnr mle bin Pix/fm Rho Phi\n')
    outf.write('Per segment:  Frame# Col Row RA Dec Azim Elev Inten Mag\n')
    outf.write('-------------------------------------------------------\n')
    return 


def getSingleStnFTPdetect(fname, archdir, cinfo):
    lines_we_want = []
    fnsplits = fname.split('_')
    camid = fnsplits[1]
    datestr = fnsplits[2]
    timestr = fnsplits[3]
    if int(timestr) < 120000:
        dt=datetime.datetime.strptime(datestr, '%Y%m%d') + datetime.timedelta(-1)
        datestr = dt.strftime('%Y%m%d')
    fldr = cinfo.getFolder(camid)
    fullpath = os.path.join(archdir, fldr, datestr[:4], datestr[:6], datestr)
    ftps = glob.glob1(fullpath, 'FTPdetect*.txt')
    if len(ftps) == 0:
        return lines_we_want
    print(fullpath, ftps[0])
    with open(os.path.join(fullpath, ftps[0]), 'r') as inf:
        lines = inf.readlines()
    foundit = False
    for li in lines:
        if fname in li:
            foundit = True
        if foundit is True:
            lines_we_want.append(li)
            if '-----------' in li:
                foundit = False
                break
    if len(lines_we_want) == 0:
        print('no data found')
        return lines_we_want
    if '-----------' not in lines_we_want[-1]:
        lines_we_want.append('-------------------------------------------------------\n')
    return lines_we_want


# filterSingleData(2022,204,5,39.2,5,69.2,5)

# filter single-station data for a given year. 
def filterSingleData(yr, ra=None, dra=5, dec=None, ddec=5, sollon=None, dsl=5, save_plots=True):
    df = pd.DataFrame()
    if ra is not None and (ra < 0 or ra > 360):
        print('invalid RA - must be in the range 0<=RA<360')
        return df
    if dec is not None and (dec < -90 or dec > 90):
        print('invalid dec - must be in the range -90<dec<+90')
        return df
    if sollon is not None and (sollon < 0 or sollon > 180):
        print('invalid sollon - must be in the range 0<=sollon<180')
        return df
    dt = datetime.datetime.now()
    dt = dt.replace(year=yr)
    mth = dt.month
    jdt = sollon2jd(yr, mth, sollon)
    pkdt = jd2Date(jdt, dt_obj=True)    
    srcfile = f'https://archive.ukmeteornetwork.co.uk/browse/parquet/singles-{yr}.parquet.gzip'
    df = pd.read_parquet(srcfile)
    # filter by RA if requested
    if ra is not None:
        df = df[(df.Ra1 >= (ra - dra)) | (df.Ra2 >= (ra - dra))]
        df = df[(df.Ra1 <= (ra + dra)) | (df.Ra2 <= (ra + dra))]
    if dec is not None:
        df = df[(df.Dec1 >= (dec - ddec)) | (df.Dec2 >= (dec - ddec))]
        df = df[(df.Dec1 <= (dec + ddec)) | (df.Dec2 <= (dec + ddec))]
    if sollon is not None:
        d1 = pkdt + datetime.timedelta(-dsl)
        d2 = pkdt + datetime.timedelta(dsl)
        df = df[df.Dtstamp >= d1.timestamp()]
        df = df[df.Dtstamp <= d2.timestamp()]
    if len(df) > 0:
        # find the ftpdetect and extract the relevant rows
        archdir = os.getenv('ARCHDIR', default='/home/ec2-user/ukmon-shared/archive')
        cinfo = cd.SiteInfo()
        outdtstr = pkdt.strftime("%Y%m%d")
        outfname = (f'./FTPdetectinfo_UK0000_{outdtstr}_000000_000000.txt')
        with open(outfname, 'w') as outf:
            writeFTPheader(outf)
            for _, row in df.iterrows(): 
                gotlines = getSingleStnFTPdetect(row['Filename'], archdir, cinfo)
                for li in gotlines:
                    outf.write(li)

        if save_plots is True: 
            rmsloc = os.getenv('RMS_LOC', default='/home/ec2-user/src/RMS')
            config = cr.loadConfigFromDirectory('.config', rmsloc)
            showerAssociation(config, outfname, save_plots = save_plots)
            outfname = os.path.join('.', f'singles-{yr}-{ra}-{dec}-{sollon}.csv')
            print(f'writing data to {outfname}')
            outdf.to_csv(outfname, index=False)
    else:
        print('no matches')
    return df


# mydf=filterMatchData(2022,204,5,29.2,5,69.2,5,14,3)
# filter matched data for a given year. 
def filterMatchData(yr, ra=None, dra=5, dec=None, ddec=5, sollon=None, dsl=5, vg=None, dvg=3, save_plots=True):
    df = pd.DataFrame()
    if ra is not None and (ra < 0 or ra > 360):
        print('invalid RA - must be in the range 0<=RA<360')
        return df
    if dec is not None and (dec < -90 or dec > 90):
        print('invalid dec - must be in the range -90<dec<+90')
        return df
    if sollon is not None and (sollon < 0 or sollon > 180):
        print('invalid sollon - must be in the range 0<=sollon<180')
        return df
    if vg is not None and (vg < 5 or sollon > 100):
        print('invalid vg - must be in the range 5<=vg<=99')
        return df
    srcfile = f'https://archive.ukmeteornetwork.co.uk/browse/parquet/matches-full-{yr}.parquet.gzip'
    df = pd.read_parquet(srcfile)
    # filter by RA if requested
    if ra is not None:
        df = df[df._ra_o >= (ra - dra)]
        df = df[df._ra_o <= (ra + dra)]
    if dec is not None:
        df = df[df._dc_o >= (dec - ddec)]
        df = df[df._dc_o <= (dec + ddec)]
    if vg is not None:
        df = df[df._vg >= (vg - dvg)]
        df = df[df._vg <= (vg + dvg)]
    if sollon is not None:
        df = df[df._sol >= (sollon - dsl)]
        df = df[df._sol <= (sollon + dsl)]
    if len(df) > 0:
        # find the ftpdetect and extract the relevant rows
        tmppth='./tmppickles'
        if os.path.isdir(tmppth):
            shutil.rmtree(tmppth)
        os.makedirs(tmppth, exist_ok=True)
        matchdir = os.getenv('MATCHDIR', default='/home/ec2-user/ukmon-shared/matches')
        picklefiles=[]
        for _, row in df.iterrows(): 
            orbname = row.orbname
            dtstr = orbname[:8]
            fullpath = os.path.join(matchdir,'RMSCorrelate','trajectories', 
                dtstr[:4], dtstr[:6], dtstr, orbname)
            picklefile = os.path.join(fullpath, orbname[:15]+'_trajectory.pickle')
            outpick = os.path.join(tmppth, orbname[:15]+'_trajectory.pickle')
            shutil.copy2(picklefile, outpick)
            picklefiles.append(outpick)
        if save_plots is True:
            print(f'creating plots in {tmppth}')
            traj_quality_params = TrajQualityParams()
            traj_list = loadTrajectoryPickles(tmppth, traj_quality_params, verbose=True)
            generateTrajectoryPlots(tmppth, traj_list, plot_showers=True, time_limited_plot=False)
            plotAllOrbits(picklefiles, tmppth)

            outfname = os.path.join(tmppth, f'matches-{yr}-{ra}-{dec}-{sollon}-{vg}.csv')
            print(f'writing data to {outfname}')
            outdf.to_csv(outfname, index=False)

    return df


def plotAllOrbits(picklefiles, tmppth):
    with open(os.path.join(tmppth, 'orbeles.csv'), 'w') as csvf:
        csvf.write('_a,_e,_incl,_peri,_node\n')
        for pf in picklefiles:
            traj = loadPickle(*os.path.split(pf))
            orb = traj.orbit
            csvf.write(f'{orb.a}, {orb.e}, {orb.i}, {orb.peri}, {orb.node}\n')
    processFile(os.path.join(tmppth, 'orbeles.csv'), tmppth)
    return


if __name__ == '__main__':
    ### COMMAND LINE ARGUMENTS
    # Init the command line arguments parser
    arg_parser = argparse.ArgumentParser(description="Filter single or matched data by various criteria")

    arg_parser.add_argument('-t', '--type', metavar='DATATYPE', type=str,
        help="Data to filter - matched or single")

    arg_parser.add_argument('-y', '--year', metavar='YEAR', type=int,
        help="year to filter for")

    arg_parser.add_argument('-r', '--ra', metavar='RA', type=float,
        help="RA to centre around")
    arg_parser.add_argument('-dr', '--dra', metavar='DRA', type=float,
        help="+/- range of Dec", default=5)
    arg_parser.add_argument('-d', '--dec', metavar='DEC', type=float,
        help="DEC to centre around")
    arg_parser.add_argument('-dd', '--ddec', metavar='DDEC', type=float,
        help="+/- range of Dec", default=5)

    arg_parser.add_argument('-s', '--sollon', metavar='SOLLON', type=float,
        help="RA to centre around")
    arg_parser.add_argument('-ds', '--dsl', metavar='DSL', type=float,
        help="+/- range of Dec", default=5)
    arg_parser.add_argument('-v', '--vg', metavar='VG', type=float,
        help="DEC to centre around")
    arg_parser.add_argument('-dv', '--dvg', metavar='DVG', type=float,
        help="+/- range of Dec", default=3)
    args = arg_parser.parse_args()

    if args.year is None:
        args.year = 2022
    print(args)
    
    if args.type.upper() == 'MATCHED':
        outdf = filterMatchData(args.year, args.ra, args.dra, args.dec, args.ddec, 
            args.sollon, args.dsl, args.vg, args.dvg, save_plots=True)
    elif args.type.upper() == 'SINGLE':
        outdf = filterSingleData(args.year, args.ra, args.dra, args.dec, args.ddec, 
            args.sollon, args.dsl, save_plots=True)
