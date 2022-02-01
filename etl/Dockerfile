FROM python:3.9.6-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

#Рабочая dir
ENV HOME=/home/postgres_to_es/
ENV APP_HOME=/home/postgres_to_es/
WORKDIR $APP_HOME

COPY . .

CMD ["python"  , "main.py"]