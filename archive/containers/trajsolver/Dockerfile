FROM public.ecr.aws/lambda/python:3.8
RUN yum -y update
RUN pip install --upgrade pip
COPY requirements.txt ./
RUN python3.8 -m pip install -r requirements.txt -t .
ENV LD_LIBRARY_PATH ./:

COPY WesternMeteorPyLib/ ./WesternMeteorPyLib
ENV PYTHONPATH ./WesternMeteorPyLib
ENV PROJ_LIB ./
RUN pip install boto3
COPY *.py ./

# uncomment this to test the container locally eg with "docker run -t trajsolver 20220924_01"
# where 20220924_01 is a folder in s3://ukmon-shared/matches/distrib containing pairing pickles 

#COPY awskeys ./

ENTRYPOINT ["python", "trajsolver.py"]
