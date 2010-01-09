from helixcore.db.wrapper import EmptyResultSetError


class HelixtariffError(Exception):
    pass


class TariffCycleError(HelixtariffError):
    pass


class TariffNotFound(HelixtariffError):
    def __init__(self, name):
        super(TariffNotFound, self).__init__('''Tariff '%s' not found.''' % name)


class ObjectNotFound(HelixtariffError):
    pass


class RuleNotFound(HelixtariffError):
    pass


class ServiceTypeNotFound(ObjectNotFound):
    def __init__(self, name):
        super(ServiceTypeNotFound, self).__init__('''Service type '%s' not found''' % name)


class ClientNotFound(EmptyResultSetError, HelixtariffError):
    def __init__(self, client_id):
        super(ClientNotFound, self).__init__('''Client '%s' not found.''' % client_id)
