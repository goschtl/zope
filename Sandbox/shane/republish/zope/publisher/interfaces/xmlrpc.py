

from zope.deferredimport import deprecatedFrom
from zope.publisher.interfaces.http import IHTTPRequest

class IXMLRPCRequest(IHTTPRequest):
    """XML-RPC Request
    """

deprecatedFrom("moved to zope.complextraversal.interfaces",
    "zope.complextraversal.interfaces",
    "IXMLRPCPublisher")
