FROM public.ecr.aws/lambda/python:3.8

COPY *.py requirements.txt ./
RUN python3.8 -m pip install -r requirements.txt -t .
ENV LD_LIBRARY_PATH ./
COPY WesternMeteorPyLib/ ./WesternMeteorPyLib
COPY *.npy ./WesternMeteorPyLib/wmpl/share/
ENV PYTHONPATH ./WesternMeteorPyLib
ENV PROJ_LIB ./

CMD ["getExtraFiles.lambda_handler"]
