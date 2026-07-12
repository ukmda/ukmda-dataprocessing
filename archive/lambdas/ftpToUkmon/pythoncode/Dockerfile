FROM public.ecr.aws/lambda/python:3.14

COPY requirements.txt ./
RUN python -m pip install -r requirements.txt -t .
ENV LD_LIBRARY_PATH ./
COPY *.py ./
COPY *.csv ./

CMD ["ftpToUkmon.lambda_handler"]
