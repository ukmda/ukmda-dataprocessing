#
# Collect data for a potential match at a specific time
#
# 
import os 
import sys
import pandas as pd
from urllib.request import urlretrieve
import requests
import datetime


def gatherDetectionData(dttime):
    yr = dttime[:4]
    snglfile = f's3://ukmon-shared/matches/singlepq/singles-{yr}.parquet.gzip'
    sngl = pd.read_parquet(snglfile)
    fltr = sngl[sngl.Filename.str.contains(dttime)]
    idlist = pd.concat([fltr.ID, fltr.Filename], axis=1).drop_duplicates()
    idlist['dtstamp'] = [d[10:25] for d in idlist.Filename]
    idlist['Filename']=idlist.Filename.replace('.fits','.jpg', regex=True)
    return idlist


def getJpgs(idlist, outpth):
    for _,row in idlist.iterrows():
        yr = row.Filename[10:14]
        ym = row.Filename[10:16]
        fpth = f'https://archive.ukmeteornetwork.co.uk/img/single/{yr}/{ym}/{row.Filename}'
        outfnam = os.path.join(outpth, row.Filename)
        try:
            urlretrieve(fpth, outfnam)
        except:
            pass
    return


def getECSVfiles(idlist, outpth):
    apiurl = 'https://jpaq0huazc.execute-api.eu-west-1.amazonaws.com/Prod/getecsv?stat={}&dt={}'
    for _,row in idlist.iterrows():
        stat =row.ID
        dts = datetime.datetime.strptime(row.dtstamp, '%Y%m%d_%H%M%S')
        dt = dts.strftime('%Y-%m-%dT%H:%M:%S')
        res = requests.get(apiurl.format(stat, dt))
        if res.status_code == 200:
            rawdata = res.text
            ecsvlines = rawdata.split('\n') # convert the raw data into a python list
            if len(ecsvlines) > 1:
                numecsvs = len([e for e in ecsvlines if '# %ECSV' in e]) # find out how many meteors 
                fnamebase = stat + '_' + dt.replace(':','_').replace('.','_') # create an output filename
                if numecsvs == 1:
                    with open(os.path.join(outpth, fnamebase + '.ecsv'), 'w') as outf:
                        outf.writelines(ecsvlines)
                else:
                    outf = None
                    j=1
                    for i in range(len(ecsvlines)):
                        if '# %ECSV' in ecsvlines[i]:
                            if outf is not None:
                                outf.close()
                                j=j+1
                            outf = open(os.path.join(outpth, fnamebase + '.ecsv'), 'w')
                        outf.write(f'{ecsvlines[i]}\n')
            else:
                print(row.Filename, dt, ecsvlines)
    return 


if __name__ == '__main__':
    outpth = f'./{sys.argv[1]}'
    os.makedirs(outpth, exist_ok=True)
    idlist = gatherDetectionData(sys.argv[1])
    #getJpgs(idlist, outpth)
    getECSVfiles(idlist, outpth)
    print(idlist)
