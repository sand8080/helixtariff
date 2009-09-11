import psycopg2
from functools import partial

import helixcore.db.wrapper as wrapper
from settings import DSN

get_connection = partial(psycopg2.connect, DSN)
transaction = partial(wrapper.transaction, get_connection)
