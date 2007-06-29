""" Collector interfaces

$Id$
"""
from zope.interface import Interface

class ICollector(Interface):
    """ Marker interface for collectors.
    """

class ICollectorIssue(Interface):
    """ Marker interface for collector issues.
    """
