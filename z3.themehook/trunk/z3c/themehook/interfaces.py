"""Interfaces
"""

from zope.interface import Interface

class IPublicationObjectCaller(Interface):
    """IPublicationCaller calls the object with the request
    
    Calling IPublicationCaller should generate the output to be passed to
    the publisher. An IPublicationCaller should be an adapter between
    (ob, request) and IPublicationCaller."""

    def __call__():
        """calls the object"""
        