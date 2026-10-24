# simple scripts to analyse the GMN data in python

import pandas as pd
import os
import sys
import datetime
import glob

from converters.gmnTxtToPandas import loadOneFile

def compareTwoFiles(file1, file2):
    df1 = loadOneFile(file1)
    df2 = loadOneFile(file2)

    df1['dupe']=df1.duplicated(subset=['id'])
    print(f'file 1 contains {len(df1[df1.dupe==True].id.unique())} duplicates')
    dupe1 = df1[df1.dupe==True] # noqa: E712
    df1.drop(columns=['dupe'])

    df2['dupe']=df2.duplicated(subset=['id'])
    print(f'file 2 contains {len(df2[df2.dupe==True].id.unique())} duplicates')
    dupe2 = df2[df2.dupe==True] # noqa: E712
    df2.drop(columns=['dupe'])

    mrg = df1.merge(df2.drop_duplicates(), on=['id'], how='left', indicator=True)
    old_not_new = mrg[mrg._merge!='both']
    print(f'there are {len(old_not_new)} rows in the first file not in the second')

    mrg = df2.merge(df1.drop_duplicates(), on=['id'], how='left', indicator=True)
    new_not_old = mrg[mrg._merge!='both']
    print(f'there are {len(new_not_old)} rows in the second file not in the first')

    print(old_not_new)
    old_not_new.to_csv('./old_not_new.csv')
    new_not_old.to_csv('./old_not_new.csv')
    return df1,df2, old_not_new, new_not_old, dupe1, dupe2


def aggregateOneMonth(dirpath, yr, mth):
    startdt = datetime.datetime(yr, mth, 1) - datetime.timedelta(days=1)
    syr = startdt.year
    smth = startdt.month
    sday = startdt.day
    datafiles = glob.glob(os.path.join(dirpath, 'daily', f'traj_summary_{syr:04d}{smth:02d}{sday:02d}*.txt'))
    prevfile = datafiles[0]
    datafiles = [prevfile] + glob.glob(os.path.join(dirpath, 'daily', f'traj_summary_{yr:04d}{mth:02d}*.txt'))
    mthlydata = None
    for datfile in datafiles:
        newdata = loadOneFile(datfile)
        if mthlydata is None:
            mthlydata = newdata
        else:
            mthlydata = pd.concat([mthlydata, newdata], sort=True)
    mthlydata = mthlydata[mthlydata.utc_beg >= datetime.datetime(yr,mth,1,0,0,0)]
    return mthlydata


def doYear(dirpath, yr):
    datafiles = glob.glob(os.path.join(dirpath, 'monthly', f'traj_summary_monthly_{yr}*.txt'))
    for datfile in datafiles:
        print(f'processing {datfile}')
        newdata = loadOneFile(datfile)
        fn, _ = os.path.splitext(datfile)
        ym = fn[-6:]
        newdata.to_parquet(os.path.join(dirpath, 'parquet', 'monthly', f'gmn_{ym}.parquet.snap'), index=False)

    datafiles = glob.glob(os.path.join(dirpath, f'traj_summary_yearly_{yr}.txt'))
    for datfile in datafiles:
        print(f'processing {datfile}')
        newdata = loadOneFile(datfile)
        newdata.to_parquet(os.path.join(dirpath, 'parquet', f'gmn_{yr}.parquet.snap'), index=False)
    return


def getStats(dirpath):
    for yr in range(2022,2025):
        df = pd.read_parquet(os.path.join(dirpath, f'gmn_{yr}01.parquet.snap'))
        for mth in range(2,13):
            try: 
                df2 = pd.read_parquet(f'gmn_{yr}{mth:02d}.parquet.snap')
                df = pd.concat(df, df2)
            except:
                pass
#        df = df[df.Amag < -3.99]
        print(f'{yr}, {len(df)}, {df.Lat1.mean():.1f}, {df.Lat1.max():.1f}, {df.Lat1.min():.1f}, {df.Lat1.std():.1f}')
    print('-----')
    for yr in range(2022,2025):
        df = pd.read_parquet(f'gmn_{yr}01.parquet.snap')
        for mth in range(2,13):
            try: 
                df2 = pd.read_parquet(f'gmn_{yr}{mth:02d}.parquet.snap')
                df = pd.concat(df, df2)
            except:
                pass
        df = df[df.Amag < -3.99]
        print(f'{yr}, {len(df)}, {df.Lat1.mean():.1f}, {df.Lat1.max():.1f}, {df.Lat1.min():.1f}, {df.Lat1.std():.1f}')



def analyseAMonth(fulldf, yr, mth):
    if mth != 0:
        beg = datetime.datetime(yr, mth, 1)
        if mth < 12:
            end = datetime.datetime(yr, mth+1, 1)
        else:
            end = datetime.datetime(yr+1, 1, 1)
        mthdf = fulldf[fulldf.utc_beg >= beg]
        mthdf = mthdf[mthdf.utc_beg < end]
    else:
        mthdf = fulldf
    tot_num = len(mthdf)
    uktraj = mthdf[mthdf.stats.str.contains('UK')]
    num_uk_traj = len(uktraj)
    allstats = ','.join(uktraj.stats)
    stats = list(set(allstats.split(',')))
    ukstats = [x for x in stats if 'UK' in x]
    otherstats = [x for x in stats if 'UK' not in x]
    distinctuk = [x for x in ukstats if '_' not in x]
    distinctother = [x for x in otherstats if '_' not in x]
    ctrys = list(set([x[:2] for x in otherstats]))
    otherctrydf = uktraj[uktraj.stats.str.contains('|'.join(ctrys))]
    if mth == 0:
        uktraj.to_csv('uk-trajectories.csv', index=False)
    return len(distinctuk), len(distinctother), num_uk_traj, tot_num, len(otherctrydf)


def findDuplicatesById(dirpath, yr, mth=None):
    if mth:
        datafile = os.path.join(dirpath, 'parquet', 'monthly', f'gmn_{yr:04d}{mth:02d}.parquet.snap')
    else:
        datafile = os.path.join(dirpath, 'parquet', f'gmn_{yr:04d}.parquet.snap')
    df = pd.read_parquet(datafile)
    df['dupe']=df.duplicated(subset=['id'])
    dupeids = df[df.dupe].sort_values(by=['id']).id
    duperows = df[df.id.isin(dupeids)]
    print(duperows)
    print(len(df))
    return duperows


def atleastOneStation(stats,statsnext):
    if stats is None or statsnext is None:
        return False
    stats = stats.split(',')
    statsnext = statsnext.split(',')
    return any(i in statsnext for i in stats)


def findDuplicatesByStatAndJD(yr, mth=None, df=None):
    if not df:
        dirpath = '.'
        if mth:
            datafile = os.path.join(dirpath, 'parquet', 'monthly', f'gmn_{yr:04d}{mth:02d}.parquet.snap')
        else:
            datafile = os.path.join(dirpath, 'parquet', f'gmn_{yr:04d}.parquet.snap')
        df = pd.read_parquet(datafile)
    df['statsnext'] = df.stats.shift(-1)
    df['jd_next'] = df.jd_beg.shift(-1)
    df['Lat1_next'] = df.Lat1.shift(-1)
    df['Lon1_next'] = df.Lon1.shift(-1)
    nearjd = df.query('abs(jd_beg - jd_next) < (0.5/86400)')
    nearlat = nearjd.query('abs(Lat1 - Lat1_next) < 1 and abs(Lon1 - Lon1_next) < 1')
    samestats = nearlat.query('stats == statsnext')
    nearlat['overlapstats'] = nearlat.apply(lambda row: atleastOneStation(row.stats, row.statsnext), axis=1)
    commonstats = nearlat[nearlat.overlapstats]
    print(f'there are {len(df)} trajectories in the period')
    print(f'there are {len(nearjd)} ({round(100*len(nearjd)/len(df),2)}%) events within 1s')
    print(f'there are {len(commonstats)} ({round(100*len(commonstats)/len(df),2)}%) with at least one common station')
    print(f'there are {len(samestats)} ({round(100*len(samestats)/len(df),2)}%) with the same stations')
    return nearjd, commonstats, samestats


if __name__ == '__main__':
    yr = int(sys.argv[1])
    fulldf = None
    data = []
    for mth in range(1,13):
        print(f'processing month {mth}')
        df = pd.read_parquet(f'parquet/monthly/gmn_{yr}{mth:02d}.parquet.snap')
        cams, othercams, traj, totaltraj, othertraj = analyseAMonth(df, yr, mth)
        data.append([mth, cams, othercams, traj, totaltraj, othertraj])
        fulldf = df if fulldf is None else pd.concat([fulldf, df])

    result = pd.DataFrame(data, columns=['Mth','Camcount','OtherCams','TrajCount','TotalTraj','NonUKTraj'])
    tmpres = result.set_index('Mth')
    plot = tmpres.plot(title='UK Statistics')
    fig = plot.get_figure()
    fig.savefig(f'uk-analysis-{yr}.jpg')

    cams, othercams, traj, totaltraj, otherctry, = analyseAMonth(fulldf, yr, 0)
    data.append([0, cams, othercams, traj, totaltraj, otherctry])
   
    result = pd.DataFrame(data, columns=['Mth','Camcount','OtherCams','TrajCount','TotalTraj','NonUKTraj'])
    result.to_csv('2025-stats.csv', index=False)
