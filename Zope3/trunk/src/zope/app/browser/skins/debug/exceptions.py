import sys
import traceback

from zope.interface.common.interfaces import IException

class ExceptionDebugView:

    """ Render exceptions for debugging.
    """
    __used_for__ = ( IException, )

    def __init__( self, context, request ):

        self.context = context
        self.request = request

        self.error_type, self.error_object, tb = sys.exc_info()
        try:
            self.traceback_lines = traceback.format_tb( tb )
        finally:
            del tb
