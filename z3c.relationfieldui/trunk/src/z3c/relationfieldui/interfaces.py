from zc.sourcefactory.interfaces import IValuePolicy

class IRelationValuePolicy(IValuePolicy):    
    def getTargets():
        """Return an iterable of objects that are potential relation targets.
        """

