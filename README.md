# UKMon Shared code and libraries


## archive
The code for archive.ukmeteors.co.uk, including the data processing pipeline.

### Software Deployment
All software deployment uses Ansible. 
The shell scripts and python code are deployed with deploy-analysis.yml. Use the "prod" tag to push to production, and the "dev" tag to push to a development environment. Deployments target the batch server in the MM account. 

```bash
ansible-playbook deploy-analysis.yml -t prod
```

The configuration is deployed with deploy-config.yml. Parameters are created with Terraform and stored in the AWS Systems Manager Parameter store. 

The website static is deployed with deploy-static.yml. The target bucket must have ACLs enabled while deploying. This is a limitation of ansible's S3sync module.

### Infrastructure Deployment
Done with Terraform - see the Terraform folder readme for details. 

## live
Code relating to handling of the ukmon-live feed.I have no idea how this works, i just dumped the lambda
from AWS and stored the code. Apparently the developer left no notes. 

## tests

some test scripts - only partial coverage of just the python codebase. 

## usermgmt
a python app that is used to add/modify contributors' camera details and grant them permission to upload.
Relies on SSH access to the batch server. 



