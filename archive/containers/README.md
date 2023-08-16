# cronjobs

This folder contains the code that creates the docker image used in the processing pipeline. The container is loaded into Amazon ECR (Elastic Container Repository) and run using Amazon ECS (Elastic Container Service). The ECR and ECS environments are built with terraform. 

# trajsolver
This docker image runs the trajectory solver for a subset of data supplied to it via environment variables. This allows us to run multiple solvers in parallel, massively reducing runtime and cost. 

Code elsewhere in this repo executes a first-pass through the data to determine groups of potential matches. These are then divided into random groups of twenty, and one docker container started for each group. The containers solve and push the results directly to the website, as well as saving the pickled orbit back to matches/RMSCorrelate/trajectories. This avoids extra work and cost copying and storing files in two places.

# Testing
To test locally, create an IAM user with S3FullAccess. Create credentials for it and save them in awskeys.test. The keys will be embedded in the test container, which is poor security practice so you should treat this with caution.

Then  build the container in test mode: 
``` bash
./build.ps1 test
```

Then to test the container
  docker run trajsolver test/20220924_01

To build the prod container, leave off "test" from the build command. The AWS keys will not be embedded in this case.

# Copyright
All code Copyright (C) 2018-2023 Mark McIntyre