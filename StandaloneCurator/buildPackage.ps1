# powershell script to package the curator for non-windows

Remove-Item .\ufoCurator.zip
xcopy /dy ..\newanalysis\CameraCurator\*.py CameraCurator
xcopy /dy ..\newanalysis\UFOHandler\*.py UFOHandler
xcopy /dy ..\newanalysis\curateUFO.py .

compress-archive -path .\curate.sh -destinationpath .\ufoCurator.zip -update
compress-archive -path .\curate.ps1 -destinationpath .\ufoCurator.zip -update
compress-archive -path .\curateUFO.py -destinationpath .\ufoCurator.zip -update
compress-archive -path .\curation.ini -destinationpath .\ufoCurator.zip -update
compress-archive -path .\requirements.txt -destinationpath .\ufoCurator.zip -update
compress-archive -path .\INSTALL_WINDOWS.txt -destinationpath .\ufoCurator.zip -update
compress-archive -path .\INSTALL_LINUX.txt -destinationpath .\ufoCurator.zip -update
compress-archive -path .\USAGE.txt -destinationpath .\ufoCurator.zip -update

if ( (test-path ".\UFOHandler\__pycache__")) { Remove-Item .\UFOHandler\__pycache__ -recurse}
if ( (test-path ".\CameraCurator\__pycache__")) {Remove-Item .\CameraCurator\__pycache__ -recurse }

compress-archive -path .\UFOHandler -destinationpath .\ufoCurator.zip -update
compress-archive -path .\CameraCurator -destinationpath .\ufoCurator.zip -update
