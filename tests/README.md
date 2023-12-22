# README for Tests 

## APIs
These two scripts are used to test the APIs. They're triggered from a GitHub action `.github/workflows/automated-testing.yml` whenever code is checked in. 

## TESTING container
This container is used to test the other python code in this repository. Its also triggered from a GitHub action in `.github/workflows/automated-testing.yml` and is launched automatically when code is checked in. 

The container includes copies of RMS, WMPL, MeteorTools and the other python libraries required to run the tests. If any changes are made to RMS, WMPL or the requirements then the container must be rebuilt with 
```bash
docker build -t ukmdatester .
docker tag ukmdatester:latest markmac99/ukmdatester:latest
docker push markmac99/ukmdatester:latest
```
(TODO: move this container to the GH ukmda-dataprocessing registry)

### Using the container
The GitHub action is launched automatically when you check code into the dev branch. If you'd like to run it on your own branch, then please contact me so i can configure access.

You can also run the docker container locally by passing the branch name and your AWS keys as as environment variables:
```bash
docker run -e BRANCH=dev -e AWS_ACCESS_KEY_ID=... -e AWS_SECRET_ACCESS_KEY=... -t markmac99/ukmdatester:latest
```

### Adding new Tests
Create a pytest-compatible python script and add it to `archive/ukmon_pylib/tests`. 

### Test Data
The container loads a test dataset that is kept on our website.  If any new data is required you must download the test dataset and add the new data, then upload it back to the server. You'll need AWS access for the latter step, so contact me for further advice. 

To obtain the test dataset, run the following:
```bash
curl https://archive.ukmeteors.co.uk/browse/testdata/testdata.tar.gz  -o ./testdata.tar.gz
tar -xvf ./testdata.tar.gz
```
(these instructions assume you're using Linux or WSL2).
