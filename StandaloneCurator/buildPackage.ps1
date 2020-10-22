# powershell script to package the curator for non-windows

compress-archive -path .\*.py -destinationpath .\ufoCurator.zip -update
compress-archive -path .\curation.ini -destinationpath .\ufoCurator.zip -update
compress-archive -path .\requirements.txt -destinationpath .\ufoCurator.zip -update
compress-archive -path .\INSTALL.txt -destinationpath .\ufoCurator.zip -update
compress-archive -path .\USAGE.txt -destinationpath .\ufoCurator.zip -update
compress-archive -path .\curate.sh -destinationpath .\ufoCurator.zip -update
compress-archive -path .\curate.ps1 -destinationpath .\ufoCurator.zip -update

Remove-Item .\UFOHandler\__pycache__ -recurse
Remove-Item .\CameraCurator\__pycache__ -recurse
compress-archive -path .\UFOHandler -destinationpath .\ufoCurator.zip -update
compress-archive -path .\CameraCurator -destinationpath .\ufoCurator.zip -update
