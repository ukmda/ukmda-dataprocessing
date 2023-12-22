# README for containers used by the data processing pipeline

## TRAJSOLVER container
This container runs the trajectory solver for a subset of data supplied to it via environment variables. This allows us to run multiple solvers in parallel, massively reducing runtime and cost. 

Code elsewhere in this repo executes a first-pass through the data to determine groups of potential matches. These are then divided into random groups of twenty, and one docker container is started for each group. The containers solve and push the results directly to the website, as well as saving the pickled orbit back to matches/RMSCorrelate/trajectories. This avoids extra work and cost copying and storing files in two places.

The build script build.ps1 will build the container and push it to AWS ECR, optionally updating WMPL if needed. 

### Testing Locally
To test locally, you'll need credentials for an AWS IAM user with S3FullAccess. Save them in `trajsolver/awskeys.test` and rebuild the container in test mode. Note that the keys will be embedded in the test container which is terrible security practice so you should never push this container to a remote repository (AWS will actually invalidate your keys if you do).

To build and test the container in test mode: 
``` bash
./build.ps1 test
docker run trajsolver test/20220924_01
```

## TESTING container
This container is used to test the python code in this repository using GitHub Actions. The action itself is in `.github/workflows` in the root of the repository, and is launched automatically when code is checked into github. 

The container includes copies of RMS, WMPL, MeteorTools and the other python libraries required to run the tests. If any changes are made to the requirements, these must be added to `testing/requirements.txt`, and the container rebuilt with 
```bash
docker build -t ukmdatester .
docker tag ukmdatester:latest markmac99/ukmdatester:latest
docker push markmac99/ukmdatester:latest
```
(TODO: move this container to the GH ukmda-dataprocessing registry)

### Using the container
The GitHub action is launched automatically when you check code into the dev branch. If you'd like to run it on your own branch, add the branch name to the list of branches mentioned in `.github/workflows/automated-testing.yml`:
```yaml
on:
  push:
    branches: [ dev, markmac99 ]
```

You can also run the docker container locally by passing the branch name and AWS keys as as environment variables:
```bash
docker run -e BRANCH=dev -e AWS_ACCESS_KEY_ID=... -e AWS_SECRET_ACCESS_KEY=... -t markmac99/ukmdatester:latest
```

### Adding new Tests
Create a pytest-compatible python script and add it to `archive/ukmon_pylib/tests`. 

If any new data is required you must download the test dataset and add the new data, then upload it back to the server. You'll need AWS access for the latter step, so contact me for further advice. To obtain the test dataset, run the following:

```bash
curl https://archive.ukmeteors.co.uk/browse/testdata/testdata.tar.gz  -o ./testdata.tar.gz
tar -xvf ./testdata.tar.gz
```
(these instructions assume you're using Linux or WSL2).

# Copyright
All code Copyright (C) 2018-2023 Mark McIntyre