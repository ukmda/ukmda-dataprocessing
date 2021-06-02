import sys
import datetime
import boto3
from botocore.config import Config

PRICEPERGBSEC = 0.00001667


def getMonitorLogs(client, dtwanted):
    loggroup = '/aws/lambda/MonitorLiveFeed'

    yyyy = dtwanted.year
    mm = dtwanted.month
    dd = dtwanted.day
    logstreampref = '{:04d}/{:02d}/{:02d}/[$LATEST]'.format(yyyy, mm, dd)
    evlog = 'actions-{:04d}-{:02d}-{:02d}.log'.format(yyyy, mm, dd)
    bilog = 'billing-{:04d}-{:02d}.log'.format(yyyy, mm)
    f = open(evlog, 'w')
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
    for s in response['logStreams']:
        # times  expressed as the number of milliseconds after Jan 1, 1970 00:00:00 UTC
        sname = s['logStreamName']
        stime = int(datetime.datetime(yyyy, mm, dd, 12, 0, 0).timestamp() * 1000)
        etime = int(datetime.datetime(yyyy, mm, dd + 1, 12, 0, 0).timestamp() * 1000)
        resp2 = client.get_log_events(
            logGroupName=loggroup,
            logStreamName=sname,
            startTime=stime,
            endTime=etime,
            # nextToken='string',
            # limit=123,
            startFromHead=True
        )
        for ev in resp2['events']:
            msg = ev['message']
            ts = int(ev['timestamp']) / 1000
            evdt = datetime.datetime.fromtimestamp(ts)
            if msg[:7] == 'LiveMon':
                f.write(str(evdt) + ',' + msg)
            if msg[:6] == 'REPORT':
                flds = msg.split(' ')
                # print(flds)
                interesting = flds[6] + ',' + flds[9] + '\n'
                gbsecs = float(flds[6]) * float(flds[9]) / 1000 / 1024
                totgbs = totgbs + gbsecs
                g.write(str(evdt) + ',' + interesting)
    f.close()
    g.close()
    cost = totgbs * PRICEPERGBSEC
    print('cost is ${:.5f}'.format(cost))
    return


def getCSVTriggerLogs(client, dtwanted):
    loggroup = '/aws/lambda/CSVTrigger'

    yyyy = dtwanted.year
    mm = dtwanted.month
    dd = dtwanted.day
    logstreampref = '{:04d}/{:02d}/{:02d}/[$LATEST]'.format(yyyy, mm, dd)
    bilog = 'billing-csv-{:04d}-{:02d}.log'.format(yyyy, mm)
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
    for s in response['logStreams']:
        # times  expressed as the number of milliseconds after Jan 1, 1970 00:00:00 UTC
        sname = s['logStreamName']
        stime = int(datetime.datetime(yyyy, mm, dd, 12, 0, 0).timestamp() * 1000)
        etime = int(datetime.datetime(yyyy, mm, dd + 1, 12, 0, 0).timestamp() * 1000)
        resp2 = client.get_log_events(
            logGroupName=loggroup,
            logStreamName=sname,
            startTime=stime,
            endTime=etime,
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
                # print(flds)
                interesting = flds[6] + ',' + flds[9] + '\n'
                gbsecs = float(flds[6]) * float(flds[9]) / 1000 / 1024
                totgbs = totgbs + gbsecs
                g.write(str(evdt) + ',' + interesting)
    g.close()
    cost = totgbs * PRICEPERGBSEC
    print('cost is ${:.5f}'.format(cost))
    return


if __name__ == '__main__':
    doff = 1
    if len(sys.argv) == 2:
        doff = int(sys.argv[1])
    dtwanted = datetime.date.today() - datetime.timedelta(days=doff)
    print('getting MonitorLiveFeed logs for ', dtwanted)
    client = boto3.client('logs')
    getMonitorLogs(client, dtwanted)

    print('getting CSVTrigger logs for ', dtwanted)
    myconfig = Config(region_name='eu-west-2')
    client = boto3.client('logs', config=myconfig)
    getCSVTriggerLogs(client, dtwanted)
