# Copyright (c) Mark McIntyre

import hvac

hcvURL = 'http://testpi4:8200'


# Authentication
def hcvAuth(vault_token_file):
    vault_token=open(vault_token_file, 'r').readlines()[0].strip()
    try:
        client = hvac.Client(url=hcvURL,token=vault_token)
    except Exception as e:
        print('unable to authenticate', e)
    return client


# Writing a secret
def hcvWriteSecret(client, secretpath, secretname, secretvalue):
    try:
        create_response = client.secrets.kv.v2.create_or_update_secret(
            path=secretpath, secret={f'{secretname}':f'{secretvalue}'})
        if create_response.ok is True:
            return True
        else:
            print(create_response.reason)
            return False
    except Exception as e:
        print('problem writing secret', e)
        return False


# Reading a secret
def hcvReadSecret(client, secretpath, secretname):
    try:
        read_response = client.secrets.kv.read_secret_version(path=secretpath, raise_on_deleted_version=True)
        password = read_response['data']['data'][secretname]
        return password
    except Exception as e:
        print('problem reading secret', e)
        return ''
