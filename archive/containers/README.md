# cronjobs

This folder contains the code that creates the docker images used by containers in various parts of the processing pipeline. The containers are loaded into Amazon ECR (Elastic Container Repository) and run using Amazon ECS (Elastic Container Service). The ECR and ECS environments are built with terraform. 

# trajsolver
This docker image runs the trajectory solver for a subset of data supplied to it via environment variables. This allows us to run multiple solvers in parallel, massively reducing runtime and cost. 

# Testing
To test locally, create an IAM user with S3FullAccess. Create credentials for it and save them in awskeys.test. The keys will be embedded in the test container, which is poor security practice so you should treat this with caution.

Then  build the container in test mode: 
``` bash
./build.ps1 test
```

Then to test the container
  docker run trajsolver test/20220924_01

To build the prod container, leave off "test" from the build command. 

# Copyright
All code Copyright (C) 2018-2023 Mark McIntyre