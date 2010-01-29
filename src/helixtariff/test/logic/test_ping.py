import unittest

from helixtariff.test.db_based_test import ServiceTestCase


class PingTestCase(ServiceTestCase):
    def test_ping(self):
        self.handle_action('ping', {})


if __name__ == '__main__':
    unittest.main()