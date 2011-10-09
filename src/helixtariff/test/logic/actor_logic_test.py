from helixcore.security import Session
import helixcore.test.logic.access_granted #@UnusedImport
from helixcore.test.logic.access_granted import (GRANTED_ENV_ID,
    GRANTED_USER_ID)

from helixtariff.test.logic.logic_test import LogicTestCase


class ActorLogicTestCase(LogicTestCase):
    def login_actor(self):
        return Session('ACTOR_LOGIC_TEST_CASE', GRANTED_ENV_ID, GRANTED_USER_ID)

