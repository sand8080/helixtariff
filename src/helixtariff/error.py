from helixcore.server.exceptions import ActionNotAllowedError


class HelixtariffError(Exception):
    pass


class OperatorAlreadyExists(ActionNotAllowedError, HelixtariffError):
    def __init__(self, login):
        super(OperatorAlreadyExists, self).__init__("Operator '%s' already exists" % login)


class TariffCycleError(HelixtariffError):
    pass


class ObjectNotFound(HelixtariffError):
    pass


class TariffNotFound(ObjectNotFound):
    def __init__(self, name):
        super(TariffNotFound, self).__init__("Tariff '%s' not found" % name)


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


class ServiceSetUsed(HelixtariffError):
    def __init__(self, tariffs):
        super(ServiceSetUsed, self).__init__("Service set used in tariffs '%s'" % tariffs)


class OperatorNotFound(ObjectNotFound):
    def __init__(self, operator_id):
        super(OperatorNotFound, self).__init__("Operator '%s' not found" % operator_id)
