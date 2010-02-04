from remotetaskexample.interfaces import IExampleTask
from lovely.remotetask.service import TaskService
from OFS.SimpleItem import SimpleItem

class ExampleService(TaskService, SimpleItem):
    taskInterface = IExampleTask

    def __init__(self):
        super(ExampleService, self).__init__()
        parent = getattr(self, '__parent__', None)
        if parent:
            self.startProcessing()
