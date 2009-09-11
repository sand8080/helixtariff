import helixtariff.test.test_environment #IGNORE:W0611 @UnusedImport

from helixcore.install import install
from helixtariff.conf.db import get_connection
from helixtariff.conf.settings import patch_table_name
from helixtariff.test.test_environment import patches_path

from root_test import RootTestCase


class DbBasedTestCase(RootTestCase):
    def setUp(self):
        install.execute('reinit', get_connection, patch_table_name, patches_path)

