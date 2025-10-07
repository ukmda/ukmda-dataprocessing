# A Fireball Collector and Analyser for UKMON and GMN

This tool allows authorised users to collect fireball data from UKMON and GMN and then to reduce and solve it. 

## Prerequisites
  
* [WMPL](https://github.com/wmpg/WesternMeteorPyLib/), used to solve trajectories. 
* [RMS](https://github.com/CroatianMeteorNetwork/RMS), used to reduce raw data.
* A local folder where you will store fireball data. This is called `basedir` in this documentation. 

The above are sufficient to collect data from UKMON and to analyse data either collected from UKMON or by other means.  There are additional configuration options that can be used to collect data from GMN and upload solutions to UKMON. These are described inline below. 

## Installation
* Clone this repository to a location of your choice 
* Install WMPL and RMS, and activate the WMPL python virtual environment. 
* Change directory into the location of this code then install the additional requiremnts with `pip install -r requirements.txt`
* Copy `config.ini.sample` to `config.ini` and update the values of `basedir`, `rms_loc`, `rms_env`, `wmpl_loc`, and `wmpl_env` as appropriate. 

## Using the App
* Launch the app by running `fbCollector.ps1` in a Powershell window. After a few seconds the GUI window should appear.
* In the box labelled `Image Selection` enter a date and time in the format `YYYYMMDD_HHMMSS`, then click "Get Images". 
* After a few seconds, the listbox below should be populated with images from around the time you selected, provided the UKMON live feed captured something. 
  * If nothing appears, check the UKMON [livestream](https://archive.ukmeteors.co.uk/live/index.html) to make sure you chose the correct time. 
  
* Go through the image list and click `Remove` to delete any that are not of the event you are interested in. 
* Once you've whittled the list down to just the interesting events, you can select `Get ECSVs` from the `Raw` menu. This will attempt to get raw data for each image. You can also click `Get Videos` to collect any video data thats available. 
* Now you can click `Solve` from the `Solve` menu. This will invoke WMPL and will attempt to find a trajectory that matches the raw data. It may take some time. 
* If the solver is successful, you can view the solution by selecting `View Solution` from the `Solve` menu. The left-hand list will now show the output of the solver so you can examine it. You can switch back to viewing the raw images by selecting `Review Images` from the `Review` menu. 
* If the solve process fails or if the solution seems very poor then try excluding some detections. To do this, select `Excl/Incl ECSV` from the `Raw` menu then rerun the Solver. 
* If the solution was bad its also worth deleting it before attempting a rerun via `Delete Solution` from the `Solve` menu.

## Manually Reducing an Image
If you've installed RMS then if you have a FITS or FR file from RMS along with the camera's config and platepar files, you can run RMS's `SkyFit2` tool to analyse the image - select and image then select `Reduce Selected Image` from the `Raw` menu. 

## Sending Solutions to UKMON
Once you have a solution, select `Upload orbit` from the `Solve` menu. This will create a Zip file that bundles the created trajectory pickle file with any images and videos.  You can then upload the file to Dropbox, Google Drive or another file-sharing site and email a link to fireballdata@ukmeteornetwork.org where one of our team will validate and upload it to our Archive. 

#### API Key
Members of the UKMON team who frequently create solutions can request an API key to upload solutions less than 10 MB in size. We'll contact you if we think this is applicable.

### Collecting data from GMN
Members of the GMN coordinators group who have permission from Denis Vida can use this tool to collect data directly from GMN or using the GMN Watchlist. If you fall into this category you can fill in the `[gmnanalysis]` section of the config file with the name of your SSH private key and other details.  This will activate additional menu options to `Get GMN Raw Data` and to use the `Watchlist`. 

## Logs
The programme creates logs in your system's `TEMP` folder. 


