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
This container is used to test the python and other code in this repository using GitHub Actions. The action itself is in `.github/workflows` in the root of the repository, and is launched automatically when code is checked into github. 

The container includes copies of RMS, WMPL, MeteorTools and the other python libraries required to run the tests. If any changes are made to the requirements, these must be added to `testing/requirements.txt`, and the container rebuilt with 
```bash
docker build -t ukmdatester .
docker tag ukmdatester:latest markmac99/ukmdatester:latest
docker push markmac99/ukmdatester:latest
```
(TODO: move this container to the GH ukmda-dataprocessing registry)

To add new tests, create pytest-compatible python scripts and add them to `archive/ukmon_pylib/tests`, including any necessary data in the `data` folder following the general pattern used by the existing tests. The tests will then be automatically executed whenever the code is pushed to GitHub and you'll be able to see the results in GitHub under Actions. Alternatively if you're using Visual Code you can install the Github Actions plugin which makes results visible in the VSCode GUI. 

# Copyright
All code Copyright (C) 2018-2023 Mark McIntyre