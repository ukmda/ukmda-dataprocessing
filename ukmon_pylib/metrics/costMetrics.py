import sys
import os
import datetime
import json 
import boto3
from botocore.config import Config
import matplotlib.pyplot as plt
import numpy as np
from dateutil import relativedelta

PRICEPERGBSEC = 0.00001667

csvdtype = np.dtype([('dt', 'S10'), ('tag', 'S32'), ('cost', '<f8'), ('amt', '<f8')])


def drawBarChart(outdir, accountid, regionid, mthdate):
    fldr = os.path.join(outdir, '{}'.format(accountid), regionid)
    fname = os.path.join(fldr, '{}-{}.csv'.format('ec2', mthdate))
    ec2data = np.genfromtxt(fname, delimiter=',', dtype=csvdtype)
    fltr=np.logical_or(ec2data['tag']==b'billingtag$ukmon',ec2data['tag']==b'billingtag$ukmonstuff')
    ec2fdata = ec2data[fltr]
    labels = ec2fdata['dt']
    ec2cost = ec2fdata['cost']
    s3cost = np.zeros(len(ec2cost))

    fname = os.path.join(fldr, '{}-{}.csv'.format('s3', mthdate))
    s3data = np.genfromtxt(fname, delimiter=',', dtype=csvdtype)
    fltr=np.logical_or(s3data['tag']==b'billingtag$ukmon',s3data['tag']==b'billingtag$ukmonstuff')
    s3fdata = s3data[fltr]
    s3labels = s3fdata['dt']
    tmps3cost = s3fdata['cost']
    for i in range(len(tmps3cost)):
        dt = s3labels[i]
        idx = np.where(labels==dt)
        if len(idx) > 1:
            idx = idx[0]
        s3cost[idx] = tmps3cost[i]

    width = 0.35       # the width of the bars: can also be len(x) sequence
    labs = []
    for lab in labels:
        labs.append(lab[8:10])

    # print(mth, labs)
    fig, ax = plt.subplots()
    maxy = np.ceil(max(s3cost)+max(ec2cost))
    totcost = np.round(sum(s3cost) + sum(ec2cost),2)

    ax.bar(labs, s3cost, width, label='S3')
    ax.bar(labs, ec2cost, width, bottom=s3cost, label='EC2')

    ax.set_ylabel('Cost ($)')
    ax.set_xlabel('Day of Month')
    ax.set_title('Cost for month starting {}: total ${:.2f}'.format(mthdate, totcost))
    ax.legend()
    plt.ylim(0,maxy)

    #plt.show()
    os.makedirs(os.path.join(outdir, 'plots'), exist_ok=True)
    fname = os.path.join(outdir, 'plots','{}-{}'.format(accountid, mthdate))
    plt.savefig(fname)


def getBillingData(ceclient, service, abbrv, dtwanted, endwanted, fldr):
    startdt = dtwanted.strftime('%Y-%m-%d')
    if endwanted is None:
        endwanted = datetime.date.today()
    enddt = endwanted.strftime('%Y-%m-%d')
    print(startdt, enddt)

    response = ceclient.get_cost_and_usage(
        TimePeriod={'Start': startdt, 'End': enddt},
        Granularity='DAILY',
        Filter={'Dimensions': {'Key': 'SERVICE', 'Values': [service]}},
        Metrics=['BlendedCost', 'UsageQuantity'],
        GroupBy=[{'Type': 'DIMENSION','Key': 'SERVICE'}, {'Type': 'TAG','Key': 'billingtag'}])

    fname = os.path.join(fldr, '{}-{}.json'.format(abbrv, startdt))
    strdata = json.dumps(response, indent=4)
    with open(fname, "w") as write_file:
        write_file.write(strdata)
    interpretCostData(response, startdt, abbrv, fldr)
    return 


def interpretCostData(srcdata, mthdate, abbrv, fldr):
    fname = os.path.join(fldr, '{}-{}.csv'.format(abbrv, mthdate))
    with open(fname, 'w') as csvf:
        for results in srcdata['ResultsByTime']:
            daterange = results['TimePeriod']['Start'] 
            costdata = results['Groups']
            for dta in costdata:
                tag = dta['Keys'][1]
                cost = dta['Metrics']['BlendedCost']['Amount']
                amt = dta['Metrics']['UsageQuantity']['Amount']
                csvf.write('{},{},{},{}\n'.format(daterange, tag, cost, amt))
    return


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
    fldr = os.path.join(outdir, '{}'.format(accountid), regionid)

    os.makedirs(fldr, exist_ok=True)

    myconfig = Config(region_name=regionid)
    ceclient = boto3.client('ce', config=myconfig)

    service = 'Amazon Elastic Compute Cloud - Compute'
    getBillingData(ceclient, service, 'ec2', dtwanted, endwanted, fldr)

    service = 'Amazon Simple Storage Service'
    getBillingData(ceclient, service, 's3', dtwanted, endwanted, fldr)

    service = 'AWS Lambda'
    getBillingData(ceclient, service, 'lambda', dtwanted, endwanted, fldr)

    drawBarChart(outdir, accountid, regionid, dtwanted)
