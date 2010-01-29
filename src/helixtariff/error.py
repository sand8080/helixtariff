class HelixtariffError(Exception):
    pass


class TariffCycleError(HelixtariffError):
    pass


class TariffNotFound(HelixtariffError):
    def __init__(self, name):
        super(TariffNotFound, self).__init__("Tariff '%s' not found" % name)


class ObjectNotFound(HelixtariffError):
    pass


class RuleNotFound(ObjectNotFound):
    pass


class ServiceTypeUsed(HelixtariffError):
    pass


class TariffUsed(HelixtariffError):
    pass


class ServiceTypeNotFound(ObjectNotFound):
    def __init__(self, name):
        super(ServiceTypeNotFound, self).__init__("Service type '%s' not found" % name)


class ServiceTypeNotInServiceSet(HelixtariffError):
    def __init__(self, st_name, ss_name):
        super(ServiceTypeNotInServiceSet, self).__init__("Service type '%s' not in service set '%s'"
            % (st_name, ss_name))


class ServiceSetNotEmpty(HelixtariffError):
    def __init__(self, name):
        super(ServiceSetNotEmpty, self).__init__("Service set '%s' contains service types" % name)


class ServiceSetNotFound(ObjectNotFound):
    def __init__(self, name):
        super(ServiceSetNotFound, self).__init__("Service set '%s' not found" % name)


class ClientNotFound(ObjectNotFound):
    def __init__(self, client_id):
        super(ClientNotFound, self).__init__("Client '%s' not found" % client_id)