import sys

from BTrees.IOBTree import IOBTree
from OFS.SimpleItem import SimpleItem

from z3c.taskqueue.baseservice import BaseTaskService


class TaskService(BaseTaskService, SimpleItem):
    containerClass = IOBTree
    maxint = sys.maxint

    def getServicePath(self):
        path = [part for part in self.getPhysicalPath() if part]
        return path


def setNameAndParent(object, event):
    object.__name__ = event.newName
    event.object.__parent__ = event.newParent
