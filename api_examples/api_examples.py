import pandas as pd
import json 
import requests


def detectionsExample():
    apiurl='https://api.ukmeteors.co.uk/getecsv?stat={}&dt={}'

    # retrieve details of a single-station detection at a specific time
    stat ='UK0025'
    dt = '2021-07-17T02:41:05.05'
    res = requests.get(apiurl.format(stat, dt))
    if res.status_code == 200:
        rawdata=res.text
        ecsvlines=rawdata.split('\n') # convert the raw data into a python list
        numecsvs = len([e for e in ecsvlines if '# %ECSV' in e]) # find out how many meteors 
        fnamebase = dt.replace(':','_').replace('.','_') # create an output filename
        if numecsvs == 1:
            with open(fnamebase + '.ecsv', 'w') as outf:
                outf.writelines(ecsvlines)
        else:
            outf = None
            j=1
            for i in range(len(ecsvlines)):
                if '# %ECSV' in ecsvlines[i]:
                    if outf is not None:
                        outf.close()
                        j=j+1
                    outf = open(fnamebase + f'_M{j:03d}.ecsv', 'w')
                outf.write(f'{ecsvlines[i]}\n')


def matchExampleA():
    apiurl = 'https://api.ukmeteors.co.uk/matches'

    # get all matched events for a given date
    reqtyp = 'matches'
    reqval = '20231121'
    apicall = '{}?reqtyp={}&reqval={}'.format(apiurl, reqtyp, reqval)
    matchlist = pd.read_json(apicall, lines=True)
    print(matchlist)

    # get details of the 6th event in matchlist
    reqtyp = 'detail'
    reqval = matchlist.iloc[5].orbname
    apicall = '{}?reqtyp={}&reqval={}'.format(apiurl, reqtyp, reqval)
    evtdetail = pd.read_json(apicall, typ='series')
    print(evtdetail)

    # get details for the first five events in the match list
    # and put them in a pandas dataframe, then sort by brightest
    details=[]
    for id in matchlist.head(5).orbname:
        reqval = id
        apicall = '{}?reqtyp={}&reqval={}'.format(apiurl, reqtyp, reqval)
        details.append(pd.read_json(apicall, typ='series'))
    df = pd.DataFrame(details)
    df = df.sort_values(by=['_mag'])
    print(df)


def matchSummaryExample():
    apiurl = 'https://api.ukmeteors.co.uk/matches'
    
    # get summary of all events from a specific date
    reqtyp = 'summary'
    reqval = '20231121'
    apicall = '{}?reqtyp={}&reqval={}'.format(apiurl, reqtyp, reqval)
    data=requests.get(apicall)
    if data.status_code == 200:
        df = pd.DataFrame(json.loads(data.text))
        print(df._lat1)
        print(df.orbname)
        rec = df[df._localtime =='_20231121_212437']
        print(rec._lat1)


def trajectoryExample():
    apiurl = 'https://api.ukmeteors.co.uk/pickle/getpickle'

    # get the complete raw and processed data for a given solution
    trajid = '20220814_205940.252_UK'
    apicall = '{}?reqval={}'.format(apiurl, trajid)
    data=requests.get(apicall)
    if data.status_code == 200:
        traj = json.loads(data.text)
        print(traj['jdt_ref'])

        # observations contains the raw data
        observations = traj['observations']
        print(len(observations))
        for obs in observations:
            k = list(obs.keys())[0]
            print(obs[k]['station_id'])

        # print all fields
        print(traj.keys())
