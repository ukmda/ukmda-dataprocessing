# A Fireball Collector and Analyser for UKMON and GMN

This tool allows authorised users to collect fireball data from UKMON and GMN and then to reduce and solve it. 

## Prerequisites
  
* You have installed [WMPL](https://github.com/wmpg/WesternMeteorPyLib/), used to solve trajectories. 
* You have installed [RMS](https://github.com/CroatianMeteorNetwork/RMS), used to reduce raw data.
* You have a local folder where you will store fireball data. This is called `basedir` in this documentation. 

The above are sufficient to collect data from UKMON and to analyse data either collected from UKMON or by other means.  There are additional configuration options that can be used to collect data from GMN and upload solutions to UKMON. These are described inline below. 

## Installation
* Install the package `setup_fireballCollector.exe` from [here](https://github.com/ukmda/ukmda-dataprocessing/releases).
* Install WMPL and RMS and verify they're working. 

## Configuring the App
* Launch the app from the desktop icon or start menu. After a few seconds a text editor will appear to allow you to configure the application.
* Update the values of `basedir`, `rms_loc`, `rms_env`, `wmpl_loc`, and `wmpl_env` as appropriate and save. 

## Using the App
* Enter a date and time in the format `YYYYMMDD_HHMMSS` into the `Image Selection` box, then click "Get Images". 
  * After a few seconds, the listbox below should be populated with images from around the time you selected, provided the UKMON live feed captured something. 
  * If nothing appears, check the UKMON [livestream](https://archive.ukmeteors.co.uk/live/index.html) to make sure you chose a suitable time. 
  
* Go through the image list and click `Remove` or press the `Delete` key to delete any that are not of the event you are interested in. 
* Once you've whittled the list down to just the interesting events, you can select `Get ECSVs` from the `Raw` menu. This will attempt to get raw data for each image. You can also click `Get Videos` to collect any video data thats available. 

* Now you can click `Solve` from the `Solve` menu. This will invoke WMPL and will attempt to find a trajectory that matches the raw data. It may take some time. 
* If the solver is successful, you can view the solution by selecting `View Solution` from the `Solve` menu. The left-hand list will now show the output of the solver so you can examine it. You can switch back to viewing the raw images by selecting `Review Images` from the `Review` menu. 

* If the solve process fails or if the solution seems very poor then try excluding some detections. To do this, select `Excl/Incl ECSV` from the `Raw` menu then rerun the Solver. 
* If the solution was bad its also worth deleting it before attempting a rerun via `Delete Solution` from the `Solve` menu.

## Manually Reducing an Image
If you've installed RMS and you have a FITS or FR file from RMS along with the camera's config and platepar files, you can reduce the data using RMS's `SkyFit2` tool. Select an image in the file list then select `Reduce Selected Image` from the `Raw` menu. 

## Sending Solutions to UKMON
Once you have a solution, select `Upload orbit` from the `Solve` menu. This will create a Zip file that bundles the created trajectory pickle file with any images and videos.  You can then upload the file to Dropbox, Google Drive or another file-sharing site and email a link to [us](fireballdata@ukmeteornetwork.org) where one of our team will check and upload it to our Archive. 

#### API Key
Members of the UKMON team who frequently create solutions can request an API key to directly upload solutions less than 10 MB in size. We'll contact you if we think this is applicable. 

## Sharing Raw Data
If you've configured a raw data location in the configuration file,  `Share Raw Data` on the raw menu will create a zip file of all the raw data and copy it to the location. For example, if you have Dropbox installed and set the share location to a folder in your Dropbox, then the zip file will be copied there.

### Collecting data from GMN
Members of the GMN Coordinators group who have permission from Denis Vida can use this tool to collect raw data directly from GMN. 

If you fall into this category you can fill in the `[gmn]` section of the config file with the name of your SSH private key and other details.  This will activate additional menu options to `Get GMN Raw Data` and to use the `Watchlist`. 

*Note that you will need WSL2 enabled and the rsync tool installed in WSL2 to run this process.* 

## Logs
You can view the logs from the `File` menu. The logs are created in [%TEMP%/fbcollector](%temp%/fbcollector). 


