import sys
import os
import datetime
import boto3
from botocore.config import Config
import matplotlib.pyplot as plt
import numpy as np
from dateutil import relativedelta
import pandas as pd

csvdtype = np.dtype([('dt', 'U10'), ('service','U64'), ('tag', 'U32'), ('cost', '<f8')])


def getAllCostsAndUsage(ceclient, startdt, enddt, svcs, tagval):
    response = ceclient.get_cost_and_usage(
        TimePeriod={'Start': startdt, 'End': enddt},
        Granularity='DAILY',
        Filter={'Dimensions': {'Key': 'SERVICE', 'Values': svcs}},
        Metrics=['BlendedCost'],
        GroupBy=[{'Type': 'DIMENSION','Key': 'SERVICE'},
            {'Type': 'TAG', 'Key': tagval}])

    yield(response['ResultsByTime'])

    while "NextPageToken" in response:
        prev_token = response['NextPageToken']        
        response = ceclient.get_cost_and_usage(
            TimePeriod={'Start': startdt, 'End': enddt},
            Granularity='DAILY',
            Filter={'Dimensions': {'Key': 'SERVICE', 'Values': svcs}},
            Metrics=['BlendedCost'],
            GroupBy=[{'Type': 'DIMENSION','Key': 'SERVICE'},
                {'Type': 'TAG', 'Key': tagval}],
            NextPageToken=prev_token)

        yield(response['ResultsByTime'])


def getSvcName(svc):
    if 'Elastic Compute' in svc:
        svcname='Compute'
    elif 'EC2 - Other' in svc:
        svcname='Network'
    elif 'Glue' in svc:
        svcname='Glue'
    elif 'Cloudtrail' in svc:
        svcname='Cloudtral'
    elif 'Storage' in svc:
        svcname='S3'
    elif 'Container Service' in svc:
        svcname = 'ECS'
    elif 'Route 53' in svc:
        svcname = 'R-53'
    elif 'Backup' in svc:
        svcname = 'Backup'
    elif 'Lambda' in svc:
        svcname = 'Lambda'
    else:
        svcname = 'Other'
    return svcname


def drawBarChart(costsfile):
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
    width = 0.35       # the width of the bars: can also be len(x) sequence
    labs = []
    for lab in labels:
        labs.append(lab[8:10])

    numdays = len(labels)
    # run through services adding them to the graph
    bottoms=np.zeros(numdays)
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
        if sum(vals) > 0.1: 
            svcname = getSvcName(svc)
            #print(svcname, vals)
            ax.bar(labs, vals, width, label=svcname, bottom=bottoms)
            bottoms += vals
    
    #maxy = np.ceil(max(s3cost)+max(ec2cost))
    totcost = np.round(sum(fltrdata['cost']),2)

    ax.set_ylabel('Cost ($)')
    ax.set_xlabel('Day of Month')
    ax.set_title(f'Cost for month starting {mthdate}: total ${totcost:.2f}')
    ax.legend()

    fname = os.path.join(outdir, f'{fn}.jpg')
    plt.savefig(fname)
    plt.show()


def getAllBillingData(ceclient, dtwanted, endwanted, regionid, outdir):
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

    costsfile = os.path.join(outdir, f'costs-{accid}-{startdt[:7]}.csv')

    with open(costsfile,'w') as outf:
        outf.write('Date,Service,Tag,Amount\n')
        for costs in getAllCostsAndUsage(ceclient, startdt, enddt, svcs, tagval):
            for cost in costs:
                strt = cost['TimePeriod']['Start']
                for grp in cost['Groups']:
                    svc = grp['Keys'][0]
                    tag = grp['Keys'][1]
                    amt = grp['Metrics']['BlendedCost']['Amount']
                    outf.write(f'{strt}, {svc}, {tag}, {amt}\n')
    return costsfile, accid


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage python getMetrics.py outdir regionId {month}')
        print('note: you must set the AWS credentials before invoking the code')
        exit(0)
    outdir = sys.argv[1]
    regionid = sys.argv[2]
    if len(sys.argv)> 3:
        mthwanted = int(sys.argv[3])
        curdt = datetime.date.today()
        if int(mthwanted) > 12:
            yr = int(str(mthwanted)[:4])
            mth = int(str(mthwanted)[4:])
        else:
            yr = curdt.year
            mth = int(mthwanted)

        if yr >= curdt.year and mth > curdt.month:
            print("can't request for a future date, requesting for this month instead")
            yr = curdt.year
            mth = curdt.month

        dtwanted = curdt.replace(day=1).replace(month=mth).replace(year=yr)
        endwanted = dtwanted + relativedelta.relativedelta(months=1)
    else:
        endwanted = datetime.date.today() - datetime.timedelta(days=1)
        dtwanted = endwanted.replace(day=1)

    stscli = boto3.client("sts")
    myconfig = Config(region_name=regionid)
    ceclient = boto3.client('ce', config=myconfig)

    costsfile, accid = getAllBillingData(ceclient, dtwanted, endwanted, regionid, outdir)

    drawBarChart(costsfile)
