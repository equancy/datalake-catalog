## Live development setup

```shell
poetry install

export FLASK_APP=datalake_catalog/main
export FLASK_ENV=development

poetry run flask run
```

## Run unit test

First start database backends

```shell
docker-compose up -d -f "tests/docker-compose.yaml"
```

Then run the test suite

```shell
poetry install
poetry run coverage run -m pytest && poetry run coverage report -m
```

> If Database backends cannot be launched, tests can be run without them by adding the following marker to pytest `-m "not backends"`
