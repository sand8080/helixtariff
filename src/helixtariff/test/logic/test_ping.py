import unittest

from helixtariff.test.db_based_test import ServiceTestCase
from helixtariff.logic.actions import handle_action


class PingTestCase(ServiceTestCase):
    def test_ping(self):
        handle_action('ping', {})


if __name__ == '__main__':
    unittest.main()