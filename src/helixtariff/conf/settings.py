DSN = 'dbname=_DBC_DBNAME_ host=_DBC_DBSERVER_ user=_DBC_DBUSER_ password=_DBC_DBPASS_'

patch_table_name = 'patches'

server_http_addr = '0.0.0.0'
server_http_port = 9998

server_https_addr = '0.0.0.0'
server_https_port = 9999

import logging
log_filename = '/var/log/helix/helixtariff.log'
log_level = logging.DEBUG
log_format = "%(asctime)s [%(levelname)s] - %(message)s"
log_console = False

import lock_order #IGNORE:W0611 @UnusedImport
