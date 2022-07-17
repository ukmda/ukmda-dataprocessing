#
# Python module to create a ukmon keyfile from an AWS json file
#

import json
import sys
import os


def createKeyFile(inf, outp):
    with open(inf, 'r') as inp:
        data = json.load(inp)

    user = data['AccessKey']['UserName']
    key = data['AccessKey']['AccessKeyId']
    secr = data['AccessKey']['SecretAccessKey']

    pth, fname = os.path.split(inf)

    outf = os.path.join(outp, fname.split('.')[0].lower() + '.key')
    with open(outf, 'w') as ouf:
        ouf.write('export AWS_ACCESS_KEY_ID={}\n'.format(key))
        ouf.write('export AWS_SECRET_ACCESS_KEY={}\n'.format(secr))
        ouf.write('export AWS_DEFAULT_REGION=eu-west-1\n')
        ouf.write('export CAMLOC="{}"\n'.format(user))

    with open(os.path.join(pth, '../arch/all.key'), 'r') as inf:
        lines = inf.readlines()
    arckey = os.path.join(outp, '../arch/', fname.split('.')[0].lower() + '.key')
    with open(arckey, 'w') as ouf:
        ouf.write('{}'.format(lines[0]))
        ouf.write('{}'.format(lines[1]))
        ouf.write('{}'.format(lines[2]))
        ouf.write('export S3FOLDER="archive/{}/"'.format(user))


if __name__ == '__main__':
    createKeyFile(sys.argv[1], sys.argv[2])
