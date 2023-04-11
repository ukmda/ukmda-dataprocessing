# testing vault

# set the default to JSON exports
export VAULT_FORMAT="json"

# create an approle thats bound to your cidr blocks
 vault write auth/approle/role/usermaint \
    secret_id_ttl=10m \
    token_num_uses=10 \
    token_ttl=20m \
    token_max_ttl=30m \
    secret_id_num_uses=40 \
    secret_id_bound_cidrs="192.168.1.0/24"

# a policy must exist to allow the role to access the secret
echo 'path "secret/test" { capabilities = ["list"]}' >  usermaint.hcl
echo 'path "secret/test" {   capabilities = ["read"] }' >> usermaint.hcl
vault policy write usermaint usermaint.hcl
vault write auth/approle/role/usermaint policies=usermaint

# a token must exist for the server to initially authenticate. 
# This needs a policy which grants access the approle 
# in a corporate environment this step would be done with LDAP or AD authentication

echo 'path "auth/approle/role" { capabilities = ["list"]}' >  server1.hcl
echo 'path "auth/approle/role/usermaint/*" {   capabilities = ["read", "update"] }' >> server1.hcl
vault policy write server1 server1.hcl
servertoken=$(vault token create -policy=server1 -format=json | jq -r .auth.client_token)


# now  on the target server we can use this unprivileged token to retrieve a more privileged one
export VAULT_TOKEN=$servertoken
# get the role ID - this could be statically stored, its not considered Secret
vault_role_id=$(vault read -format=json auth/approle/role/usermaint/role-id | jq -r .data.role_id)

# then either get a wrapped token and unwrap it to get a secret
# this is more secure because the wrapped token is single-use and expires after 120s
wraptoken=$(vault write -format=json -wrap-ttl=120s -f auth/approle/role/usermaint/secret-id | jq -r .wrap_info.token)
vault_secret_id=$(vault unwrap -format=json $wraptoken | jq -r .data.secret_id)

# or just straight up get the secret. 
vault_secret_id=$(vault write -format=json -force auth/approle/role/usermaint/secret-id | jq -r .data.secret_id)

# then login to get a token with permission to read the actual secret
vault_token=$(vault write -format=json auth/approle/login role_id=$vault_role_id secret_id=$vault_secret_id | jq -r .auth.client_token)

# now you can use vault_token in subsequent calls eg
VAULT_TOKEN=$vault_token vault kv get -format=json  -mount=secret test

