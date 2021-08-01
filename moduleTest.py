class moduleTest(object):
    def __init__(self, moduleName):
        self.moduleName = moduleName
        self.directory = ''
        self.repository = ''
        self.testSet = []
        self.nFlakies = 0
        self.single_mapped_failures = {}
        self.multi_mapped_failures = {}
        self.none_mapped_failures = {}
