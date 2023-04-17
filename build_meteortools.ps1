# update the version number
bumpver update --patch

# build the package
python -m build

# upload the package to test-pypi
 python -m twine upload --repository pypitest dist/*

