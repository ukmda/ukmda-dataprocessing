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
conda activate wmpl
pip install -r additional_requirements.txt
./install_or_upgrade.sh PROD
```
* double check that all required SSM variables exist in the account holding the server. These
are used to build the config file and are deployed via terraform so should be present!  For example:
``` bash
aws ssm get-parameters --region eu-west-2 --names prod_siteurl --query Parameters[0].Value
"https://archive.ukmeteors.co.uk"
```

## data
Replicate `~/prod/data` to the new server.  (once for prod and once for dev). This will have to be repeated every day till golive. 
``` bash
cd $DATADIR
rsync -avz ukmonhelper2:prod/data/ .
```
Replicate the contents of `~/keymgmt` to the new server. Repeat if any new cameras added before golive. 
``` bash
rsync -avz ukmonhelper2:keymgmt/ ./keymgmt
```

## Mariadb database
TBC

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
The basic process is to extract the user accounts from the current server along with
group and password info, then import it back in on the new server. Its important to avoid 
accidentally overwriting system or otherwise-existing accounts on the new server. 

On most systems, accounts below 500 are system accounts. Check though, as some AWS servers create
new accounts starting at 1000 and working both upwards and downwards! 

Steps in brief. NB must all be done as root, of course. 

### On the old server
``` bash
mkdir /root/move/
export UGIDLIMIT=500
awk -v LIMIT=$UGIDLIMIT -F: '($3>=LIMIT) && ($3!=65534)' /etc/passwd > /root/move/passwd.mig
awk -v LIMIT=$UGIDLIMIT -F: '($3>=LIMIT) && ($3!=65534)' /etc/group > /root/move/group.mig
awk -v LIMIT=$UGIDLIMIT -F: '($3>=LIMIT) && ($3!=65534) {print $1}' /etc/passwd | tee - |egrep -f - /etc/shadow > /root/move/shadow.mig
cp /etc/gshadow /root/move/gshadow.mig

# Also backup the user homedirs. In our case, they're all in /var/sftp
tar cvfz /root/move/varsftp.tar.gz /var/sftp
# now copy the files to target server, 
scp /root/move/* newserver:/tmp

```

### On the new server
In summary: backup the existing files, remove any accounts from the .mig files 
that are already present in the target, then append the filtered data. 

When comparing groups, remember new ids will get added to the sftp group. 


``` bash
mkdir -p /root/move/bkp
mv /tmp/*.mig /tmp/varsftp.tar.gz /root/move
cp /etc/passwd /etc/group /etc/shadow /etc/gshadow /root/move/bkp

cd /
tar -xvf /root/move/varsftp.tar.gz .

export UGIDLIMIT=500
awk -v LIMIT=$UGIDLIMIT -F: '($3>=LIMIT) && ($3!=65534)' /etc/passwd > /root/move/passwd.orig
awk -v LIMIT=$UGIDLIMIT -F: '($3>=LIMIT) && ($3!=65534)' /etc/group > /root/move/group.orig
awk -v LIMIT=$UGIDLIMIT -F: '($3>=LIMIT) && ($3!=65534) {print $1}' /etc/passwd | tee - |egrep -f - /etc/shadow > /root/move/shadow.orig

cd /root/move
diff passwd.orig passwd.mig
diff shadow.orig shadow.mig
diff group.orig group.mig
```

