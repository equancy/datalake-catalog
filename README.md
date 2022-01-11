# Datalake Catalog

Configure the parameters with a [python file](https://flask.palletsprojects.com/en/2.0.x/config/#configuring-from-python-files) 

For example, `catalog.conf.py`

```python
SECRET_KEY = b"changemenow"
DB_STRING = "sqlite://localhost/catalog.sqlite"
```

Start the catalog 

```shell
docker run -d \
    -p '8080:8080' \
    -v 'catalog.conf.py:/etc/datacatalog/catalog.conf.py' \
    -e 'CATALOG_SETTINGS=/etc/datacatalog/catalog.conf.py' \
    public.ecr.aws/equancy-tech/datalake-catalog
```
