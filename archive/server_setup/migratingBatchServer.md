# Replacing the UKMON helper server 
The ukmon helper server provides two services. 
* batch processing
* camera authentication and key management

## how to move batch processing
* Build a new Ubuntu server from the Terraform by cloning the existing batch server details in `terraform/ukmda/batchserver.tf` and making any necessary changes then deploying it with terraform in the normal way. 
* I do not recommend using Amazon Linux as this doesn't contain many of the base requirements like C++, development libraries, GEOS and PROJ, so you would need to install and/or build these from source which is tedious. 
* If you want to set the hostname to eg `batchserver1`, then do the following
  * edit `/etc/cloud/cloud.cfg` and set `preserve_hostname: true`
  * run `sudo hostnamctl hostname batchserver1`
  * now the new hostname should be preserved through boot

### Prerequisites
* install some prerequisites via apt
``` bash
sudo apt-get install unzip net-tools dos2unix mariadb-server 
```

### Miniconda
* Install miniconda with the default settings

### WMPL
* Install WMPL 
  * create a 'wmpl' conda environment with at least python 3.13
  * install the python requirements
  * See note below for how to get PyQt5 working. 
  * Alternatively you can delete subfolders of wmpl that rely on QT (`CAM0` `MetSIM` and `Utils/DynamicMassFit.py`). 
``` bash
conda create -n wmpl python=3.13
mkdir -p ~/src
cd ~/src
git clone --recursive git@github.com:markmac99/WesternMeteorPyLib.git
cd WesternMeteorPyLib
conda activate wmpl
pip install -r requirements.txt
python setup.py
```

### UKMDA Dataprocessing
* Clone the ukmda git repo and then install all the code using the deployment script. Both dev and prod envs should be created, though arguably the dev env should be on a separate server.
``` bash
cd ~/src
git clone git@github.com:ukmda/ukmda-dataprocessing.git
cd ukmda-dataprocessing
./install_or_upgrade.sh PROD
```
* double check that all required SSM variables exist in the account holding the server. These
are used to build the config file and are deployed via terraform so should be present!  For example:
``` bash
aws ssm get-parameters --region eu-west-2 --names prod_siteurl --query Parameters[0].Value
"https://archive.ukmeteors.co.uk"
```

### SSH and other API keys 
copy the below files from ~/.ssh on the old server, and make sure permissions are correct (should all be 0600). At a minimum you need the following files
``` bash
gmailcreds.json
gmailtoken.json
```
These are used to authenticate against gmail. The keys are currently specific to Mark McIntyre's account and will need to be replaced with keys for `ukmeteors@gmail.com`

You may also need the `github` keys though this depends on how you authenticate with GitHub. 

## data
Replicate `~/prod/data`, `~/prod/logs` and `~/keymgmt` to the new server.  (once for prod and once for dev).
 
 This will have to be repeated every day till golive (strictly, the key data only needs to be replicated if a new camera is added). Also keep the MariaDB SQL database up to date.
``` bash
cd $DATADIR
rsync -avz ukmonhelper2:prod/data/ .
cd $SRC/logs
rsync -avz ukmonhelper2:prod/logs/ .
cd ~
rsync -avz ukmonhelper2:keymgmt/ ./keymgmt
$SRC/utils/loadSingleCsvMDB.sh
$SRC/utils/loadMatchCsvMDB.sh

```
## Mariadb database
Sudo to root and run the following to set a root password
``` bash
mysql -u root -p
ALTER USER 'root'@'localhost' IDENTIFIED VIA mysql_native_password USING PASSWORD('ROOTPASSWORD');
FLUSH PRIVILEGES;
quit
```
Pbviously, replace `ROOTPASSWORD` with the password in the SSM variable `prod_dbpw`

Exit the root shell, and as a 'normal' user execute the following:
``` bash
cd $SRC/database/
mysql -u root -pROOTPASSWORD < ddl/create_dbs_and_users.sql
mysql -u root -pROOTPASSWORD < ddl/create_tables.sql
mysql -u root -pROOTPASSWORD < ddl/create_brightness_table.sq
```
Now dump and reload the databases from the old server.
Make sure the old server can connect to the new one then on the old server, run the following:
``` bash
mysqldump -u batch -p'passwd' ukmon | ssh newserver mysql -u batch -p'passwd' ukmon
```


### To install PyQt5 
* needs at least 3GB memory so add 2GB swap if the server has less.
``` bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

sudo apt install qtbase5-dev qt5-qmake
pip install pyqt5
```

### To get conda working in batch scripts
This is done by sourcing a file `.condaon` which is automatically installed by the ukmda deployment script and sourced from the environments' config.ini files. Make sure any scripts activate conda like this:

``` bash
source $HOME/prod/config.ini >/dev/null 2>&1
conda activate ${WMPL_ENV}
```

## how to move accounts to a new server

### Install and configure sftp
First set up the SFTP server on the new host.
Run the following as root:

``` bash
groupadd sftp
mkdir -p /var/sftp
chown root:root /var/sftp
chmod 751 /var/sftp
```

Add this to /etc/ssh/sshd_config
``` bash
Match group sftp
ChrootDirectory /var/sftp/%u
AllowTCPForwarding no
X11Forwarding no
ForceCommand internal-sftp
```

and then reload sshd 
``` bash
service sshd reload
```
### Now move the user accounts

First, ensure that root on the new server can connect to the old server as the batch user by creating a default SSH keypair for root, and adding its public half to root's authorized_keys file on the old server.

* on the new server as the standard batch user:
  * create a folder `move`
  * Create a list of the desired SFTP user accounts using 
``` bash
ssh oldserver "sudo ls -1 /var/sftp" > ./move/sftp_accts.txt
```
  * Edit the list to exclude defunct accounts and other entries not related to a camera account.
  * use `$SRC/$utils/migrateSftpAccts.sh`  to create accounts on the new server and copy over the user data
``` bash
$SRC/utils/migrateSftpAccts.sh oldserverFQDN ./move/sftp_accts.txt
```
Once you've completed the process you can remove the `move` folder. 