FROM python:alpine

RUN apk add --no-cache git

RUN pip install git+https://github.com/gallofeliz/python-gallocloud-utils

VOLUME /backup

WORKDIR /app

ADD app.py .

CMD python -u ./app.py -
