from helixcore.mapping.objects import Mapped


class ServiceType(Mapped):
    __slots__ = ['id', 'name']
    table = 'service_type'
