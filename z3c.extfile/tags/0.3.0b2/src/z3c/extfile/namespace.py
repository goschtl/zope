from zope.traversing.namespace import view
from zope.traversing.interfaces import TraversalError
import datamanager

class Static(view):

    def traverse(self, name, ignored):
        if len(name)==40:
            try:
                return datamanager.getFile(str(name))
            except KeyError:
                pass
        raise TraversalError(self.context, name)


