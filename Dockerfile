FROM python:3.10-alpine

COPY update-linear-issues.py /update-linear-issues.py

RUN pip install requests

ENTRYPOINT [ "python", "/update-linear-issues.py" ]