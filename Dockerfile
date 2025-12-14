FROM python:3.11-slim

WORKDIR /app

COPY ssrf_lib.py /app/
COPY app1.py app2.py app3.py metadata_server.py /app/

RUN pip install flask requests pillow

ENV PYTHONUNBUFFERED=1
