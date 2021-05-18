FROM python:3.8-alpine3.12

RUN apk add --update --no-cache --virtual .tmp git \
    && pip install git+https://github.com/gallofeliz/python-gallocloud-utils \
    && apk del .tmp

VOLUME /backup

WORKDIR /app

ADD app.py .

CMD python -u ./app.py -
