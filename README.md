## Setup and start the API 

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

## Generate an API token

The `catalog create-api-key` generated tokens that can be used with restricted endpoint.

- **admin** role can access all restricted endpoints
- **author** role can only access the restricted endpoints in `/catalog`

```shell
Usage: catalog create-api-key [OPTIONS] NAME

Options:
  -e, --expires INTEGER      number of days before token expires
  -r, --role [author|admin]  the role associated with the name
  --help                     Show this message and exit.
```

## Update the storages configuration

Storage configures aliases to help resolve actual buckets (S3, Azure, local fs, etc.).
It consists of a bucket name and an optional prefix.

For example:

```json
{
    "landing": {
        "bucket": "my-raw-bucket",
        "prefix": "landing"
    },
    "archive": {
        "bucket": "my-raw-bucket",
        "prefix": "archives"
    },
    "bronze": {
        "bucket": "my-bucket-bronze"
    },
    "silver": {
        "bucket": "my-bucket-silver"
    },
    "gold": {
        "bucket": "my-bucket-gold",
    }
}
```

```shell
curl -XPUT http://localhost:8080/storage \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${CATALOG_ADMIN_TOKEN}" \
    --data "@${STORAGE_CONFIG_FILE}" 
```
