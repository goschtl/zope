from remotetaskexample.interfaces import IExampleTask
from zope.interface import implements

class ExampleTask(object):
    implements(IExampleTask)

    def __call__(self, service, jobid, input):
        print "Running", input
