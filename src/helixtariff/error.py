from helixtariff import error_code
from helixcore.db.wrapper import ObjectCreationError, ObjectNotFound
from helixcore import security


class HelixtariffError(Exception):
    code = error_code.HELIXTARIFF_ERROR


class HelixtariffObjectAlreadyExists(HelixtariffError, ObjectCreationError):
    def __init__(self, *args, **kwargs):
        super(HelixtariffObjectAlreadyExists, self).__init__(*args, **kwargs)
        self.code = error_code.HELIXTARIFF_OBJECT_ALREADY_EXISTS


class HelixtariffObjectNotFound(HelixtariffError, ObjectNotFound):
    def __init__(self, class_name, **kwargs):
        sanitized_kwargs = security.sanitize_credentials(kwargs)
        super(HelixtariffObjectNotFound, self).__init__('%s not found by params: %s' %
            (class_name, sanitized_kwargs))
        self.code = error_code.HELIXTARIFF_OBJECT_NOT_FOUND


class TarifficationObjectNotFound(HelixtariffObjectNotFound):
    def __init__(self, **kwargs):
        super(TarifficationObjectNotFound, self).__init__('TarifficationObject', **kwargs)
        self.code = error_code.HELIXTARIFF_TARIFFICATION_OBJECT_NOT_FOUND


class TariffNotFound(HelixtariffObjectNotFound):
    def __init__(self, **kwargs):
        super(TariffNotFound, self).__init__('Tariff', **kwargs)
        self.code = error_code.HELIXTARIFF_TARIFF_NOT_FOUND


class TariffCycleError(HelixtariffError):
    code = error_code.HELIXTARIFF_TARIFF_CYCLE

#class RuleNotFound(ObjectNotFound):
#    pass
#
#
#class ServiceTypeUsed(HelixtariffError):
#    pass
#
#
#class TariffUsed(HelixtariffError):
#    pass
#
#
#class ServiceTypeNotFound(ObjectNotFound):
#    def __init__(self, name):
#        super(ServiceTypeNotFound, self).__init__("Service type '%s' not found" % name)
#
#
#class ServiceTypeNotInServiceSet(HelixtariffError):
#    def __init__(self, st_name, ss_name):
#        super(ServiceTypeNotInServiceSet, self).__init__("Service type '%s' not in service set '%s'"
#            % (st_name, ss_name))
#
#
#class ServiceSetNotEmpty(HelixtariffError):
#    def __init__(self, name):
#        super(ServiceSetNotEmpty, self).__init__("Service set '%s' contains service types" % name)
#
#
#class ServiceSetNotFound(ObjectNotFound):
#    def __init__(self, name):
#        super(ServiceSetNotFound, self).__init__("Service set '%s' not found" % name)
#
#
#class ServiceSetUsed(HelixtariffError):
#    def __init__(self, tariffs):
#        super(ServiceSetUsed, self).__init__("Service set used in tariffs '%s'" % tariffs)
#
#
#class OperatorNotFound(ObjectNotFound):
#    def __init__(self, operator_id):
#        super(OperatorNotFound, self).__init__("Operator '%s' not found" % operator_id)
