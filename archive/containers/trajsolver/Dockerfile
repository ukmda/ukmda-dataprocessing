FROM public.ecr.aws/lambda/python:3.8
COPY requirements.txt ./
RUN yum -y update
RUN pip install --upgrade pip
RUN python3.8 -m pip install -r requirements.txt -t .
ENV LD_LIBRARY_PATH ./:

COPY WesternMeteorPyLib/ ./WesternMeteorPyLib
ENV PYTHONPATH ./WesternMeteorPyLib
ENV PROJ_LIB ./
RUN pip install boto3
COPY *.py ./

ENTRYPOINT ["python", "trajsolver.py"]
