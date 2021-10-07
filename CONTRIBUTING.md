## Development setup

```shell
poetry install

export FLASK_APP=datalake_catalog/main
export FLASK_ENV=development
export CATALOG_SETTINGS=${PWD}/dev_settings.cfg

poetry run flask run
```