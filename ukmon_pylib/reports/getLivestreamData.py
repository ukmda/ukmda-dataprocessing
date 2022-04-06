#
# Create an index of the livestream
# 


import boto3
import os
import datetime
import pandas as pd


def chopFilename(fname):
    spls = fname.split('_')
    dtstr = spls[0]
    dtstr = dtstr[1:] + '_' + spls[1]
    evtdate = datetime.datetime.strptime(dtstr, '%Y%m%d_%H%M%S')
    siteid = spls[2]
    if len(spls) < 5: # non-GMN camera
        camid = spls[3]
        camid= camid[:-1]
        if len(camid) < 6:
            camid = siteid + '_' + camid
    else:
        camid=spls[4]
        camid= camid[:-1]
    return evtdate.timestamp(), siteid, camid


def getLatestLiveFiles(daysback=None, df=None):
    livebucket = os.getenv("UKMONLIVEBUCKET")[5:]

    if df is None:
        df=pd.DataFrame(columns=['eventtime','source','shower','Mag','loccam','url','imgs'])

    if daysback is None:
        pref = 'M202'
    else:
        nowdt = datetime.datetime.now()
        for d in range(daysback,1):
            fromdate = nowdt + datetime.timedelta(days=d)
            pref = 'M' + fromdate.strftime('%Y%m%d')
            s3 = boto3.resource('s3')
            objlist = s3.meta.client.list_objects_v2(Bucket=livebucket,Prefix=pref)
            if objlist['KeyCount'] > 0:
                keys = objlist['Contents']
                for k in keys:
                    fname, ext = os.path.splitext(k['Key'])
                    if ext == '.jpg':
                        dt, site, cam = chopFilename(fname)
                        url = 'https://live.ukmeteornetwork.co.uk/' + k['Key']
                        newr={'eventtime':dt,'source':'3Live','shower':'Unk','Mag':99,'loccam':cam,'url':url,'imgs':url}
                        newdf=pd.DataFrame([newr])
                        df = pd.concat([df, newdf], ignore_index=True)

            while objlist['IsTruncated'] is True:
                contToken = objlist['NextContinuationToken'] 
                objlist = s3.meta.client.list_objects_v2(Bucket=livebucket,Prefix=pref, ContinuationToken=contToken)
                if objlist['KeyCount'] > 0:
                    keys = objlist['Contents']
                    for k in keys:
                        fname, ext = os.path.splitext(k['Key'])
                        if ext == '.jpg':
                            dt, site, cam = chopFilename(fname)
                            url = 'https://live.ukmeteornetwork.co.uk/' + k['Key']
                            newr={'eventtime':dt,'source':'3Live','shower':'Unk','Mag':99,'loccam':cam,'url':url,'imgs':url}
                            newdf=pd.DataFrame([newr])
                            df = pd.concat([df, newdf], ignore_index=True)

    return df 
# ['eventtime','source','shower','Mag','loccam','url','imgs']


if __name__ == '__main__':
    datadir = os.getenv('DATADIR')
    df = getLatestLiveFiles(-30)
    prvfile = os.path.join(datadir, 'ukmonlive', 'livefeed.csv')
    if os.path.isfile(prvfile):
        prevdata = pd.read_csv(prvfile)
        newdata = pd.concat([prevdata, df], ignore_index=True)
    else:
        newdata = df
        os.makedirs(os.path.join(datadir, 'ukmonlive'), exist_ok=True)
    df = df.drop_duplicates()
    df.to_csv(prvfile, index=False)
    print(df)
