from helixcore.db.wrapper import EmptyResultSetError


class HelixtariffError(Exception):
    pass


class ClientNotFound(EmptyResultSetError, HelixtariffError):
    def __init__(self, id):
        super(ClientNotFound, self).__init__('Client %s not found.' % id)
