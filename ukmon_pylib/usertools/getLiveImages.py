#
# python script to get all live JPGs for a specified time
#
import os
import sys
import boto3
import tempfile
from fileformats import ReadUFOCapXML as ufoc


def getLiveJpgs(dtstr, outdir):
    os.makedirs(outdir, exist_ok=True)
    s3 = boto3.client('s3')
    buck = os.getenv('UKMONLIVEBUCKET', default='s3://ukmon-live')[5:]
    x = s3.list_objects_v2(Bucket=buck,Prefix=f'M{dtstr}')
    if  x['KeyCount'] > 0:
        print(f"found {x['KeyCount']} records, saving to {outdir}")
        for k in x['Contents']:
            key = k['Key']
            if '.xml' in key:
                s3.download_file(buck, key, os.path.join(outdir, key))
                x = ufoc.UCXml(os.path.join(outdir, key))
                fn = x.ucxml['ufocapture_record']['@cap'].strip()
                os.remove(os.path.join(outdir, key))
                key = key.replace('.xml', 'P.jpg')
                if len(fn) < 5:
                    outkey = key
                    spls = key.split('_')
                    stationid = spls[4][:6].lower()
                    dtime = key[1:16]
                    patt = f'FF_{stationid}_{dtime}'
                else:
                    outkey = fn.replace('.fits', '.jpg')
                    patt = fn[:26]
                    stationid = fn[3:9].lower()
                print(key)
                s3.download_file(buck, key, os.path.join(outdir, outkey))
                txtf = os.path.join(f'{stationid}.txt')
                if os.path.isfile(txtf):
                    os.remove(txtf)
                with open(txtf,'w') as outf:
                    outf.write(f'{patt}\n{patt.replace("FF_", "FR_")}\n')



    else:
        print('no records found')

if __name__ == '__main__':
    getLiveJpgs(sys.argv[1], sys.argv[2])
