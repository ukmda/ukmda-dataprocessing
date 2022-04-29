# run remote container

. ~/.ssh/mark-creds.ps1 

aws ecs run-task --region eu-west-2 --cli-input-json "file://taskrunner.json"