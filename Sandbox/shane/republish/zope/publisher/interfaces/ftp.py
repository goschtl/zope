
from zope.deferredimport import deprecatedFrom
from zope.publisher.interfaces.base import IRequest

class IFTPRequest(IRequest):
    """FTP Request
    """

deprecatedFrom("moved to zope.complextraversal.interfaces",
    "zope.complextraversal.interfaces",
    "IFTPPublisher")
