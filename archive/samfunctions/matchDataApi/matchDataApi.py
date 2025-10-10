# Copyright (C) 2018-2023 Mark McIntyre
# 
# python code behind the MatchData API
# 

import os
import boto3
import json
import pymysql.cursors


def getSqlLoginDetails():
    # retrieve password and host from SSM. This allows me to manage them from Terraform
    ssm = boto3.client('ssm', region_name='eu-west-1')
    res = ssm.get_parameter(Name='prod_dbpw', WithDecryption=True)
    password = res['Parameter']['Value']
    res = ssm.get_parameter(Name='prod_dbhost')
    host = res['Parameter']['Value'] 
    # should really do these too but they won't change often if at all
    user = 'batch'
    db = 'ukmon'
    return host, user, password, db


def getStationData(statid, dtstr):
    host, user, passwd, db = getSqlLoginDetails()
    connection = pymysql.connect(host=host, user=user, password=passwd, db=db, cursorclass=pymysql.cursors.DictCursor)  
    try:
        with connection.cursor() as cursor:
            if statid is None:
                sql = f"SELECT s.orbname from matches s where s._localtime like '_{dtstr}%'"
            else:
                sql = f"SELECT s.orbname from matches s where s._localtime like '_{dtstr}%' and s.stations like '%{statid}%'"
            cursor.execute(sql)
            result = cursor.fetchall()
    finally:
        connection.close()
    res=''
    for event in result:
        res = res + json.dumps(event) + '\n'
    return res


def getSummaryData(dtstr):
    host, user, passwd, db = getSqlLoginDetails()
    connection = pymysql.connect(host=host, user=user, password=passwd, db=db, cursorclass=pymysql.cursors.DictCursor)  
    fieldlist = '_localtime,_mjd,_sol,_ID1,_amag,_ra_o,_dc_o,_ra_t,_dc_t,_elng,_elat,_vo,_vi,_vg,_vs,_a,_q,_e,_p,_peri,_node,_incl,'\
        '_stream,_mag,_dur,_lng1,_lat1,_H1,_lng2,_lat2,_H2,_LD21,_az1r,_ev1r,_Nts,_Nos,_leap,_tme,_dt,'\
        'dtstamp,orbname,iau,shwrname as name,mass,pi,Q,true_anom,EA,MA,Tj,T,last_peri,jacchia1,Jacchia2,numstats,stations'
    expr = f"SELECT {fieldlist} from matches s where s._localtime like '_{dtstr}%'"
    result=[]
    try:
        with connection.cursor() as cursor:
            cursor.execute(expr)
            result = cursor.fetchall()
    finally:
        connection.close()
    if len(result) > 0:
        res = json.dumps(result)
    else:
        res=json.dumps({'result': 'no data'})
    res = res.replace('}, {','},\n{')
    return res


def getDetailData(orbname):
    host, user, passwd, db = getSqlLoginDetails()
    connection = pymysql.connect(host=host, user=user, password=passwd, db=db, cursorclass=pymysql.cursors.DictCursor)  
    expr = f"SELECT * from matches s where s.orbname like '{orbname}%'"
    try:
        with connection.cursor() as cursor:
            cursor.execute(expr)
            result = cursor.fetchall()
    finally:
        connection.close()
    if len(result) > 0:
        res = json.dumps(result[0])
    else: 
        res=json.dumps({'result': 'no data'})
    res = res.replace('}, {','},\n{')
    return res


def lambda_handler(event, context):
    webbuck = os.getenv('WEBBUCKET', default='ukmda-website')
    #print('received event', json.dumps(event))
    qs = event['queryStringParameters']
    if qs is None:
        return {
            'statusCode': 200,
            'body': 'usage: detections?reqtyp=xxx&reqval=yyyy[&points=1]'
        }
    reqtyp = qs['reqtyp']
    points = False
    if 'points' in qs:
        points = True

    if reqtyp == 'station':
        statid = qs['statid']
        dtstr = qs['reqval']
        print(f'station data requested for {statid} on {dtstr}')
        res = getStationData(statid, dtstr)
    elif reqtyp == 'summary':
        dtstr = qs['reqval']
        print(f'summary data requested for {dtstr}')
        res = getSummaryData(dtstr)
    elif reqtyp == 'matches':
        dtstr = qs['reqval']
        print(f'match data requested for {dtstr}')
        res = getStationData(None, dtstr)
    elif reqtyp == 'detail':
        orbname = qs['reqval']
        print(f'detail requested for {orbname}')
        res = getDetailData(orbname)
        if points:
            print(f'points requested for {orbname}')
            if 'imgstr' in res:
                url = json.loads(res)['imgstr']
                url = url.replace('ground_track.png','report.txt')
                reppth = url.split('//', 1)[1].split('/',1)[1]
                _, repname = os.path.split(reppth)
                try:
                    tmpfname = f'/tmp/{repname}'
                    s3 = boto3.client('s3')
                    s3.download_file(webbuck, reppth, tmpfname)
                    flis = open(tmpfname, 'r').readlines()
                    os.remove(tmpfname)
                    res = fileToJsonString(flis)
                except Exception:
                    print('report file unavailable')
                    res = '{"points": "unavailable"}'
            else:
                res = '{"points": "unavailable"}'

    else:
        res = '{"invalid request type - must be one of \'matches\', \'details\', \'station\',\'summary\'"}'
    
    print(res)
    return {
        'statusCode': 200,
        'body': res
    }


def fileToJsonString(flis):
    hdr = ['No','statid','ign','t','jd','m1','m2','az','alt','azl','altl','rao', 
           'deco','ral','decl','X','Y','Z','lat','lon','H','range','length','svd',
           'lag','vel','pvel', 'hres','vres','ares','vmag','amag']
    ptsarray='['
    gotpts = False
    for fli in flis:
        if 'Points' in fli:
            gotpts = True
            continue
        elif '------' in fli or ' No' in fli:
            continue
        elif gotpts is True and (len(fli) < 2 or 'Notes' in fli):
            gotpts=False
            break
        elif gotpts is True:
            spls = fli.split(',')
            thisrow = '{'
            for h, s in zip(hdr, spls):
                thisrow = thisrow + f'"{h}": "{s.strip()}",'
            thisrow = thisrow[:-1] + '},'
            ptsarray = ptsarray + thisrow
    ptsarray = ptsarray[:-1] + ']'
    ptsarray = '{' + f'"points": {ptsarray}' + '}'
    return ptsarray
