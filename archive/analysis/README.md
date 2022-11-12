# analysis

This folder contains the batch scripts that perform various analyses of the data. They're mostly triggere
from the nightly batch but can also be triggered manually as needed. 

## consolidateOutput
Collects all single station and match data and consolidates it into two files in parquet format. These are used for all detailed analysis.

## convertUfoToRms
Convert a folder of UFO data into RMS-compatible format

## createDensityPlots
(unused)

## createSearchable
Creates a single file for the search engine, by consolidating the required information from the match and single station data. 

## findAllMatches
The heart of the matching engine. Reads in all single station for the date ranged provided (default three days) and runs the distributed matching engine process. 

## getBadStations
Checks for stations that failed quality tests such as too many detections, not uploaded for a few days etc. 

## getLogData
Scans the logs to create a simplified version for publication on the website. 

## getRMSSingleData
Creates a UFO-analyser compatible version of the RMS single-station detections. 

## reportActiveShowers
Creates a shower report for any active showers, by calling showerReport for each active shower year-to-date. 

## runDistrib
Called by findAllMatches to execute the distributed processing engine. 

## showerReport
Creates a report for one or more showers. 

## stationReports
Creates a report of data for one or all stations, for a month or year to date, which is then pushed to the website. 