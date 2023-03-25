# Running RMS in a Docker Container

RMS can be run in a Docker container using the scripts here. The approach i've taken is 
to build a container based on Ubuntu 20.04 (which supports RMS natively) and to attach an
external volume in the Host which is mapped to ~/RMS_data in the container.

## Configuration
The camera-specific configuration files (.config, mask.bmp, etc) are stored in a folder ./config 
on the external volume along with a configuration script *configure_container.sh*. 
The image is configured to run this script at startup. 

As currently deployed, the script copies the camera-specific configuration, SSH keys 
and other configuration data, updates the UKMON toolset, and installs some functionality specific to me. 

## RMS_data
The use of the external filesystem allows RMS to write data directly back to the Host, removing 
any need to copy or move data after each run and keeping the container size small. However, you'll 
need to implement some process on the host to purge the CapturedFiles data periodically, as RMS typically
collects 10-20GB per night. 

## Updating RMS
RMS is updated whenever the container is restarted or whenever the image is rebuilt. To force an update, 
restart the container. I am using cron to restart all the containers daily via the *runAll.sh* script

## Scripts
* build.* - builds the image. Note that you'll need Docker Desktop installed with WSL2 support enabled in order to build the container properly. 
* runAll.sh - runs multiple containers.  I run this from cron to restart everything daily. 

* run.* - run the image.
* login.* - login to the container.
* stop.* - stop the container.

The last three all require a path to be passed, specifying where to find the container configuration. For example *.\run.ps1 f:\dockervols\uk0006* will look in the specified location for the container config, and *login.ps1 f:\dockervols\uk0006* will read from this location to determine which container to connect to. 

