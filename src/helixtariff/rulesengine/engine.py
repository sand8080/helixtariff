class PythonTranslator(object):
    pass


class Loader(object):
    def load(self, context):
        tariff = None
        return tariff


class Executor(object):
    def __init__(self, tariff):
        self.tariff = tariff

    def call(self, request):
        return self.tariff.compute(request)
