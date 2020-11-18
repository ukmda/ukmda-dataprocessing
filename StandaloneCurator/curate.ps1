# Powershell script to curate large amounts of data

Set-Location $PSScriptRoot
if ($args.count -lt 1 ){
    Write-Output "usage 1: .\curate.ps1 /path/to/files"
    Write-Output ""
    Write-Output "eg .\curate.ps1 c:\ufodata\2020"
    Write-Output "will curate all UFO files under c:\ufodata\2020"
    exit
}
if ( !(test-path ".installed"))
{
    pip install -r requirements.txt
    Write-Output '1' > .installed
}
if ( !(test-path "logs")) {mkdir logs}

$logf='./logs/curate-'+(get-date -uformat '%Y%m%d_%H%M%S')+'.log'
python ./CurateUFO.py ./curation.ini $args[0] | tee-object $logf
