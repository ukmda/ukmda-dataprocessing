# Python module to access the single-station data held in a Glue database
#
# 
import boto3
import pandas as pd


def run_query(client, query, bucket_name, dbname):
    response = client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': dbname},
        ResultConfiguration={'OutputLocation': 's3://{}/tmp/fromglue/'.format(bucket_name)},
    )
    return response


def validate_query(client, query_id):
    resp = ["FAILED", "SUCCEEDED", "CANCELLED"]
    response = client.get_query_execution(QueryExecutionId=query_id)
    # wait until query finishes
    while response["QueryExecution"]["Status"]["State"] not in resp:
        response = client.get_query_execution(QueryExecutionId=query_id)

    return response["QueryExecution"]["Status"]["State"]


def read(query, bucket_name, athena_client, dbname, credentials=None):
    if credentials is None:
        s3_client = boto3.client('s3')
    else:
        s3_client = boto3.client('s3',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'])
    #print('start query: {}\n'.format(query))
    qe = run_query(athena_client, query, bucket_name, dbname)
    _ = validate_query(athena_client, qe["QueryExecutionId"])
    #print('query state: {}\n'.format(qstate))

    file_name = "tmp/fromglue/{}.csv".format(qe["QueryExecutionId"])
    obj = s3_client.get_object(Bucket=bucket_name, Key=file_name)
    return pd.read_csv(obj['Body'])


if __name__ =='__main__':
    # s3 = boto3.resource('s3')
    athena_client = boto3.client(service_name='athena', region_name='eu-west-2')
    bucket_name = 'ukmon-shared'
    # print('Working bucket: {}'.format(bucket_name))

    time_entries_df = read("SELECT dtstamp,filename,y,m,d,h,mi,s FROM singlepq where id='UK000P' and d=2 and y=2022", 
        bucket_name, athena_client, 'ukmonsingledata')
    print(time_entries_df)
