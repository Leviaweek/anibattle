import os

from psycopg_pool import ConnectionPool

CONNECTION_URL = os.environ["CONNECTION_URL"]

with ConnectionPool(CONNECTION_URL) as pool:
    ...