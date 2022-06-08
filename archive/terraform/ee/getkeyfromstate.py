import json
userid = 'ukmonreadonly'
keyid = 'ukmro_key'

with open('terraform.tfstate','r') as inf:
    jsd = json.load(inf)
keyfs = [x for x in jsd['resources'] if x['type'] == 'aws_iam_access_key']
keyf = [x for x in keyfs if x['name'] =='ukmro_key'][0]
id = keyf['instances'][0]['attributes']['id']
secret = keyf['instances'][0]['attributes']['secret']
with open(f'{userid}.key','w') as outf:
    outf.write(f'AWS_ACCESS_KEY_ID={id}\n')
    outf.write(f'AWS_SECRET_ACCESS_KEY={secret}\n')
