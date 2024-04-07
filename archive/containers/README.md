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

# Copyright
All code Copyright (C) 2018-2023 Mark McIntyre