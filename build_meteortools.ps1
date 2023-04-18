# update the version number

remove-item dist/*

bumpver update --patch

# build the package
python -m build

if ($LASTEXITCODE -eq 0 ) {
    # upload the package to test-pypi
    python -m twine upload --repository pypitest dist/*
}
