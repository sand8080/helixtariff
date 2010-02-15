import unittest
import doctest
from helixtariff import utils

from helixtariff.test.wsgi.test_application_loading import ApplicationTestCase #IGNORE:W0611 @UnusedImport

from helixtariff.test.validator.test_validator import ValidatorTestCase #IGNORE:W0611 @UnusedImport
from helixtariff.test.logic.test_ping import PingTestCase #IGNORE:W0611 @UnusedImport
from helixtariff.test.logic.test_client import ClientTestCase #IGNORE:W0611 @UnusedImport
from helixtariff.test.logic.test_service_type import ServiceTypeTestCase #IGNORE:W0611 @UnusedImport
from helixtariff.test.logic.test_service_set import ServiceSetTestCase #IGNORE:W0611 @UnusedImport
from helixtariff.test.logic.test_tariff import TariffTestCase #IGNORE:W0611 @UnusedImport
from helixtariff.test.logic.test_rule import RuleTestCase #IGNORE:W0611 @UnusedImport
from helixtariff.test.logic.test_price import PriceTestCase #IGNORE:W0611 @UnusedImport
from helixtariff.test.logic.test_action_log import ActionLogTestCase #IGNORE:W0611 @UnusedImport

from helixtariff.test.rulesengine.test_engine import EngineTestCase #IGNORE:W0611 @UnusedImport
from helixtariff.test.rulesengine.test_checker import RuleChecker #IGNORE:W0611 @UnusedImport

from helixtariff.test.test_utils import UtilsTestCase #IGNORE:W0611 @UnusedImport

doctest.testmod(utils)


if __name__ == '__main__':
    unittest.main()