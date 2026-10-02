# Building a new Calcserver

## Create a new AWS asset
* The server is built form Terraform, so clone `calcserver.tf` in the `terraform` folder. 
* Update the server AMI, instance type, name etc as desired
* Run `terraform plan` and then `terraform apply`

## Install some prerequisites
* Login to the new server and install Miniconda using the defaults
* Install the AWS CLI and run `aws configure`.
* Deploy bashrc, bash_aliases and vimrc from `server_setup/calcserver/` to the calcserver user's homedir
* Log out and log in again. Ignore any conda-related and python errors for now. 

## Create required folder structure
Run the following
``` bash
mkdir -p ~/ukmon-shared/matches/RMSCorrelate/
mkdir -p ~/data/distrib/canddbs/
mkdir -p ~/src/
mkdir -p ~/runtime/scripts/
```

## Install WMPL from my Repo
Important note: do *NOT* run setup.py as instructed in the WMPL readme. This is not necessary and will in fact break WMPL on modern python builds. Instead, after installation,  remove the `wmpl/CAM0 `and `wmpl/MetSim` folders, these are not used and rely on unavailable libraries, delete `wmpl/Utils/DynamicMassFit.py` as this makes a callback to `MetSim`, then copy over the static data files from the old server. 
you can also make a conda environment as per the WMPL readme, though this is only used for debugging purposes. 

``` bash
cd ~/src
git clone --recursive https://github.com/markmac99/WesternMeteorPyLib.git
rm -Rf WesternMeteorPyLib/wmpl/MetSim
rm -Rf WesternMeteorPyLib/wmpl/CAM0
rm -Rf WesternMeteorPyLib/wmpl/Utils/DynamicMassFit.py
```

## Create a Python virtualenv
Now create a python virtualenv, activate it and install the requirements:
``` bash
python -m venv ~/venvs/wmpl
source /home/ubuntu/venvs/wmpl/bin/activate
pip install -r ~/src/WesternMeteorPyLib/requirements.txt
pip install scp pymysql
```
## Copy the data files from the old server.
Copy the contents of `~/src/WesternMeteorPyLib/wmpl/share/` from the old server to the same location on the new server.

## Test the installation
Logout and back in then run 
``` bash
python -c "from wmpl.Utils.TrajConversions import jd2Date;print(jd2Date(2461180.5))"
```
this should print `(2026, 5, 20, 0, 0, 0, 0.0)`

## Cutting Over
When you're ready to cut over:
* update the terraform file `ssm_variables.tf` to reflect the new values of calcinstance, calcuser and calcserverip. 
* These variables are used at runtime by the batch to start, stop and connect with the calc engine. 
* Redeploy the terraform with `terraform plan` and `terraform apply`
* On the production batch server, run `$SRC/utils/makeConfig.sh`  to update the configuration file. 
