from zope import interface

class IResponseHeaderSetter(interface.Interface):

    def setHeaders():
        """sets the response headers for the view"""
    
