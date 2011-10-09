from helixcore.install import install

# must be imported before other user imports
from helixtariff.test.root_test import RootTestCase

from helixtariff.conf.db import get_connection, put_connection
from helixtariff.conf.settings import patch_table_name
from helixtariff.test.test_env import patches_path


class DbBasedTestCase(RootTestCase):
    def setUp(self):
        install.execute('reinit', get_connection, put_connection, patch_table_name, patches_path)
