#!/bin/bash

docker login
docker build -t ukmdatester .
if [ $? -eq 0 ] ; then 
	docker tag ukmdatester:latest markmac99/ukmdatester:latest
	docker push markmac99/ukmdatester:latest
fi
