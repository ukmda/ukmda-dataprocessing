import sys
import os
import datetime
import json 
import boto3
from botocore.config import Config

PRICEPERGBSEC = 0.00001667


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


def getLambdaBillingData(client, dtwanted, logname):
    loggroup = '/aws/lambda/{}'.format(logname)

    yyyy = dtwanted.year
    mm = dtwanted.month
    dd = dtwanted.day
    logstreampref = '{:04d}/{:02d}/{:02d}/[$LATEST]'.format(yyyy, mm, dd)
    bilog = '{}-{:04d}-{:02d}.log'.format(logname, yyyy, mm)
    g = open(bilog, 'a+')
    totgbs = 0

    response = client.describe_log_streams(
        logGroupName=loggroup,
        logStreamNamePrefix=logstreampref,
        orderBy='LogStreamName',
        descending=False,
        # nextToken='string',
        # limit=123
    )
    print('got {:d} logstreams'.format(len(response['logStreams'])))

    stime = datetime.datetime(yyyy, mm, dd, 12, 0, 0)
    etime = stime + datetime.timedelta(days=1)

    for s in response['logStreams']:
        # times  expressed as the number of milliseconds after Jan 1, 1970 00:00:00 UTC
        sname = s['logStreamName']
        resp2 = client.get_log_events(
            logGroupName=loggroup,
            logStreamName=sname,
            startTime=int(stime.timestamp()*1000),
            endTime=int(etime.timestamp()*1000),
            # nextToken='string',
            # limit=123,
            startFromHead=True
        )
        for ev in resp2['events']:
            msg = ev['message']
            ts = int(ev['timestamp']) / 1000
            evdt = datetime.datetime.fromtimestamp(ts)
            if msg[:6] == 'REPORT':
                flds = msg.split(' ')
                #print(flds)
                interesting = flds[6] + ',' + flds[9] + '\n'
                gbsecs = float(flds[6]) * float(flds[9]) / 1000 / 1024
                totgbs = totgbs + gbsecs
                g.write(str(evdt) + ',' + interesting)
    g.close()

    sumlog = '{}-daily-{:04d}-{:02d}.log'.format(logname, yyyy, mm)

    cost = totgbs * PRICEPERGBSEC
    with open(sumlog, 'a+') as outf:
        outf.write('{} ${:.5f}\n'.format(stime, cost))
    return


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage python getMetrics.py outdir regionId')
        print('note: you must set the AWS credentials before invoking the code')
        exit(0)
    outdir = sys.argv[1]
    regionid = sys.argv[2]
    doff = 1
    dtwanted = datetime.date.today() - datetime.timedelta(days=doff)

    stscli = boto3.client("sts")
    account_id = stscli.get_caller_identity()["Account"]
    fldr = os.path.join(outdir, '{}'.format(account_id), regionid)

    os.makedirs(fldr, exist_ok=True)

    #print('getting MonitorLiveFeed logs for ', dtwanted)
    #myconfig = Config(region_name='eu-west-1')
    #client = boto3.client('logs', config=myconfig)
    #getLambdaBillingData(client, dtwanted, 'MonitorLiveFeed')

    #print('getting CSVTrigger logs for ', dtwanted)
    #myconfig = Config(region_name='eu-west-2')
    #client = boto3.client('logs', config=myconfig)
    #getLambdaBillingData(client, dtwanted, 'CSVTrigger')

    dtwanted=datetime.date.today()
    dtwanted = dtwanted.replace(day=1)

    #endwanted = datetime.datetime(2021,6,1)
    endwanted = None

    myconfig = Config(region_name=regionid)
    ceclient = boto3.client('ce', config=myconfig)

    service = 'Amazon Elastic Compute Cloud - Compute'
    getBillingData(ceclient, service, 'ec2', dtwanted, endwanted, fldr)

    service = 'Amazon Simple Storage Service'
    getBillingData(ceclient, service, 's3', dtwanted, endwanted, fldr)

    service = 'AWS Lambda'
    getBillingData(ceclient, service, 'lambda', dtwanted, endwanted, fldr)
