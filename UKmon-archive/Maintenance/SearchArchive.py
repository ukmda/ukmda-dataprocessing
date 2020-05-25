# python routine to search the S3 archive for specific criteria
import sys, os, shutil, glob, datetime
import numpy, math
import boto3


def FindMatch(bucket, csvfile, yr, mth, dy, hr, mn) :
    s3 = boto3.client('s3')

    resp = s3.select_object_content(
        Bucket=bucket,
        Key=csvfile,
        ExpressionType='SQL',
        Expression="SELECT * FROM s3object s where " +
            "s.\"Y(UT)\" like '"+f'{yr:04}'+"' and s.\"M(UT)\" like '" +f'{mth:02}'+"' " +
            "and  s.\"D(UT)\" like '" + f'{dy:02}'+"' " +
            "and s.\"H(UT)\" like '"+f'{hr:02}'+"' and s.\"M\" like '"+f'{mn:02}'+"'",
        InputSerialization = {'CSV': {"FileHeaderInfo": "Use"}, 'CompressionType': 'NONE'},
        OutputSerialization = {'CSV': {}},
    )

    for event in resp['Payload']:
        if 'Records' in event:
            records = event['Records']['Payload'].decode('utf-8')
            print(records)
        elif 'Stats' in event:
            statsDetails = event['Stats']['Details']
            print("Stats details bytesScanned: ")
            print(statsDetails['BytesScanned'])
            print("Stats details bytesProcessed: ")
            print(statsDetails['BytesProcessed'])
            print("Stats details bytesReturned: ")
            print(statsDetails['BytesReturned'])

def main() :
    FindMatch("ukmon-shared", "consolidated/M_2020-unified.csv", 2020, 1, 8, 1, 11)

if __name__ == '__main__':
    main()
