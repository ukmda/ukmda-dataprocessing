# Copyright (c) Mark McIntyre, 2024-

# python script to report on and manage camera login details and keys
# this looks at both the AWS IAM accounts and the Unix sftp accounts

# getUserAndKeyInfo.py audit        = An audit report of unused or stale acconts and keys
# getUserAndKeyInfo.py dormant      - reports on dormant AWS accounts
# getUserAndKeyInfo.py update xxxx  - issues a new key to site xxxx and deploys it to the corresponding unix homedirs
# getUserAndKeyInfo.py delete xxxx  - deletes user xxxx, their keys and associated corresponding unix homedirs

import boto3
import datetime
import time
import pandas as pd
import os
import sys
import requests
import subprocess
from reports.CameraDetails import loadLocationDetails
from botocore.exceptions import ClientError

MAXAGE = 90     # connections older than this are regarded stale

if sys.platform == 'win32':
    csvdir = 'f:/videos/meteorcam/usermgmt/csvkeys'
    lnxdir='/home/ec2-user/keymgmt/csvkeys'
else:
    csvdir='/home/ec2-user/keymgmt/csvkeys'
    lnxdir='/home/ec2-user/keymgmt/csvkeys'


def checkIfOnGMN(camid):
    """
    Check if a station is still on GMN, and if so, when it last uploaded.
    """
    baseurl = f'https://globalmeteornetwork.org/weblog/{camid[0:2]}/{camid}/latest/index.html'
    r = requests.get(baseurl)
    if r.status_code != 200:
        return False, f'data for {camid} not available'
    text = r.text
    rb=text.find('Recording begin: ')
    if rb < 50:
        return False, f'data for {camid} not available'
    rb = rb + len('Recording begin: ')
    lastdt = text[rb:rb+19]
    try:
        dtval = datetime.datetime.strptime(lastdt, '%Y-%m-%d %H:%M:%S')
        return True, dtval
    except:
        return False, "date not parseable"


def getLinkedCams(site, camdets, active=False):
    """
    Given a site name, find the owner, status GMN and ukmon IDs of cameras at that site
    """
    if site == 'Testpi4':
        return 'markmcintyre@googlemail.com', [1], ['UK0006'], ['testpi4']
    fltlist = camdets[camdets.site.str.lower()==site.lower()]
    if active:
        fltlist = fltlist[fltlist.active==1]
    if len(fltlist) > 0:
        email = str(fltlist.iloc[0].eMail)
        active = list(fltlist.active)
        rmsids = list(fltlist.stationid)
        locs = [x.lower() + '_' + y.lower() for x,y in zip(fltlist.site, fltlist.direction)]
    else:
        email = 'no match'
        active = []
        rmsids = []
        locs = []
    return email, active, rmsids, locs


def auditReport():
    """
    Generate an audit report showing accounts with stale passwords, stale keys, unused keys or extra keys 
    """
    stalepwds, stalekeys, unusedkeys, twokeys = getKeyStatuses()
    print('\nAccounts with Stale Passwords\n============================')
    if len(stalepwds) == 0:
        print('None')
    else:
        print(stalepwds)
    print('\nAccounts with stale keys\n========================')
    if len(stalekeys) == 0:
        print('None')
    else:
        print(stalekeys)
    print('\nAccounts with unused keys\n========================')
    if len(unusedkeys) == 0:
        print('None')
    else:
        print(unusedkeys)
    print('\nAccounts with two keys\n======================')
    if len(twokeys) == 0:
        print('None')
    else:
        print(twokeys)


def getKeyStatuses(excludeadm=False):
    """
    """
    maxage = int(os.getenv('MAXAGE', default=MAXAGE))
    now = datetime.datetime.now()
    iamc = boto3.client('iam')
    try:
        res = iamc.get_credential_report()
        print('got the report')
    except ClientError as error:
        err = error.response['Error']['Code']
        if err == 'CredentialReportNotPresentException' or err == 'CredentialReportExpiredException':
            print('creating credentials report')
            res = iamc.generate_credential_report()
            time.sleep(60)
        elif err == 'CredentialReportNotReadyException':
            print('report not ready, sleeping 30s')
            time.sleep(30)
        gotit = False
        while not gotit:
            try:
                res = iamc.generate_credential_report()
                time.sleep(60)
                res = iamc.get_credential_report()
                gotit = True
                print('got the report')
            except ClientError:
                time.sleep(30)
                print('waiting for report')

    txtcontent = res['Content'].decode('utf-8').split('\n')
    data = [sub.split(",") for sub in txtcontent]
    df = pd.DataFrame(data[1:], columns=data[:1][0])
    df2 = df.filter(items=['user', 'password_enabled','password_last_used', 'password_last_changed', 
        'access_key_1_active', 'access_key_1_last_rotated','access_key_1_last_used_date',
        'access_key_2_active', 'access_key_2_last_rotated', 'access_key_2_last_used_date'])
    # check accounts with passwords
    pd.options.mode.chained_assignment = None
    newdf = df2[df2.password_enabled == 'true']
    newdf['pwage'] = [(now-datetime.datetime.strptime(x,'%Y-%m-%dT%H:%M:%SZ')).days for x in newdf.password_last_changed]
    newdf = newdf[newdf.pwage > maxage]
    stalepwds = newdf.filter(items=['user','pwage'])

    # check age of active keys
    newdf = df2[df2.access_key_1_active == 'true']
    newdf = newdf[newdf.access_key_1_last_used_date!='N/A']
    newdf['k1age'] = [(now-datetime.datetime.strptime(x,'%Y-%m-%dT%H:%M:%SZ')).days for x in newdf.access_key_1_last_rotated]
    newdf['k1used'] = [(now-datetime.datetime.strptime(x,'%Y-%m-%dT%H:%M:%SZ')).days for x in newdf.access_key_1_last_used_date]
    newdf = newdf[newdf.k1age > maxage]
    if excludeadm:
        newdf = newdf[newdf.password_enabled == 'false']
    newdf = newdf.filter(items=['user','k1age','k1used'])

    newdf2 = df2[df2.access_key_1_active == 'true']
    newdf2 = newdf2[newdf2.access_key_1_last_used_date=='N/A']
    newdf2['k1age'] = [(now-datetime.datetime.strptime(x,'%Y-%m-%dT%H:%M:%SZ')).days for x in newdf2.access_key_1_last_rotated]
    newdf2['k1used'] = ['N/A'] * len(newdf2)
    newdf2 = newdf2[newdf2.k1age > maxage]
    if excludeadm:
        newdf2 = newdf2[newdf2.password_enabled == 'false']
    newdf2 = newdf2.filter(items=['user','k1age','k1used'])
    stalekeys = pd.concat([newdf, newdf2])

    # check last-used-date of active keys
    newdf = df2[df2.access_key_1_active == 'true']
    newdf = newdf[newdf.access_key_1_last_used_date!='N/A']
    newdf['k1age'] = [(now-datetime.datetime.strptime(x,'%Y-%m-%dT%H:%M:%SZ')).days for x in newdf.access_key_1_last_rotated]
    newdf['k1used'] = [(now-datetime.datetime.strptime(x,'%Y-%m-%dT%H:%M:%SZ')).days for x in newdf.access_key_1_last_used_date]
    newdf = newdf[newdf.k1used > maxage]
    newdf = newdf[newdf.k1age > 2]
    newdf = newdf.filter(items=['user','k1age','k1used'])

    newdf2 = df2[df2.access_key_1_active == 'true']
    newdf2 = newdf2[newdf2.access_key_1_last_used_date=='N/A']
    newdf2['k1age'] = [(now-datetime.datetime.strptime(x,'%Y-%m-%dT%H:%M:%SZ')).days for x in newdf2.access_key_1_last_rotated]
    newdf2['k1used'] = ['N/A'] * len(newdf2)
    newdf2 = newdf2[newdf2.k1age > 2]
    newdf2 = newdf2.filter(items=['user','k1age','k1used'])
    unusedkeys = pd.concat([newdf, newdf2])

    # check for accounts with two keys
    newdf = df2[df2.access_key_2_active == 'true']
    twokeys = newdf.filter(items=['user','k2age','access_key_2_last_used_date'])

    return stalepwds, stalekeys, unusedkeys, twokeys


def getDormantUsers():
    """ 
    Get a list of dormant AWS accounts, keys, and corresponding camera and unix IDs 
    """
    camdets = loadLocationDetails()
    maxage = int(os.getenv('MAXAGE', default=MAXAGE))
    print(f'Cameras not active for more than {maxage} days')
    print('=========================================')
    _, _, unusedkeys, _ = getKeyStatuses()
    for _, rw in unusedkeys.iterrows():
        uid = rw.user
        email, active, ids, locs = getLinkedCams(uid, camdets, active=True)
        statuses = []
        for id in ids:
            sts,dt = checkIfOnGMN(id)
            if sts:
                statuses.append(dt.strftime('%Y-%m-%d'))
            else:
                statuses.append('n/a')
        print(f'{uid}, {rw.k1age}, {rw.k1used}, {email}, {active}, {ids}, {locs}, {statuses}')


def createAndSaveKey(uid):
    """
    Create a new key for a IAM user and save it safely
    """
    iamc = boto3.client('iam')
    keyresp = iamc.create_access_key(UserName=uid)
    if 'AccessKey' not in keyresp:
        print('key creation failed')
        return ''
    key = keyresp['AccessKey']
    csvf = os.path.join(csvdir, f'{uid}.csv')
    with open(csvf,'w') as outf:
        outf.write('Access key ID,Secret access key\n')
        outf.write(f'{key["AccessKeyId"]},{key["SecretAccessKey"]}\n')
    return key["AccessKeyId"]


def copyToHomedirs(uid, camlocs):
    if sys.platform == 'win32':
        com = f'scp {csvdir}/{uid}.csv ukmonhelper2.:{lnxdir}' 
        subprocess.call(com, shell=True, cwd=csvdir)
        for cam in camlocs:
            com = f'ssh ukmonhelper2. "sudo cp {lnxdir}/{uid}.csv /var/sftp/{cam}/{cam}.csv"'
            subprocess.call(com, shell=True, cwd=csvdir)
    else:
        for cam in camlocs:
            com = f'sudo cp {lnxdir}/{uid}.csv /var/sftp/{cam}/{cam}.csv'
            subprocess.call(com, shell=True, cwd=lnxdir)
    return 


def issueNewKey(uid, force=False):
    """
    issue a new AWS key for a site and deploy it to the correct unix folders
    but check first if the key is due for replacement 
    and only replace it if either its old, or 'force' is True
    """
    maxage = int(os.getenv('MAXAGE', default=MAXAGE))
    now = datetime.datetime.now(datetime.timezone.utc)
    camdets = loadLocationDetails()
    _, _, _, locs = getLinkedCams(uid, camdets, active=True)
    iamc = boto3.client('iam')
    resp = iamc.list_access_keys(UserName=uid)
    if 'AccessKeyMetadata' not in resp:
        print('adding new key from scratch')
        createAndSaveKey(uid)
        copyToHomedirs(uid, locs)
        return
    else:
        numkeys = len(resp['AccessKeyMetadata'])
        # can only have two keys so delete the 2nd of them
        if numkeys == 2: 
            k = resp['AccessKeyMetadata'][1]
            keyid = k['AccessKeyId']
            lastused = 'never'
            luresp = iamc.get_access_key_last_used(AccessKeyId=keyid)
            if 'LastUsedDate' in luresp['AccessKeyLastUsed']:
                lastused = luresp['AccessKeyLastUsed']['LastUsedDate']
            print(f'already two keys, deleting {keyid} last used on {lastused}')
            iamc.delete_access_key(UserName=uid, AccessKeyId=keyid)
        # create a new key
        if numkeys > 0:
            k = resp['AccessKeyMetadata'][0]
            oldkeyid = k['AccessKeyId']
            oldkeyage = (now - k['CreateDate']).days
            if oldkeyage <= maxage and force is False:
                print(f'key {oldkeyid} for {uid} is only {oldkeyage} days old, not replacing')
                return 
        newkey = createAndSaveKey(uid)
        copyToHomedirs(uid, locs)
        # and then delete the old one
        if numkeys > 0:
            lastused = 'never'
            luresp = iamc.get_access_key_last_used(AccessKeyId=oldkeyid)
            if 'LastUsedDate' in luresp['AccessKeyLastUsed']:
                lastused = luresp['AccessKeyLastUsed']['LastUsedDate']
            print(f'new key {newkey} issued to replace {oldkeyid}, last used on {lastused}')
            iamc.delete_access_key(UserName=uid, AccessKeyId=oldkeyid)
    return 


def deleteDormantAwsUser(uid, force=False):
    """
    Delete a dormant AWS non-interactive account
    Checks are done that the user exists and is not a console-user
    """
    maxage = int(os.getenv('MAXAGE', default=MAXAGE))
    now = datetime.datetime.now(datetime.timezone.utc)
    iamc = boto3.client('iam')
    camdets = loadLocationDetails()
    _, _, cams, locs = getLinkedCams(uid, camdets, active=True)
    print(f'checking {uid} linked to {cams} at {locs}')
    try:
        resp = iamc.get_user(UserName=uid)
    except Exception:
        print(f'user {uid} not found')
        return 
    if 'PasswordLastUsed' in resp:
        print(f'user {uid} is a console user')
        return 
    resp = iamc.list_access_keys(UserName=uid)
    if 'AccessKeyMetadata' in resp:
        k = resp['AccessKeyMetadata'][0]
        oldkeyid = k['AccessKeyId']
        oldkeyage = (now - k['CreateDate']).days
        if oldkeyage <= maxage and force is False:
            print(f'key {oldkeyid} for {uid} is only {oldkeyage} days old, not deleting')
            return 
    print('pausing for thought....')
    time.sleep(30) 
    resp = iamc.list_access_keys(UserName=uid)
    if 'AccessKeyMetadata' in resp:
        for k in resp['AccessKeyMetadata']:
            keyid = k['AccessKeyId']
            iamc.delete_access_key(UserName=uid, AccessKeyId=keyid)
    resp = iamc.list_user_policies(UserName=uid)
    if 'PolicyNames' in resp:
        for k in resp['PolicyNames']:
            iamc.delete_user_policy(UserName=uid, PolicyName=k)
    resp = iamc.list_attached_user_policies(UserName=uid)
    if 'AttachedPolicies' in resp:
        for k in resp['AttachedPolicies']:
            iamc.detach_user_policy(UserName=uid, PolicyArn=k['PolicyArn'])
    resp = iamc.list_groups_for_user(UserName=uid)
    if 'Groups' in resp:
        for k in resp['Groups']:
            iamc.remove_user_from_group(UserName=uid, GroupName=k['GroupName'])
    iamc.delete_user(UserName=uid)
    return 


def rollKeysForUsers(nusers=3):
    """ 
    Get a list of stale keys, then roll a random sample of them
    """
    camdets = loadLocationDetails()
    _, stalekeys, _, _ = getKeyStatuses(excludeadm=True)
    if len(stalekeys) == 0:
        return 
    sampledf = stalekeys.sample(n=nusers)
    for _, rw in sampledf.iterrows():
        uid = rw.user
        if 'testtraj' in uid:
            continue
        _, _, _, locs = getLinkedCams(uid, camdets, active=True)
        print(f'rolling key for {uid}, old key age {rw.k1age} last used {rw.k1used} days ago affects {locs}')
        issueNewKey(uid)
    return 


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: getUserAndKeyInfo audit|dormant|delete|update|autoroll')
        exit(0)
    if sys.argv[1] == 'audit':
        auditReport()
    if sys.argv[1] == 'dormant':
        getDormantUsers()
    if sys.argv[1] == 'autoroll':
        rollKeysForUsers(nusers=5)
    elif sys.argv[1] == 'update':
        if len(sys.argv) < 3:
            print('need a location code')
            exit(1)
        force = False
        if len(sys.argv) == 4:
            force = True
        issueNewKey(sys.argv[2], force=force)
    elif sys.argv[1] == 'delete':
        if len(sys.argv) < 3:
            print('need a location code')
            exit(1)
        deleteDormantAwsUser(sys.argv[2])

    
