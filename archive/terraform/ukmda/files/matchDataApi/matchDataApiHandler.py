# Copyright (C) 2018-2023 Mark McIntyre
import datetime
import os
import boto3
import json


def lambda_handler(event, context):
    target = os.getenv('SRCHBUCKET', default='ukmda-shared')
    webbuck = os.getenv('WEBBUCKET', default='ukmda-website')
    #print('received event', json.dumps(event))
    qs = event['queryStringParameters']
    if qs is None:
        return {
            'statusCode': 200,
            'body': 'usage: detections?reqtyp=xxx&reqval=yyyy[&points=1]'
        }
    reqtyp = qs['reqtyp']
    reqval = qs['reqval']
    points = False
    if 'points' in qs:
        points = True

    if reqtyp not in ['matches','detail','station','summary']:
        res = '{"invalid request type - must be one of \'matches\', \'details\', \'station\',\'summary\'"}'
    else:
        print(f'{reqtyp} {reqval} {points}')
        if reqtyp == 'summary':
            d1 = datetime.datetime.strptime(reqval, '%Y%m%d')
            idxfile = 'matches/matched/matches-full-{:04d}.csv'.format(d1.year)
            res = '{"no matches"}'
            fieldlist = '_localtime,_mjd,_sol,_ID1,_amag,_ra_o,_dc_o,_ra_t,_dc_t,_elng,_elat,_vo,_vi,_vg,_vs,_a,_q,_e,_p,_peri,_node,_incl,'\
                '_stream,_mag,_dur,_lng1,_lat1,_H1,_lng2,_lat2,_H2,_LD21,_az1r,_ev1r,_Nts,_Nos,_leap,_tme,_dt,'\
                'dtstamp,orbname,iau,name,mass,pi,Q,true_anom,EA,MA,Tj,T,last_peri,jacchia1,Jacchia2,numstats,stations'
            expr = f"SELECT {fieldlist} from s3object s where s._localtime like '_{reqval}%'"
            fhi = {"FileHeaderInfo": "Use"}
        elif reqtyp == 'matches':
            d1 = datetime.datetime.strptime(reqval, '%Y%m%d')
            idxfile = 'matches/matched/matches-full-{:04d}.csv'.format(d1.year)
            res = '{"no matches"}'
            expr = "SELECT s.orbname from s3object s where s._localtime like '_{}%'".format(reqval)
            fhi = {"FileHeaderInfo": "Use"}
        elif reqtyp == 'detail':
            idxfile = 'matches/matched/matches-full-{}.csv'.format(reqval[:4])
            res = '{"event not found"}'
            expr = "SELECT * from s3object s where s.orbname='{}'".format(reqval)
            fhi = {"FileHeaderInfo": "Use"}
        elif reqtyp == 'station':
            statid = qs['statid']
            d1 = datetime.datetime.strptime(reqval, '%Y%m%d')
            idxfile = 'matches/matched/matches-full-{:04d}.csv'.format(d1.year)
            res = '{"no matches"}'
            expr = "SELECT s.orbname from s3object s where s._localtime like '_{}%' and s.stations like '%{}%'".format(reqval, statid)
            fhi = {"FileHeaderInfo": "Use"}

        s3 = boto3.client('s3')
        resp = s3.select_object_content(Bucket=target, Key=idxfile, ExpressionType='SQL',
            Expression=expr, InputSerialization={'CSV': fhi, 'CompressionType': 'NONE'}, OutputSerialization={'JSON': {}}, )
        res=''
        for event in resp['Payload']:
            if 'Records' in event:
                res = res + event['Records']['Payload'].decode('utf-8')
        if reqtyp == 'summary':
            res = '[' + res.replace('}\n{','},\n{') +']'
        if points is True:
            print('requested points')
            url = json.loads(res)['img']
            url = url.replace('ground_track.png','report.txt')
            reppth = url.split('//', 1)[1].split('/',1)[1]
            _, repname = os.path.split(reppth)
            try:
                tmpfname = f'/tmp/{repname}'
                s3.download_file(webbuck, reppth, tmpfname)
                flis = open(tmpfname, 'r').readlines()
                os.remove(tmpfname)
                res = fileToJsonString(flis)
            except Exception:
                print('report file unavailable')
                res = '{"points": "unavailable"}'
    
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
