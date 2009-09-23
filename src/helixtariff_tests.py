import unittest

from helixtariff.test.validator.test_validator import ValidatorTestCase #IGNORE:W0611 @UnusedImport

from helixtariff.test.server.test_server import ServerTestCase #IGNORE:W0611 @UnusedImport

from helixtariff.test.logic.test_service_type import ServiceTypeTestCase #IGNORE:W0611 @UnusedImport
from helixtariff.test.logic.test_service_set_descr import ServiceSetDescrTestCase #IGNORE:W0611 @UnusedImport
from helixtariff.test.logic.test_service_set import ServiceSetTestCase #IGNORE:W0611 @UnusedImport


if __name__ == '__main__':
    unittest.main()
