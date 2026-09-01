# UK Meteor Data Analysis Shared code and libraries
version: 2026.05.4

This repository contains the code behind the UK Meteors data archive and data processing pipeline. 

## ARCHIVE folder
The code for archive.ukmeteors.co.uk, including the data processing pipeline.

### Software Deployment
The software is a mix of Python and Bash shell scripts. Deployment is via an install script. 

#### Scripts and Python
The shell scripts and python code are deployed with `install_or_update.sh`. First, clone the repository onto the target server then run `install_or_update.sh` with an argument "PROD"  to create/update a production environment, or "DEV"  for a development environment. . 

#### Configuration Files
Parameters are created with Terraform and stored in the AWS Systems Manager Parameter Store. 
The configuration is then deployed with `utils/makeConfig.sh` which runs a script to create the `config.ini` file. 

#### Website 
Much of the website is dynamically created by the Python and Bash scripts or by AWS Lambda functions. 

There is some static content (mostly css and js files) that is pushed to the batch server along with the python
and shell scripts, and then deployed to the webserver by running `website/pushStatic.sh env` where as before, "env" is either "prod" or "dev". 

### Infrastructure Deployment
Done with Terraform - see the Terraform folder readme for details. 

## TESTS folder
This folder contains tests for the APIs and some of the Python code. Further tests are being developed and will be added to this folder. See the README in the folder for more details. 
