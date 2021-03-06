FROM	python:3

ENV	PYTHONUNBUFFERED 0

RUN	apt-get update && apt-get -y install libpq-dev

WORKDIR /app

ADD    https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /
RUN    chmod +x /wait-for-it.sh

ADD    ./requirements.txt   /app/
RUN    pip install -r requirements.txt
