import logging
import os

DSN = {
    'user': '_DBC_DBUSER_',
    'database': '_DBC_DBNAME_',
    'host': '_DBC_DBSERVER_',
    'password': '_DBC_DBPASS_'
}

DSN = {
    'user': 'helixtest',
    'database': 'test_helixtariff',
    'host': 'localhost',
    'password': 'qazwsx'
}

patch_table_name = 'patches'

server_host = 'localhost'
server_port = 9997
server_connections = 50

log_filename = os.path.join(os.path.dirname(__file__), '..', '..', 'log',
    'helixtariff.log')
log_level = logging.DEBUG
log_format = "%(asctime)s [%(levelname)s] - %(message)s"
log_console = False
log_max_bytes = 2048000
log_backup_count = 20

auth_server_url = 'http://localhost:9999'
