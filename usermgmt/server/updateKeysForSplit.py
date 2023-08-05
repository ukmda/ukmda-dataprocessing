import os
import boto3
import json
import sys
import shutil


def createKeyFile(livekey, archkey, location):
    archbucket = os.getenv('SRCBUCKET', default='ukmda-shared')
    livebucket = os.getenv('LIVEBUCKET', default='ukmon-live')
    webbucket = os.getenv('WEBSITEBUCKET', default='ukmda-website')
    outf = 'keys/' + location.lower() + '.key'
    if archkey is None:
        return outf
    with open(outf, 'w') as ouf:
        ouf.write(f"export AWS_ACCESS_KEY_ID={archkey['AccessKey']['AccessKeyId']}\n")
        ouf.write(f"export AWS_SECRET_ACCESS_KEY={archkey['AccessKey']['SecretAccessKey']}\n")
        ouf.write(f"export LIVE_ACCESS_KEY_ID={livekey['AccessKey']['AccessKeyId']}\n")
        ouf.write(f"export LIVE_SECRET_ACCESS_KEY={livekey['AccessKey']['SecretAccessKey']}\n")
        ouf.write('export AWS_DEFAULT_REGION=eu-west-1\n')
        ouf.write(f'export CAMLOC="{location}"\n')
        ouf.write(f'export S3FOLDER="archive/{location}/"\n')
        ouf.write(f'export ARCHBUCKET={archbucket}\n')
        ouf.write(f'export LIVEBUCKET={livebucket}\n')
        ouf.write(f'export WEBBUCKET={webbucket}\n')
        ouf.write('export ARCHREGION=eu-west-2\n')
        ouf.write('export LIVEREGION=eu-west-1\n')
        ouf.write('export MATCHDIR=matches/RMSCorrelate\n')
    os.chmod(outf, 0o666)
    return outf


def readOldKeyFile(camid):
    keyf= f'/var/sftp/{camid}/live.key'
    if not os.path.isfile(keyf):
        print(f'invalid camid {camid}')
        exit()
    flines = open(keyf, 'r').readlines()
    camloc = None
    for li in flines:
        if 'AWS_ACCESS_KEY_ID' in li:
            oldkey = li.split('=')[1].strip()
        elif 'AWS_SECRET_ACCESS_KEY' in li:
            oldsec= li.split('=')[1].strip()
        elif 'CAMLOC' in li:
            camloc= li.split('=')[1].strip().strip('"')
        elif 'LIVE_ACCESS_KEY_ID' in li:
            print('already processed')
            exit()
    if camloc is None: 
        print('malformed key file - no camloc')
        exit()
    return {'AccessKey': {'AccessKeyId': oldkey, 'SecretAccessKey': oldsec}}, camloc


def createNewUser(location):
    archuserdets = 'users/' + location + '_arch.txt'
    archkeyf = 'rawkeys/arch/' + location + '.key'
    archprof = os.getenv('ARCH_PROFILE', default='ukmda_admin')
    archconn = boto3.Session(profile_name=archprof)
    iamc = archconn.client('iam')
    sts = archconn.client('sts')
    acct = sts.get_caller_identity()['Account']
    policyarn = 'arn:aws:iam::' + acct + ':policy/UkmonLive'
    policyarn2 = 'arn:aws:iam::' + acct + ':policy/UKMDA-shared'
    try: 
        _ = iamc.get_user(UserName=location)
        print('location exists, not adding it')
        archkey = None
    except Exception:
        print('new location')
        usr = iamc.create_user(UserName=location)
        with open(archuserdets, 'w') as outf:
            outf.write(str(usr))
        archkey = iamc.create_access_key(UserName=location)
        with open(archkeyf, 'w') as outf:
            outf.write(json.dumps(archkey, indent=4, sort_keys=True, default=str))
        with open(os.path.join('csvkeys', location + '_arch.csv'),'w') as outf:
            outf.write('Access key ID,Secret access key\n')
            outf.write('{},{}\n'.format(archkey['AccessKey']['AccessKeyId'], archkey['AccessKey']['SecretAccessKey']))
        _ = iamc.attach_user_policy(UserName=location, PolicyArn=policyarn)
        _ = iamc.attach_user_policy(UserName=location, PolicyArn=policyarn2)
    os.chmod(archuserdets, 0o666)
    os.chmod(archkeyf, 0o666)
    return archkey


def copyKeyFileToTarget(newkeyfile, camid):
    targkeyf = f'/var/sftp/{camid}/live.key'
    bkpkeyf = newkeyfile + '.bkp'
    if not os.path.isfile(bkpkeyf):
        shutil.copyfile(targkeyf, bkpkeyf)
    shutil.copyfile(newkeyfile, targkeyf)
    return 


if __name__ == '__main__':
    os.chdir('/home/ec2-user/keymgmt')
    os.makedirs('users/', exist_ok=True)
    os.makedirs('csvkeys/', exist_ok=True)
    os.makedirs('rawkeys/arch/', exist_ok=True)
    os.makedirs('keys/', exist_ok=True)

    camid = sys.argv[1]
    print(f'processing {camid}... ', end='')
    sys.stdout.flush()
    oldkey, location = readOldKeyFile(camid)
    archkey = createNewUser(location)
    newkeyfile = createKeyFile(oldkey, archkey, location)
    copyKeyFileToTarget(newkeyfile, camid)
