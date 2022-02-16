FROM python:3.9-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

ENV HOME=/tests/functional
ENV APP_HOME=/tests/functional
WORKDIR $APP_HOME

COPY . .
