FROM python:latest

RUN pip install -r req.txt

COPY *.py .