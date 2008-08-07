from zope.interface import implements
from zope.app.error.interfaces import IErrorReportingUtility

class ErrorReporting(object):
    implements(IErrorReportingUtility)
    
    def raising(self, info, request=None):
        raise info[0], info[1], info[2]
        
globalErrorReporting = ErrorReporting()
