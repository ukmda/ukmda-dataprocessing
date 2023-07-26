# cronjobs

This folder contains the code that creates the docker images used by containers in various parts of the processing pipeline. The containers are loaded into Amazon ECR (Elastic Container Repository) and run using Amazon ECS (Elastic Container Service). The ECR and ECS environments are built with terraform. 

# trajsolver
This docker image runs the trajectory solver for a subset of data supplied to it via environment variables. This allows us to run multiple solvers in parallel, massively reducing runtime and cost. 

to build the container in test mode, do 
``` bash
./build.ps1 test
```

Then to test the container
  docker run trajsolvertest test/20220924_01

To build the prod container, leave off "test" from the build command. 

# Copyright
All code Copyright (C) 2018-2023 Mark McIntyre