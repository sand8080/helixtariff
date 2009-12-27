from helixcore.db.wrapper import EmptyResultSetError


class HelixtariffError(Exception):
    pass


class TariffCycleError(HelixtariffError):
    pass


class NoRuleFound(HelixtariffError):
    pass


class ClientNotFound(EmptyResultSetError, HelixtariffError):
    def __init__(self, client_id):
        super(ClientNotFound, self).__init__('Client %s not found.' % client_id)
