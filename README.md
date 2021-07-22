# UKmon-shared
UKMon Shared code and libraries
===============================

analysis
--------
Some python scripts to analyse UFO data with RMS or WMPL, curate UFO data and solve orbits
after converting to RMS format. These will be merged into the ukmon_pylib module at some point. 

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

UKmonCPPTools
-------------
The live uploader, archiver and other tools for Windows written in C++ 
These require the AWS API for C++ and Visual Studio 2019. This code is legacy. 


