# update the version number

remove-item dist/*

bumpver update --patch

# build the package
python -m build

if ($LASTEXITCODE -eq 0 ) {
    $prod = read-host -prompt "(T)est or (P)rod?"
    if ( $prod.ToUpper() -eq "P") {$repo = "pypi"} else {$repo = "pypitest"}
    python -m twine upload --repository $repo dist/*.gz
}
