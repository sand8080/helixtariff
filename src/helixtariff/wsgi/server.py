import logging
from eventlet import api, wsgi

from helixcore.server.wsgi_application import Application
import helixcore.mapping.actions as mapping

from helixtariff.conf import settings
from helixtariff.conf.log import logger
from helixtariff.logic.actions import handle_action
from helixtariff.validator.validator import protocol
from helixtariff.logic import selector
from helixtariff.conf.db import transaction
from helixtariff.domain.objects import ActionLog
from helixtariff.error import ClientNotFound


class HelixtariffApplication(Application):
    def __init__(self, h, p, l):
        self.unauthorized_trackable = ['add_client']
        super(HelixtariffApplication, self).__init__(h, p, l, (
            'add_client', 'modify_client', 'delete_client',
            'add_service_type', 'modify_service_type', 'delete_service_type',
            'add_service_set', 'modify_service_set', 'delete_service_set',
            'add_tariff', 'modify_tariff', 'delete_tariff',
            'save_draft_rule', 'make_draft_rules_actual', 'modify_actual_rule',
        ))

    @transaction()
    def track_api_call(self, s_req, s_resp, authorized_data, curs=None): #IGNORE:W0221
        super(HelixtariffApplication, self).track_api_call(s_req, s_resp, authorized_data)
        action_name = authorized_data['action']
        c_id = None
        if action_name in self.unauthorized_trackable:
            try:
                login = authorized_data['login']
                c_id = selector.get_client_by_login(curs, login).id
            except ClientNotFound:
                self.logger.log(logging.ERROR,
                    'Unable to track action for not existed client. Request: %s. Response: %s', (s_req, s_resp))
        else:
            c_id = authorized_data['client_id']
        data = {
            'client_id': c_id,
            'source': authorized_data.get('source', None),
            'action': action_name,
            'request': s_req,
            'response': s_resp,
        }
        mapping.insert(curs, ActionLog(**data))


class Server(object):
    class ServerLog(object):
        def write(self, s, l=0): #IGNORE:W0613
            logger.log(l, 'server: %s' % s)

    @staticmethod
    def run():
        wsgi.server(
            api.tcp_listener((settings.server_host, settings.server_port)),
            HelixtariffApplication(handle_action, protocol, logger),
            max_size=5000,
            log=Server.ServerLog()
        )
