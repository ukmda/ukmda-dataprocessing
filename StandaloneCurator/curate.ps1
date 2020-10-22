# Powershell script to curate large amounts of data

if ($args.count -lt 1 ){
    Write-Output usage: .\curate.ps1 /path/to/files
    Write-Output ""
    Write-Output eg .\curate.ps1 c:/ufodata/2020
    Write-Output will curate all UFO files under c:/ufodata/2020
    exit
}

conda activate ufoCurator
pip install -r requirements.txt
python ./CurateUFO.py ./curation.ini $args[0] | tee-object./logs/curate-`date +%Y%m%m_%H%M%s`.log

