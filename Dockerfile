FROM python:3.8-alpine

LABEL MAINTAINER="Didier Schmitt <dschmitt@equancy.com>"

COPY gunicorn.conf.py /etc/datacatalog/conf.py

COPY ./dist /usr/src

RUN pip install /usr/src/*.whl \
    && rm -rf /usr/src/*

WORKDIR /usr/src

CMD ["gunicorn", "--config=/etc/datacatalog/conf.py", "datalake_catalog.main:app"]
