FROM python:3.10.6

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . .

RUN rm -rf tests

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
