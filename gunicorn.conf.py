import multiprocessing
import os
import sys

bind = os.getenv("CATALOG_LISTEN", "0.0.0.0:8080")
workers = os.getenv("CATALOG_WORKERS", multiprocessing.cpu_count() * 2 + 1)

accesslog = "-"
errorlog = "-"
captureoutput = True