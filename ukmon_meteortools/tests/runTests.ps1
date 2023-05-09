#!/bin/bash

$env:PYTHONPATH="$env:WMPL_LOC;$env:RMS_LOC;.;.."
Push-Location "$PSScriptRoot/.."

if ($args.count -eq 0 ) {
    pytest -v ./tests --cov=. --cov-report=term-missing
}else{
    $targ=$args[0]
    pytest -v ./tests/test_$targ.py --cov=$targ --cov-report=term-missing
}
Pop-Location