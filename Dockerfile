FROM python:3.8-alpine

LABEL org.opencontainers.image.authors="Didier Schmitt <dschmitt@equancy.com>"

ENV CATALOG_WORKERS=1

COPY gunicorn.conf.py /etc/datacatalog/conf.py

COPY ./dist /usr/src

RUN pip install \
        /usr/src/*.whl \
        psycopg2-binary \
        pymysql \
    && rm -rf /usr/src/*

WORKDIR /usr/src

CMD ["gunicorn", "--config=/etc/datacatalog/conf.py", "datalake_catalog.main:app"]
