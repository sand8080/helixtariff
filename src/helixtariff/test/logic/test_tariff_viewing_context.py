import unittest

from helixtariff.test.logic.actor_logic_test import ActorLogicTestCase
from helixtariff.db.dataobject import Tariff
from helixcore.error import RequestProcessingError


class TariffViewingContextCase(ActorLogicTestCase):
    def test_stub(self):
        t_id = self._add_tariff('t', currency='RUB')
        t_v_name = 'first'
        context = [{'name': 'num', 'value': 4}, {'name': 'param', 'value': 'like'}]
        view_order = 1
        t_v_id = self._add_tariff_viewing_context(t_v_name,
            t_id, context, view_order=view_order)


if __name__ == '__main__':
    unittest.main()