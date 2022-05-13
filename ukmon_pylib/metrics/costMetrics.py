import sys
import os
import datetime
import boto3
from botocore.config import Config
import matplotlib.pyplot as plt
import numpy as np
from dateutil import relativedelta

csvdtype = np.dtype([('dt', 'U10'), ('service','U64'), ('tag', 'U32'), ('cost', '<f8')])


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


def drawBarChart(outdir, accountid, regionid, mthdate):
    fldr = os.path.join(outdir, f'{accountid}',f'{regionid}')
    fname = os.path.join(fldr, f'costs-{mthdate}.csv')
    costdata = np.genfromtxt(fname, delimiter=',', dtype=csvdtype, skip_header=1)

    # select only the ukmon data
    fltr=np.logical_or(costdata['tag']==' billingtag$ukmon',costdata['tag']==' billingtag$ukmonstuff')
    fltrdata = costdata[fltr]

    # list of services in use
    svcs = list(set(fltrdata['service']))
    svcs.sort()

    # get dates
    s3f=fltrdata['service']==' Amazon Simple Storage Service'
    s3data = fltrdata[s3f]
    labels = s3data['dt']

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

    os.makedirs(os.path.join(outdir, 'plots'), exist_ok=True)
    fname = os.path.join(outdir, 'plots','{}-{}'.format(accountid, mthdate))
    plt.savefig(fname)
    plt.show()


def getAllBillingData(ceclient, dtwanted, endwanted, regionid, outdir):
    fldr = os.path.join(outdir, f'{accountid}/{regionid}')
    os.makedirs(fldr, exist_ok=True)

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

    response = ceclient.get_cost_and_usage(
        TimePeriod={'Start': startdt, 'End': enddt},
        Granularity='DAILY',
        Filter={'Dimensions': {'Key': 'SERVICE', 'Values': svcs}},
        Metrics=['BlendedCost'], # 'UsageQuantity'],
        GroupBy=[{'Type': 'DIMENSION','Key': 'SERVICE'}, 
            {'Type': 'TAG','Key': 'billingtag'}])

    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        print('unable to retrieve costs by service')
        return 
    else:
        results = response['ResultsByTime']
        costsfile = os.path.join(fldr, f'costs-{startdt[:7]}.csv')
        with open(costsfile,'w') as outf:
            outf.write('Date,Service,Tag,Amount\n')
            for res in results:
                strt = res['TimePeriod']['Start']
                for grp in res['Groups']:
                    svc = grp['Keys'][0]
                    tag = grp['Keys'][1]
                    amt = grp['Metrics']['BlendedCost']['Amount']
                    outf.write(f'{strt}, {svc}, {tag}, {amt}\n')


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
        thismth = curdt.month
        dtwanted = curdt.replace(month=mthwanted).replace(day=1)
        if mthwanted > thismth:
            dtwanted = dtwanted.replace(year = curdt.year-1)
        #if mthwanted == 12:
        #    dtwanted = dtwanted.replace(year = curdt.year-1).replace(month=12)
        endwanted = dtwanted + relativedelta.relativedelta(months=1)
        
    else:
        endwanted = datetime.date.today() - datetime.timedelta(days=1)
        dtwanted = endwanted.replace(day=1)

    stscli = boto3.client("sts")
    accountid = stscli.get_caller_identity()["Account"]
    myconfig = Config(region_name=regionid)
    ceclient = boto3.client('ce', config=myconfig)

    getAllBillingData(ceclient, dtwanted, endwanted, regionid, outdir)

    drawBarChart(outdir, accountid, regionid, dtwanted.strftime('%Y-%m'))
