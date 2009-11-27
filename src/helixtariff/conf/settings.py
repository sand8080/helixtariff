DSN = {
    'user': '_DBC_DBUSER_',
    'database': '_DBC_DBNAME_',
    'host': '_DBC_DBSERVER_',
    'password': '_DBC_DBPASS_'
}

patch_table_name = 'patches'

server_host = 'localhost'
server_port = 9999

import logging
log_filename = '/var/log/helix/helixtariff.log'
log_level = logging.INFO
log_format = "%(asctime)s [%(levelname)s] - %(message)s"
log_console = False

import lock_order #IGNORE:W0611 @UnusedImport
