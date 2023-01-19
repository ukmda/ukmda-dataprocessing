#
# python script to get all live JPGs for a specified time
#
import os
import sys
import boto3
from fileformats import ReadUFOCapXML as ufoc


def getLiveJpgs(dtstr, outdir=None, create_txt=False, buck_name=None):
    if outdir is None:
        outdir = dtstr
    os.makedirs(outdir, exist_ok=True)
    if buck_name is None:
        buck_name = os.getenv('UKMONLIVEBUCKET', default='s3://ukmon-live')[5:]
    s3 = boto3.client('s3')
    x = s3.list_objects_v2(Bucket=buck_name,Prefix=f'M{dtstr}')
    if  x['KeyCount'] > 0:
        print(f"found {x['KeyCount']} records, saving to {outdir}")
        for k in x['Contents']:
            key = k['Key']
            if '.xml' in key:
                s3.download_file(buck_name, key, os.path.join(outdir, key))
                x = ufoc.UCXml(os.path.join(outdir, key))
                fn = x.ucxml['ufocapture_record']['@cap'].strip()
                os.remove(os.path.join(outdir, key))
                key = key.replace('.xml', 'P.jpg')
                if len(fn) < 5:
                    outkey = key
                    spls = key.split('_')
                    stationid = spls[-1][:6].lower()
                    dtime = key[1:16]
                    patt = f'FF_{stationid}_{dtime}'
                else:
                    outkey = fn.replace('.fits', '.jpg')
                    patt = fn[:26]
                    stationid = fn[3:9].lower()
                print(key)
                s3.download_file(buck_name, key, os.path.join(outdir, outkey))
                if create_txt is True:
                    createTxtFile(key, outdir)
    else:
        print('no records found')


def createTxtFile(fname, outdir):
    if fname[0] == 'M':
        spls = fname.split('_')
        stationid = spls[-1][:6].lower()
        dtime = fname[1:16]
        patt = f'FF_{stationid}_{dtime}'
        stationid = stationid.lower()
    else:
        patt = fname[:25]
        stationid = fname[3:9].lower()
    txtf = os.path.join(outdir, f'{stationid}.txt')
    if os.path.isfile(txtf):
        os.remove(txtf)
    patt = patt.upper()
    with open(txtf,'w') as outf:
        outf.write(f'{patt}\n{patt.replace("FF_", "FR_")}\n')
    return txtf

if __name__ == '__main__':
    getLiveJpgs(sys.argv[1])
