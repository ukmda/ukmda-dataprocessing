# simple script to copy then display the most recent CMN/RMS meteor captures
# if RMS is installed it will also run some postprocessing to generate
# shower maps, JPGs and a UFO-Orbit-compatible detection file

# read the inifile
set-location $PSScriptRoot
$ini=get-content camera1.ini -raw | convertfrom-stringdata

# copy the latest data from the Pi
$srcpath='\\'+$ini.piname+'\RMS_share\ArchivedFiles'
$destpath=$ini.localfolder+'\ArchivedFiles'
$age=[int]$ini.maxage
robocopy $srcpath $destpath /dcopy:DAT /tee /v /s /r:3 /maxage:$age

# find the latest set of data on the local drive
$path=(get-childitem $destpath -directory | sort-object creationtime | select-object -last 1).name
$myf = $destpath + '\'+$path

# Use the Python version of binviewer, or the compiled binary?
if ($ini.USE_EXE = 1){
    set-location $ini.binviewer_exe_loc
    & .\CMN_binviewer.exe $myf | out-null
}
else {
    conda activate $ini.binviewer_env
    set-location $ini.cmn_binviewer_pyt_loc
    python CMN_BinViewer.py $myf
}
# switch RMS environment to do some post processing
if ($ini.RMS_INSTALLED=1){
    # reprocess the ConfirmedFiles folder to generate JPGs, shower maps, etc
    conda activate $ini.RMS
    set-location $ini.RMS_LOC
    $destpath=$ini.localfolder+'\ConfirmedFiles'
    $mindt = (get-date).AddDays(-$age)
    $dlist = (Get-ChildItem  -directory $destpath | Where-Object { $_.creationtime -gt $mindt }).name
    foreach ($path in $dlist) {
        $myf = $destpath + '\'+$path
        $ftpfil=$myf+'\FTPdetectinfo_'+$path+'.txt'
        $platepar=$myf+ '\platepar_cmn2010.cal'

        $ufo=$myf+'\*.csv'
        $isdone=(get-childitem $ufo).Name
        $ftpexists=test-path $ftpfil
        if ($isdone.count -eq 0 -and $ftpexists -ne 0){
            # generate the UFO-compatible CSV, shower association map 
            # convert fits to jpeg and create a stack
            python -m Utils.RMS2UFO $ftpfil $platepar
            python -m Utils.ShowerAssociation $ftpfil -x
            python -m Utils.BatchFFtoImage $myf jpg
            #stack them if more than one to stack
            $fits = $myf  + '\FF*.fits'
            $nfits=(get-childitem $fits).count
            if ($nfits -gt 1)
            {
                python -m Utils.StackFFs $myf jpg -s -b -x   
            }
            # mp4 generation is not yet in the main RMS codebase
            $mp4gen=$ini.rms_loc+'\Utils\GenerateMP4s.py'
            if ((get-childitem $mp4gen).count -gt 0 ){
                python -m Utils.GenerateMP4s $myf
            }
        }
        else{
            write-output skipping' '$myf
        }
    }    
}
set-location $PSScriptRoot
.\reorgByYMD.ps1
.\UploadToUkMon.ps1
#pause
