# Copyright (C) 2018-2023 Mark McIntyre

import sys
import os
import datetime
import boto3
from botocore.config import Config
import matplotlib.pyplot as plt
import numpy as np
from dateutil import relativedelta
import pandas as pd
import matplotlib.ticker as plticker


csvdtype = np.dtype([('dt', 'U10'), ('service','U64'), ('tag', 'U32'), ('cost', '<f8')])


def monthlyCostByService(dtstr, acctid):
    mth = int(dtstr[4:6])
    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    df = pd.read_csv(os.path.join(datadir, 'costs', f'costs-{acctid}-90-days.csv'))
    if acctid != '183798037734':
        df = df[(df.Tag.str.contains('ukmda')) | (df.Tag.str.contains('ukmon'))]
    df['month']=[datetime.datetime.strptime(dt, '%Y-%m-%d').month for dt in df.Date]
    df = df[df.month == mth]
    df=df.drop(columns=['Date','Tag','month'])
    grped=df.groupby(['Service']).sum().sort_values(by=['Service'])
    grped.to_csv(os.path.join(datadir, 'costs', f'costs-{acctid}-{dtstr}.csv'))


def getAllMthly():
    lastmth=(datetime.datetime.now() + datetime.timedelta(days=-20)).strftime('%Y%m')
    monthlyCostByService(lastmth, '183798037734')
    monthlyCostByService(lastmth, '317976261112')
    monthlyCostByService(lastmth, '822069317839')


def getAllPrvMthly():
    lastmth=(datetime.datetime.now() + datetime.timedelta(days=-50)).strftime('%Y%m')
    monthlyCostByService(lastmth, '183798037734')
    monthlyCostByService(lastmth, '317976261112')
    monthlyCostByService(lastmth, '822069317839')


def getAllMthToDate():
    lastmth=(datetime.datetime.now()).strftime('%Y%m')
    monthlyCostByService(lastmth, '183798037734')
    monthlyCostByService(lastmth, '317976261112')
    monthlyCostByService(lastmth, '822069317839')


def getAllCostsAndUsage(ceclient, startdt, enddt, svcs, tagval, acctid):
    response = ceclient.get_cost_and_usage(
        TimePeriod={'Start': startdt, 'End': enddt},
        Granularity='DAILY',
        Filter={'And': [{'Dimensions': {'Key': 'SERVICE', 'Values': svcs}}, {'Dimensions': {'Key': 'LINKED_ACCOUNT', 'Values': [acctid]}}]},
        Metrics=['BlendedCost'],
        GroupBy=[{'Type': 'DIMENSION','Key': 'SERVICE'},
            {'Type': 'TAG', 'Key': tagval}])

    yield response['ResultsByTime']

    while "NextPageToken" in response:
        prev_token = response['NextPageToken']        
        response = ceclient.get_cost_and_usage(
            TimePeriod={'Start': startdt, 'End': enddt},
            Granularity='DAILY',
            Filter={'And': [{'Dimensions': {'Key': 'SERVICE', 'Values': svcs}}, {'Dimensions': {'Key': 'LINKED_ACCOUNT', 'Values': [acctid]}}]},
            Metrics=['BlendedCost'],
            GroupBy=[{'Type': 'DIMENSION','Key': 'SERVICE'},
                {'Type': 'TAG', 'Key': tagval}],
            NextPageToken=prev_token)

        yield response['ResultsByTime']


def getSvcName(svc):
    if 'Elastic Compute' in svc:
        svcname='Compute'
    elif 'EC2 - Other' in svc:
        svcname='Network'
    elif 'Glue' in svc:
        svcname='Glue'
    elif 'Cloudtrail' in svc:
        svcname='Cloudtrail'
    elif 'CloudWatch' in svc:
        svcname='CloudWatch'
    elif 'Storage' in svc:
        svcname='S3'
    elif 'Container Service' in svc:
        svcname = 'ECS'
    elif 'Route 53' in svc:
        svcname = 'Route53'
    elif 'Backup' in svc:
        svcname = 'Backup'
    elif 'Lambda' in svc:
        svcname = 'Lambda'
    elif 'Tax' in svc:
        svcname = 'VAT'
    else:
        svcname = 'Other'
    return svcname


def drawBarChart(costsfile, typflag, accid):
    outdir, fname =os.path.split(costsfile)
    fn, _ = os.path.splitext(fname)
    #accid = spls[1]
    spls = fn.split('-')
    mthdate = spls[2] + '-' + spls[3]
    costdata = np.genfromtxt(costsfile, delimiter=',', dtype=csvdtype, skip_header=1)

    # select only the ukmon data
    fltr=np.logical_or(costdata['tag']==' billingtag$ukmon',costdata['tag']==' billingtag$ukmonstuff')
    fltrdata = costdata[fltr]

    # list of services in use
    svcs = list(set(fltrdata['service']))
    svcs.sort()

    # get dates
    dts = pd.date_range(str(min(costdata['dt'])), str(max(costdata['dt'])))
    labels = [d.strftime('%Y-%m-%d') for d in dts]
    #print(labels)

    # create plot
    fig, ax = plt.subplots()
    fig.set_size_inches(23.2, 8.26)
    width = 0.35       # the width of the bars: can also be len(x) sequence
    labs = []
    i = 0
    for lab in labels:
        if i % 7 == 0:
            labs.append(lab[8:10]+'-'+lab[5:7])
        else:
            labs.append(' ')
        i += 1

    numdays = len(labels)
    # run through services adding them to the graph
    bottoms = np.zeros(numdays)
    othertot = np.zeros(numdays)
    for svc in svcs: 
        #print(svc)
        thisfltr = fltrdata['service']==svc
        thisdata = fltrdata[thisfltr]
        vals=np.zeros(numdays)
        for dta in thisdata:
            dt = dta['dt']
            val = dta['cost']
            idx = list(labels).index(dt)
            vals[idx] += val
        svcname = getSvcName(svc)
        if sum(vals) <= 0.1 or svcname == 'Other': 
            othertot += vals
        else:
            #print(svcname, sum(vals))
            ax.bar(labels, vals, width, label=svcname, bottom=bottoms, tick_label = labs)
            bottoms += vals
    ax.bar(labels, othertot, width, label='Other', bottom=bottoms, tick_label = labs)

    #maxy = np.ceil(max(s3cost)+max(ec2cost))
    totcost = np.round(sum(fltrdata['cost']),2)

    ax.set_ylabel('Cost ($)')
    ax.set_xlabel('Day of Month')
    if typflag == 0:
        ax.set_title(f'{accid}: cost for month starting {mthdate}: total \${totcost:.2f}') # noqa:W605
    else:
        avg = totcost/typflag
        title = f'{accid}: cost for last {typflag} days: total \${totcost:.2f}, average \${avg:.2f}' # noqa:W605
        ax.set_title(title)
    ax.legend()
    tickbase = 7
    if numdays > 90:
        tickbase = 14
    loc = plticker.MultipleLocator(base=tickbase)
    ax.xaxis.set_major_locator(loc)
    plt.grid(which='major', alpha=0.5)
    plt.grid(which='minor', alpha=0.2)
    plt.ylim([0,50])

    fname = os.path.join(outdir, f'{fn}.jpg')
    plt.savefig(fname)
    plt.show()
    plt.close()


def getAllBillingData(ceclient, dtwanted, endwanted, regionid, outdir, typflag):
    accid = boto3.client('sts').get_caller_identity()['Account']
    startdt = dtwanted.strftime('%Y-%m-%d')
    if endwanted is None:
        endwanted = datetime.date.today()
    enddt = endwanted.strftime('%Y-%m-%d')

    resp=ceclient.get_dimension_values(
        TimePeriod={'Start':startdt, 'End':enddt}, 
        Dimension='SERVICE')
    if resp['ResponseMetadata']['HTTPStatusCode'] != 200:
        print('unable to retrieve service list')
        return 

    dims = resp['DimensionValues']
    svcs=[]
    for dim in dims:
        svcs.append(dim['Value'])

    tagval = os.getenv('COSTTAG', default='billingtag')

    if typflag == 0:
        costsfile = os.path.join(outdir, f'costs-{accid}-{startdt[:7]}.csv')
    else:
        costsfile = os.path.join(outdir, f'costs-{accid}-{typflag}-days.csv')

    tagstartdt = datetime.datetime(2022,2,25)
    with open(costsfile,'w') as outf:
        outf.write('Date,Service,Tag,Amount\n')
        for costs in getAllCostsAndUsage(ceclient, startdt, enddt, svcs, tagval, accid):
            for cost in costs:
                strt = cost['TimePeriod']['Start']
                for grp in cost['Groups']:
                    svc = grp['Keys'][0]
                    tag = grp['Keys'][1]
                    amt = grp['Metrics']['BlendedCost']['Amount']
                    dt = datetime.datetime.strptime(strt, '%Y-%m-%d')
                    if accid == '822069317839' and 'Storage Service' in svc and dt < tagstartdt:
                        tag = 'billingtag$ukmon'
                    if accid == '183798037734':
                        tag = 'billingtag$ukmon'

                    outf.write(f'{strt}, {svc}, {tag}, {amt}\n')
    return costsfile, accid


def getLatestCost(costsfile, outdir, accid=None):
    mm = pd.read_csv(costsfile)
    mml=mm[mm.Date==max(mm.Date)]
    mml = mml[mml.Tag.str.contains('ukmon')]
    totcost = sum(mml.Amount)
    if accid is None:
        accid = boto3.client('sts').get_caller_identity()['Account']
    costsfile = os.path.join(outdir, f'costs-{accid}-last.csv')
    with open(costsfile,'w') as outf:
        outf.write(f'{totcost:0.2f}\n')
    return round(totcost,4)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage python getMetrics.py outdir regionId {month}')
        print('note: you must set the AWS credentials before invoking the code')
        exit(0)
    outdir = sys.argv[1]
    regionid = sys.argv[2]
    typflag = 0
    if len(sys.argv)> 3:
        mthwanted = int(sys.argv[3])
        curdt = datetime.date.today()
        if mthwanted > 12:
            if mthwanted < 365:
                # its a number of days back to look
                endwanted = curdt - datetime.timedelta(days=1)
                dtwanted = endwanted - relativedelta.relativedelta(days=mthwanted+1)
                typflag = mthwanted
            else:
                # its a specific month in YYYYMM format
                yr = int(str(mthwanted)[:4])
                mth = int(str(mthwanted)[4:])
                dtwanted = curdt.replace(day=1).replace(month=mth).replace(year=yr)
                endwanted = dtwanted + relativedelta.relativedelta(months=1)
        else:
            yr = curdt.year
            mth = int(mthwanted)
            dtwanted = curdt.replace(day=1).replace(month=mth).replace(year=yr)
            endwanted = dtwanted + relativedelta.relativedelta(months=1)

        if endwanted > curdt:
            print("can't request for a future date, requesting for this month instead")
            yr = curdt.year
            mth = curdt.month

    else:
        endwanted = datetime.date.today() - datetime.timedelta(days=1)
        dtwanted = endwanted.replace(day=1)

    stscli = boto3.client("sts")
    myconfig = Config(region_name=regionid)
    ceclient = boto3.client('ce', config=myconfig)

    costsfile, accid = getAllBillingData(ceclient, dtwanted, endwanted, regionid, outdir, typflag)

    drawBarChart(costsfile, typflag, accid)

    getLatestCost(costsfile, outdir)
