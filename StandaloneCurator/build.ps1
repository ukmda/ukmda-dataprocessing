conda activate RMS

xcopy /dy ..\newanalysis\cameracurator\*.py cameracurator
xcopy /dy ..\newanalysis\ufohandler\*.py ufohandler
xcopy /dy ..\newanalysis\curateUFO.py .
xcopy /dy ..\testing.ini .

pyinstaller curateUFO.py --noconfirm

