# UKmon-shared
UKMon Shared code and libraries
===============================

analysis
--------
Some powershell scripts to analyse data with RMS or WMPL, and solve orbits after converting to RMS format. 

archive
-------
The code for archive.ukmeteornetwork.co.uk, including the data processing pipeline.

DailyChecks
-----------
Scripts to run on a PC to manage the RMS and UFO data, perform daily checks etc. This makes use of
python from the pylib folder to curate and process data. 

docs
----
Incomplete documentation - to be filled out!

live
----
Code relating to handling of the ukmon-live feed. Curatio, indexing and retrieval of logs for
cost and other analysis. 

ukmon_pylib
-----------
A python module containing functionality used across the website and other analytics. 

The end-user library can be installed from Pypi. On Windows you will first need to install Shapely using conda. On Linux you should be able to simply install it with pip. 
'''
conda activate myenv
conda install -c conda-forge Cartopy Shapely
pip install ukmon_pylib
'''




