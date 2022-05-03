import pytest
import pony.orm
from pony.flask import Pony
from datalake_catalog.app import app
import datalake_catalog.model
import importlib


@pytest.mark.backends
def test_mysql():
    importlib.reload(datalake_catalog.model)
    datalake_catalog.model.connect("mysql://api:unittest@localhost/catalog")

    importlib.reload(datalake_catalog.model)
    datalake_catalog.model.connect("mysql://api:unittest@localhost:3306/catalog")


@pytest.mark.backends
def test_postgres():
    importlib.reload(datalake_catalog.model)
    datalake_catalog.model.connect("postgresql://api:unittest@localhost/catalog")

    importlib.reload(datalake_catalog.model)
    datalake_catalog.model.connect("postgresql://api:unittest@localhost:5432/catalog")
