# simple python script to analyse the rms correlator logs

import os
import argparse
import datetime
import glob
import numpy as np
import pandas as pd

from wmpl.Utils.Pickling import loadPickle


def getBinRuntimes(logdir, logdt):
    logfiles = os.listdir(logdir)
    logfiles = [x for x in logfiles if f'correlate_rms_{logdt}' in x]
    if len(logfiles) == 0:
        print(f'nothing to analyse matching {logdt}')
        return 
    starttime = None
    gottb = False
    analytics = []
    thisrow={}
    for logfile in logfiles:
        if logfile[-4:] =='.log':
            continue
        print(f'reading {logfile}')
        loglines = open(os.path.join(logdir, logfile), 'r').readlines()
        for lin in loglines:
            if 'PROCESSING TIME BIN' in lin and gottb is False:
                gottb = True
                starttime = datetime.datetime.strptime(lin[:19], '%Y/%m/%d %H:%M:%S')
                thisrow['starttime'] = starttime
                print(f'processing started {starttime}')

            if ':1841' in lin and gottb is True:
                vals = ' '.join(lin.split()).split()
                thisrow['dt_beg'] = datetime.datetime.strptime(vals[5] + ' ' + vals[6][:8], '%Y-%m-%d %H:%M:%S')
                thisrow['dt_end'] = datetime.datetime.strptime(vals[7] + ' ' + vals[8][:8], '%Y-%m-%d %H:%M:%S')
                print(f'bucket start {thisrow["dt_beg"]}')

            if 'Loaded' in lin and 'trajectories in' in lin and gottb is True:
                vals = ' '.join(lin.split()).split()
                thisrow['trajs'] = int(vals[6])
                print(f'loaded trajectories {thisrow["trajs"]}')

            if 'Analysing' in lin and 'observations...' in lin and gottb is True:
                vals = ' '.join(lin.split()).split()
                thisrow['obs'] = int(vals[5])
                print(f'loaded observations {thisrow["obs"]}')

            if 'CHECKING IF PREV' in lin and gottb is True:
                loadtime = datetime.datetime.strptime(lin[:19], '%Y/%m/%d %H:%M:%S')
                thisrow['loadsecs'] = (loadtime - starttime).seconds

            if 'SOLVING' in lin and 'TRAJECTORIES' in lin and gottb is True:
                analtime = datetime.datetime.strptime(lin[:19], '%Y/%m/%d %H:%M:%S')
                thisrow['analsecs'] = (analtime - loadtime).seconds

            if 'SOLVING RUN DONE' in lin and gottb is True:
                donetime = datetime.datetime.strptime(lin[:19], '%Y/%m/%d %H:%M:%S')
                thisrow['donesecs'] = (donetime - analtime).seconds
                analytics.append(thisrow)
                print(thisrow)
                thisrow = {}
                gottb = False
           
    for logfile in logfiles:
        if logfile[-4:] !='.log':
            continue
        print(f'reading {logfile}')
        loglines = open(os.path.join(logdir, logfile), 'r').readlines()
        for lin in loglines:
            if 'PROCESSING TIME BIN' in lin and starttime is not None:
                gottb = True
                starttime = datetime.datetime.strptime(lin[:19], '%Y/%m/%d %H:%M:%S')
                thisrow['starttime'] = starttime

            if ':1841' in lin and gottb is True:
                vals = ' '.join(lin.split()).split()
                thisrow['dt_beg'] = datetime.datetime.strptime(vals[5] + ' ' + vals[6][:8], '%Y-%m-%d %H:%M:%S')
                thisrow['dt_end'] = datetime.datetime.strptime(vals[7] + ' ' + vals[8][:8], '%Y-%m-%d %H:%M:%S')

            if 'Loaded' in lin and 'trajectories in' in lin and gottb is True:
                vals = ' '.join(lin.split()).split()
                thisrow['trajs'] = int(vals[6])

            if 'Analysing' in lin and 'observations...' in lin and gottb is True:
                vals = ' '.join(lin.split()).split()
                thisrow['obs'] = int(vals[5])

            if 'CHECKING IF PREV' in lin and gottb is True:
                loadtime = datetime.datetime.strptime(lin[:19], '%Y/%m/%d %H:%M:%S')
                thisrow['loadsecs'] = (loadtime - starttime).seconds

            if 'SOLVING' in lin and 'TRAJECTORIES' in lin and gottb is True:
                analtime = datetime.datetime.strptime(lin[:19], '%Y/%m/%d %H:%M:%S')
                thisrow['analsecs'] = (analtime - loadtime).seconds

            if 'SOLVING RUN DONE' in lin and gottb is True:
                donetime = datetime.datetime.strptime(lin[:19], '%Y/%m/%d %H:%M:%S')
                thisrow['donesecs'] = (donetime - analtime).seconds
                analytics.append(thisrow)
                thisrow = {}
                gottb = False
    for rw in analytics:
        print(rw)
    return analytics
    

def getSolverRunDurations2(logdir, logdt):
    logfiles = os.listdir(logdir)
    logfiles = [x for x in logfiles if f'correlate_rms_{logdt}' in x]
    for logfile in logfiles:
        if logfile[-4:] =='.log':
            continue
        print(f'reading {logfile}')
        loglines = open(logfile, 'r').readlines()
        starttime = None
        runtime = 0
        gottb = False
        for lin in loglines:
            if gottb:
                print(lin.strip())
                gottb = False

            if 'Using directory' in lin:
                starttime = datetime.datetime.strptime(lin[:19], '%Y/%m/%d %H:%M:%S')
                print(f'\nload database {starttime} - {lin.strip()}')

            if 'ALL TIME BINS' in lin and starttime is not None:
                endtime = datetime.datetime.strptime(lin[:19], '%Y/%m/%d %H:%M:%S')
                runtime = (endtime - starttime).seconds
                print(f'scan folders {runtime} - {lin.strip()}')
                starttime = endtime

            if 'PROCESSING TIME BIN' in lin and starttime is not None:
                gottb = True
                endtime = datetime.datetime.strptime(lin[:19], '%Y/%m/%d %H:%M:%S')
                runtime = (endtime - starttime).seconds
                print(f'done scan folders {runtime} - {lin.strip()}')
                starttime = endtime

            if 'Loaded' in lin and 'trajectories in' in lin and starttime is not None:
                print(lin.strip())

            if 'Analysing' in lin and 'observations...' in lin and starttime is not None:
                print(lin.strip())

            if 'CHECKING IF PREV' in lin and starttime is not None:
                runtime = (endtime - starttime).seconds
                print(f'done loading {runtime} - {lin.strip()}')
                starttime = endtime

            if 'PAIRING OBSERVATIONS' in lin and starttime is not None:
                endtime = datetime.datetime.strptime(lin[:19], '%Y/%m/%d %H:%M:%S')
                runtime = (endtime - starttime).seconds
                print(f'done checking prev {runtime} - {lin.strip()}')
                starttime = endtime

            if 'MERGING BROKEN' in lin and starttime is not None:
                endtime = datetime.datetime.strptime(lin[:19], '%Y/%m/%d %H:%M:%S')
                runtime = (endtime - starttime).seconds
                print(f'done pairing {runtime} - {lin.strip()}')
                starttime = endtime

            if 'SOLVING' in lin and 'TRAJECTORIES' in lin and starttime is not None: 
                endtime = datetime.datetime.strptime(lin[:19], '%Y/%m/%d %H:%M:%S')
                runtime = (endtime - starttime).seconds
                print(f'done merging broken {runtime} - {lin.strip()}')
                starttime = endtime

            if 'SOLVING RUN DONE' in lin and starttime is not None: 
                endtime = datetime.datetime.strptime(lin[:19], '%Y/%m/%d %H:%M:%S')
                runtime = (endtime - starttime).seconds
                print(f'done solving {runtime} - {lin.strip()}\n')
                starttime = endtime

            if 'Total run time' in lin and starttime is not None:
                endtime = datetime.datetime.strptime(lin[:19], '%Y/%m/%d %H:%M:%S')
                runtime = (endtime - starttime).seconds
                print(f'done whole pass {runtime} - {lin.strip()}\n\n')
                starttime = endtime
            
    for logfile in logfiles:
        if logfile[-4:] !='.log':
            continue
        print(f'reading {logfile}')
        loglines = open(logfile, 'r').readlines()
        starttime = None
        runtime = 0
        gottb = False
        for lin in loglines:
            if gottb:
                print(lin)
                gottb = False

            if 'Using directory' in lin:
                starttime = datetime.datetime.strptime(lin[:19], '%Y/%m/%d %H:%M:%S')
                print(f'load database {starttime} - {lin.strip()}')

            if 'ALL TIME BINS' in lin and starttime is not None:
                endtime = datetime.datetime.strptime(lin[:19], '%Y/%m/%d %H:%M:%S')
                runtime = (endtime - starttime).seconds
                print(f'scan folders {runtime} - {lin.strip()}')
                starttime = endtime

            if 'PROCESSING TIME BIN' in lin and starttime is not None:
                gottb = True
                endtime = datetime.datetime.strptime(lin[:19], '%Y/%m/%d %H:%M:%S')
                runtime = (endtime - starttime).seconds
                print(f'\ndone scan folders {runtime} - {lin.strip()}')
                starttime = endtime

            if 'Loaded' in lin and 'trajectories in' in lin and starttime is not None:
                print(lin.strip())

            if 'Analysing' in lin and 'observations...' in lin and starttime is not None:
                print(lin.strip())

            if 'CHECKING IF PREV' in lin and starttime is not None:
                runtime = (endtime - starttime).seconds
                print(f'done loading {runtime} - {lin.strip()}')
                starttime = endtime

            if 'PAIRING OBSERVATIONS' in lin and starttime is not None:
                endtime = datetime.datetime.strptime(lin[:19], '%Y/%m/%d %H:%M:%S')
                runtime = (endtime - starttime).seconds
                print(f'done checking prev {runtime} - {lin.strip()}')
                starttime = endtime

            if 'MERGING BROKEN' in lin and starttime is not None:
                endtime = datetime.datetime.strptime(lin[:19], '%Y/%m/%d %H:%M:%S')
                runtime = (endtime - starttime).seconds
                print(f'done pairing {runtime} - {lin.strip()}')
                starttime = endtime

            if 'SOLVING' in lin and 'TRAJECTORIES' in lin and starttime is not None: 
                endtime = datetime.datetime.strptime(lin[:19], '%Y/%m/%d %H:%M:%S')
                runtime = (endtime - starttime).seconds
                print(f'done merging broken {runtime} - {lin.strip()}')
                starttime = endtime

            if 'SOLVING RUN DONE' in lin and starttime is not None: 
                endtime = datetime.datetime.strptime(lin[:19], '%Y/%m/%d %H:%M:%S')
                runtime = (endtime - starttime).seconds
                print(f'done solving {runtime} - {lin.strip()}\n')
                starttime = endtime

            if 'Total run time' in lin and starttime is not None:
                endtime = datetime.datetime.strptime(lin[:19], '%Y/%m/%d %H:%M:%S')
                runtime = (endtime - starttime).seconds
                print(f'done whole pass {runtime} - {lin.strip()}\n\n')
                starttime = endtime
            
    return 
    

def getSolverRunDurations(logfilename):
    loglines = open(os.path.expanduser(logfilename), 'r').readlines()
    loglines = [lin for lin in loglines if 'SOLVING' in lin or '1)' in lin or '2)' in lin or  # noqa: W504
                'MERGING' in lin or 'SOLVED' in lin or 'RUN DONE' in lin or 'Using directory' in lin or  # noqa: W504
                'PROCESSING TIME BIN' in lin]
    inprogress = False
    recheck_time = 0    
    pair_time = 0
    merge_time = 0
    solve_time = 0

    rechecks = []
    pairs = []
    merges = []
    solves = []
    trajcounts = []


    print('task, duration(s),trajectories')
    for lin in loglines:

        if '1)' in lin: # start checking existing traj
            evt = lin.split('-')
            recheck_time = datetime.datetime.strptime(evt[0], '%Y/%m/%d %H:%M:%S')

        if '2)' in lin: # end checking existing traj, start pairing new detections
            evt = lin.split('-')
            pair_time = datetime.datetime.strptime(evt[0], '%Y/%m/%d %H:%M:%S')
            if recheck_time == 0:
                recheck_time = pair_time
            recheck_time = pair_time - recheck_time
            rechecks.append(recheck_time.seconds)
            #print(f'checkPrev, {recheck_time.seconds}')

        if 'MERGING' in lin: # end checking existing traj, start pairing new detections
            evt = lin.split('-')
            merge_time = datetime.datetime.strptime(evt[0], '%Y/%m/%d %H:%M:%S')
            pair_time = merge_time - pair_time
            pairs.append(pair_time.seconds)
            #print(f'Pairing, {pair_time.seconds}')

        if 'TRAJECTORIES' in lin and 'SOLVING' in lin:
            evt = lin.split('-')
            solve_time = datetime.datetime.strptime(evt[0], '%Y/%m/%d %H:%M:%S')
            merge_time = solve_time - merge_time
            merges.append(merge_time.seconds)
            #print(f'Merging, {merge_time.seconds}')
            trajcounts.append(int(evt[-1].strip().split(' ')[1]))
            inprogress = True
        if 'RUN DONE' in lin:
            if inprogress:
                evt = lin.split('-')
                done_time = datetime.datetime.strptime(evt[0], '%Y/%m/%d %H:%M:%S')
                solve_time = done_time - solve_time
                solves.append(solve_time.seconds)
                #print(f'Solving, {solve_time.seconds}, {trajcount[-1]}')
                inprogress = False

    print(f'max check {max(rechecks)/60:.2f}')
    print(f'max pair {max(pairs)/60:.2f}')
    print(f'max merge {max(merges)/60:.2f}')
    print(f'max solve {max(solves)/60:.2f}')
    print(f'max traj {max(trajcounts)}')
    print("")
    print(f'ave check {np.average(rechecks)/60:.2f}')
    print(f'ave pair {np.average(pairs)/60:.2f}')
    print(f'ave merge {np.average(merges)/60:.2f}')
    print(f'ave solve {np.average(solves)/60:.2f}')
    print(f'ave traj {np.average(trajcounts):.2f}')

    return 


def findAllSolvedEvents(logf, logdir):
    loglines = open(os.path.expanduser(logf), 'r').readlines()
    loglines = [lin for lin in loglines if 'Solving the trajectory' in lin or 'Saving trajectory' in lin]
    solvedtraj = []
    for lin in loglines:
        if 'Solving the trajectory' in lin:
            evtdate = lin.split(' ')[-1][:-4]
            evtdate = datetime.datetime.strptime(evtdate, '%Y-%m-%dZ%H:%M:%S')
            solvedat = lin.split('-')[0]
            solvedat = datetime.datetime.strptime(solvedat, '%Y/%m/%d %H:%M:%S')
        if 'Saving trajectory' in lin:
            #print(f"{evtdate} solved at {solvedat.replace(' ','Z')}")
            solvedtraj.append({'trajdate': evtdate, 'solvedat': solvedat})
    df = pd.DataFrame(solvedtraj)
    df.sort_values(by=['trajdate'], inplace=True)
    df.to_csv(os.path.join(logdir, 'solvedevents.csv'), index=False)
    return df


def getAllTrajStations(srcdir, logdir):
    processedtraj = glob.glob(os.path.join(srcdir,'*.pickle'))
    phase1done = []
    for trajfile in processedtraj:
        traj = loadPickle(*os.path.split(trajfile))
        statids = []
        for obs in traj.observations:
            statids.append(obs.station_id)
        trajtime = datetime.datetime.strptime(os.path.split(trajfile)[1][:15], '%Y%m%d_%H%M%S')
        phase1done.append({'traj': trajtime, 'stations': statids})
    df = pd.DataFrame(phase1done)
    df.sort_values(by=['traj'], inplace=True)
    df.to_csv(os.path.join(logdir, 'trajstations.csv'), index=False)
    return df


def getFTPtimes(logdir):
    ftptimesdata = open(os.path.join(logdir, 'ftpdetecttimes.txt'), 'r').readlines()
    ftptimes = []
    for li in ftptimesdata:
        spls = li.split()
        evtdate = spls[5] + ' ' + spls[6] + ' 2024 ' + spls[7]
        ftpdate = datetime.datetime.strptime(evtdate, '%b %d %Y %H:%M')
        fname = os.path.split(spls[-1])[1]
        spls2 = fname.split('_')
        camid = spls2[1]
        filedate = datetime.datetime.strptime(spls2[2] + '_' + spls2[3], '%Y%m%d_%H%M%S')
        ftptimes.append({'camid':camid, 'filedate':filedate, 'uploaddate':ftpdate})

    df = pd.DataFrame(ftptimes)
    df.sort_values(by=['camid','uploaddate'], inplace=True)
    df.to_csv(os.path.join(logdir, 'ftptimes.csv'), index=False)
    return df


def findWhenDataUploaded(logdir='.', startdt=pd.Timestamp(2024,10,26), enddt=pd.Timestamp(2024,10,27)):
    """
    find the timestamp of the ftpdetect file that probably contained the data
    """
    trajdf = pd.read_csv(os.path.join(logdir, 'trajstations.csv'), parse_dates=['traj'])
    ftpdf = pd.read_csv(os.path.join(logdir, 'ftptimes.csv'), parse_dates=['filedate','uploaddate'])
    trajdf = trajdf[trajdf.traj > startdt]
    trajdf = trajdf[trajdf.traj <= enddt]
    trajdf['uploadtime'] = [None]* len(trajdf)
    for idx, thistraj in trajdf.iterrows():
        print(idx)
        for station in thistraj.stations[1:-1].replace("'",'').split(','):
            flt1 = ftpdf[ftpdf.camid == station.strip()]
            flt2=flt1[flt1.uploaddate > thistraj.traj]
            if len(flt2) > 0:
                upltime = flt2.iloc[0].uploaddate
                prevupltime = trajdf.loc[idx, 'uploadtime']
                if prevupltime is None:
                    trajdf.loc[idx, 'uploadtime'] = upltime
                elif upltime > prevupltime:
                    trajdf.loc[idx, 'uploadtime'] = flt2.iloc[0].uploaddate
    return trajdf


def findWhenSolutionCalculated(trajdf, logdir='.'):
    """
    Find when a solution was calculated
    """
    solvedf=pd.read_csv(os.path.join(logdir, 'solvedevents.csv'), parse_dates=['trajdate','solvedat'])
    trajdf['solvetime'] = [None]* len(trajdf)
    matchcount = 0
    for idx, thistraj in trajdf.iterrows():
        flt1 = solvedf[solvedf.trajdate == thistraj.traj]
        if len(flt1) > 0:
            solvedt = flt1.iloc[0].solvedat
            print(f'{thistraj.traj} matched with {solvedt}')
            matchcount += 1
            trajdf.loc[idx, 'solvetime'] = solvedt
        else:
            print(f'{thistraj.traj} not matched')
    print(f'matched {matchcount} out of {len(trajdf)}')
    return trajdf


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Analyse Correlator logs')
    arg_parser.add_argument('dir_path', metavar='DIR_PATH', type=str, help='Folder containing the logs')
    arg_parser.add_argument('log_date', metavar='LOG_date', type=str, help='logfile date YYYYMMDD')
    cml_args = arg_parser.parse_args()

    print('analysing')
    getBinRuntimes(cml_args.dir_path, cml_args.log_date)

    #getSolverRunDurations2(logdir, logdt)
    #logfilename = os.path.expanduser(sys.argv[1])
    #logdir = os.path.split(logfilename)[0]
    #ph1dir = os.path.expanduser('~/data/phase1/processed')
    #getFTPtimes(logdir)
    #getAllTrajStations(ph1dir, logdir)
    #findAllSolvedEvents(logfilename, logdir)
