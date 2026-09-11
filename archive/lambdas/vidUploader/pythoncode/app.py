import os
import sys
from email import policy, message_from_bytes
import boto3
import requests
from shutil import make_archive, rmtree
from tempfile import mkdtemp

targetBucket = 'ukmda-shared'


def lambda_handler(event, context):
    print('starting')
    s3 = boto3.client('s3')

    if 'Records' not in event:
        print('no record')
        return 
    record = event['Records'][0]
    print(record)
    if 'eventSource' not in record:
        print('no eventSource')
        return 

    ############################################################
    #
    # get the email details and extract the information we need
    key = record['s3']['object']['key']
    #key = 'fireballs/videouploads/raw/' + record['ses']['mail']['messageId']
    try:
        print(f"getting {key} from {targetBucket}")
        fsobj = s3.get_object(Bucket=targetBucket, Key=key)
    except Exception:
        print(f'email object {key} not found')
        return
    print(f"reading {key}")

    try:
        raw_mail = fsobj['Body'].read()
        msg = message_from_bytes(raw_mail, policy=policy.default)
        bdy = msg.get_body('plain')
    except Exception as e:
        print('unable to find message body')
        print(e)
        return
    
    msgbdy = bdy.get_content()
    lines = msgbdy.replace('\r','').split('\n')

    if 'Link:' not in lines:
        print(f'Link field missing, unable to continue')
        return 

    fromline = [x for x in lines if 'From:' in x]
    datetime = [x for x in lines if 'Subject:' in x]
    emailadd = [x for x in lines if 'email:' in x]
    if not fromline or not datetime or not emailadd:
        print(f'From, Date or email missing, unable to continue')
        return 

    uploader = fromline[0].split(':')[1].strip()
    email = emailadd[0].split(':')[1].strip()
    orbname = datetime[0].split(':')[1].strip()

    linkline = lines.index('Link:')
    bdyline = [x for x in lines if 'Message Body:' in x]
    if len(bdyline) > 0:
        commentline = lines.index(bdyline[0])
        for i in range(commentline, linkline):
            if i == commentline:
                comment = lines[i].split(':')[1].strip()
            else:
                comment += lines[i]+ ' '
    else:
        comment = 'No remarks'

    origname = lines[linkline+1].strip()
    origext = os.path.splitext(origname)[1]
    link = lines[linkline+2].strip().replace('<https','https').replace('>','')

    tmpdir = mkdtemp()

    ############################################################
    #
    # create folder and store artefacts in it for zipping

    localdir = os.path.join(tmpdir, orbname[:15])
    os.makedirs(os.path.join(localdir, 'mp4s'), exist_ok=True)
    os.makedirs(os.path.join(localdir, 'notes'), exist_ok=True)

    ############################################################
    #
    # create a plaintext summary and save it on S3

    vidName = f"{orbname[:15]}_{uploader.replace(' ','_')}{origext}"
    fileName = f"{orbname[:15]}_{uploader.replace(' ','_')}.txt"
    filePath = os.path.join(localdir, 'notes', fileName)
    with open(filePath, 'w') as fp:
        fp.write(f'{uploader}\n')
        fp.write(f'{orbname}\n')
        fp.write(f'{vidName}\n')
        fp.write(f'{comment}')

    tmpf = 'fireballs/videouploads/' + fileName
    s3.upload_file(Bucket=targetBucket, Key=tmpf, Filename=filePath, ExtraArgs={'ContentType': "text/plain"})
    print('uploaded plaintext')

    ############################################################
    #
    # get the video from the ukmeteornetwork.org server

    vidPath = os.path.join(localdir, 'mp4s', vidName)
    
    with requests.get(link, stream=True) as r:
        r.raise_for_status()
        with open(vidPath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)

    print('got video from link')

    ############################################################
    #
    # in debug mode upload a copy of it to S3 for reference
    if int(os.getenv('DEBUG', default=0)) == 1:
        vidtype = origext[1:]
        tmpf = 'fireballs/videouploads/' + vidName
        s3.upload_file(Bucket=targetBucket, Key=tmpf, Filename=vidPath, ExtraArgs={'ContentType': f'video/{vidtype}'})

    ############################################################
    #
    # get the pickle file from the S3 archive
    pickfile = f'matches/RMSCorrelate/trajectories/{orbname[:4]}/{orbname[:6]}/{orbname[:8]}/{orbname}/{orbname[:15]}_trajectory.pickle'
    localpick = os.path.join(localdir, f'{orbname[:15]}_trajectory.pickle')
    try:
        s3.download_file(Bucket=targetBucket, Key=pickfile, Filename=localpick)
        print('got pickle')
    except Exception as e:
        print(f'unable to get pickle {pickfile}')
        print(e)
        # with no pickle we can't proceed. 
        return 

    ############################################################
    #
    # make the zip file
    zipname = os.path.join(os.getenv('TMP'), f'{orbname[:15]}')
    make_archive(zipname, 'zip',root_dir=localdir, base_dir = '.')

    ############################################################
    #
    # upload the zip file so it can be processed
    tmpf = 'fireballs/uploads/' + f'{orbname[:15]}.zip'
    s3.upload_file(Bucket=targetBucket, Key=tmpf, Filename=f'{zipname}.zip', ExtraArgs={'ContentType': 'application/zip'})
    print('uploaded zip')

    ############################################################
    #
    # clean up after ourselves
    try:
        rmtree(tmpdir)
    except Exception:
        print(f'unable to remove {tmpdir}')
        
    print('done')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        msg = {'messageId': sys.argv[1]}
    else:
        msg = {'messageId': '4k5581gt9drndeof7v46ol8jqkq9e0k8f4nqr4o1'}
    ml = {'mail': msg}
    ses = {'ses': ml, 'eventSource': 'aws:ses'}
    recs = []
    recs.append(ses)
    recorddets = {'Records': recs}
    print(f'processing {msg}')
    print(f'details{recorddets}')
    lambda_handler(recorddets, 0)
