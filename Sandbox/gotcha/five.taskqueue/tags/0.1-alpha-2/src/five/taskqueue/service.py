import sys

from BTrees.IOBTree import IOBTree
from OFS.SimpleItem import SimpleItem

from z3c.taskqueue.baseservice import BaseTaskService
from five.taskqueue import processor


class TaskService(BaseTaskService, SimpleItem):
    containerClass = IOBTree
    maxint = sys.maxint

    processorFactory = processor.SimpleProcessor

    def getServicePath(self):
        path = [part for part in self.getPhysicalPath() if part]
        return path


def setNameAndParent(object, event):
    object.__name__ = event.newName
    event.object.__parent__ = event.newParent
