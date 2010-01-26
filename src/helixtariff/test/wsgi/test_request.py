# coding=utf-8
import datetime
import unittest

from helixtariff.test.db_based_test import DbBasedTestCase
from helixtariff.test.wsgi.client import Client


class ReqTestCase(DbBasedTestCase):
    nginx_host = 'guano.loc'
    nginx_port = 1053

    def setUp(self):
        super(ReqTestCase, self).setUp()
        self.cli = Client(self.nginx_host, self.nginx_port, '%s' % datetime.datetime.now(),
            'qazwsx', protocol='https')

    def test_get_empty_service_types(self):
        print '###', self.cli.add_client(login=self.cli.login, password=self.cli.password) #IGNORE:E1101
        print '###', self.cli.view_service_types(login=self.cli.login, password=self.cli.password) #IGNORE:E1101

if __name__ == '__main__':
    unittest.main()
