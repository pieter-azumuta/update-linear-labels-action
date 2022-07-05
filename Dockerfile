FROM python:3.10-alpine

COPY update-linear-labels.py /update-linear-labels.py

RUN pip install requests

ENTRYPOINT [ "python", "/update-linear-labels.py" ]