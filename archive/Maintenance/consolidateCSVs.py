#
# AWS Lambda function to consolidate UKMON CSV files
#
# trigger on Cloudwatch event (daily)
# create rule that triggers the lambda function periodically
#
import boto3
import botocore
import uuid
import os


def lambda_handler(event, context):
    conn = boto3.client('s3')
    s3 = boto3.resource('s3')

    target = 'ukmon-shared'
    pref = 'consolidated/temp/'
    for key in conn.list_objects_v2(Bucket=target, Prefix=pref)['Contents']:
        s3object = key['Key']
        x = s3object.find('M20')
        if x == -1:
            # its not a standard ufoa file, check if its an rms file
            x = s3object.find('UK')
            if x == -1:
                # yep not interested
                continue
            # okay, create the right format output
            x = s3object.find('_20') + 1
            y = x + 4
            yr = s3object[x:y]
            outf = 'consolidated/P_' + yr + '-unified.csv'
        else:
            x = x + 1
            y = x + 4
            yr = s3object[x:y]
            outf = 'consolidated/M_' + yr + '-unified.csv'
        curr = '/tmp/' + str(uuid.uuid4().hex)
        dta = '/tmp/' + str(uuid.uuid4().hex)

        try:
            s3.meta.client.get_object(Bucket=target, Key=outf)
        except botocore.exceptions.ClientError as e:
            # The object does not exist.
            src = {'Bucket': target, 'Key': s3object}

            # sanity check data
            s3.meta.client.download_file(target, s3object, dta)
            linelist = [line.rstrip('\n') for line in open(dta, 'r')]
            lineone = linelist[0]
            startl = lineone[:4]
            if startl == 'Ver,':
                print('New file created from ' + s3object)
                s3.meta.client.copy_object(Bucket=target, Key=outf, CopySource=src)
            else:
                print('Ignored ' + s3object + ' as not valid format')

            # delete the processed file
            print('Processed ' + s3object)
            os.remove(dta)
            s3.meta.client.delete_object(Bucket=target, Key=s3object)
        else:
            s3.meta.client.download_file(target, outf, curr)
            s3.meta.client.download_file(target, s3object, dta)

            linelist = [line.rstrip('\n') for line in open(dta, 'r')]
            uniflist = [line.rstrip('\n') for line in open(curr, 'r')]

            # sanity check data
            lineone = linelist[0]
            startl = lineone[:4]
            if startl == 'Ver,':
                print('merging ' + s3object)
                newlist = uniflist[0:1] + sorted(set(uniflist[1:] + linelist[1:]))
                with open(curr, 'w') as fout:
                    fout.write('\n'.join(newlist))
                s3.meta.client.upload_file(curr, target, outf)
            else:
                print('Ignored ' + s3object + ' as not valid format')

            os.remove(curr)
            os.remove(dta)
            # delete the processed file
            s3.meta.client.delete_object(Bucket=target, Key=s3object)
    return 0
