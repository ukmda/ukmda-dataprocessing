# powershell script to run the test

$fn='C:\Users\mark\Documents\Projects\meteorhunting\UKmon-shared\NewAnalysis\test_data\platepar\M20200514_012042_TACKLEY_NE.avi'
$cf='C:\Users\mark\Documents\Projects\meteorhunting\UKmon-shared\NewAnalysis\test_data\platepar\.config_NE'

set-location C:\Users\mark\Documents\Projects\meteorhunting\RMS

python -m RMS.Astrometry.SkyFit -c $cf $fn

set-location $PSScriptRoot