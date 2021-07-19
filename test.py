class Test(object):
    def __init__(self, id, module):
        self.id = id
        self.module = module
        self.json = {}
        self.testOrder = []
        self.failures = []


class testFailure(object):
    def __init__(self, name, time, stackTrace):
        self.name = name
        self.stackTrace = stackTrace
        self.time = time

