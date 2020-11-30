If ([Environment]::OSVersion.Platform -eq "Unix") {
    $ModulePath = [Environment]::GetEnvironmentVariable("PSModulePath").split(":")[0]
    If (Test-Path "$ModulePath/PowerShell-SMS.zip"){Remove-Item "$ModulePath/PowerShell-SMS.zip"}
    If (Test-Path "$ModulePath/PowerShell-SMS"){Remove-Item "$ModulePath/PowerShell-SMS" -Confirm:$false -Recurse -Force}
    Invoke-WebRequest https://github.com/bmsimons/PowerShell-SMS/zipball/master -OutFile "$ModulePath/PowerShell-SMS.zip"
    Expand-Archive "$ModulePath/PowerShell-SMS.zip" -DestinationPath "$ModulePath"
    Remove-Item "$ModulePath/PowerShell-SMS.zip"
    Get-ChildItem "$ModulePath" | where { $_.Name -like "bmsimons-PowerShell-SMS*" } | % { Move-Item -Path ("$ModulePath/"+$_.Name) -Destination "$ModulePath/PowerShell-SMS" }
} Else {
    $ModulePath = [Environment]::GetEnvironmentVariable("PSModulePath").split(";")[0]
    If (Test-Path "$ModulePath\PowerShell-SMS.zip"){Remove-Item "$ModulePath\PowerShell-SMS.zip"}
    If (Test-Path "$ModulePath\PowerShell-SMS"){Remove-Item "$ModulePath\PowerShell-SMS" -Confirm:$false -Recurse -Force}
    Invoke-WebRequest https://github.com/bmsimons/PowerShell-SMS/zipball/master -OutFile "$ModulePath\PowerShell-SMS.zip"
    Expand-Archive "$ModulePath\PowerShell-SMS.zip" -DestinationPath "$ModulePath"
    Remove-Item "$ModulePath/PowerShell-SMS.zip"
    Get-ChildItem "$ModulePath" | where { $_.Name -like "bmsimons-PowerShell-SMS*" } | % { Move-Item -Path ("$ModulePath\"+$_.Name) -Destination "$ModulePath\PowerShell-SMS" }
}