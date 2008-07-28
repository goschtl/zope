# coding = utf-8
""" Interfaces for hierarchical roles """

from zope.schema import TextLine
from zope.securitypolicy.interfaces import IRole

class IHRole(IRole):
    """A hierarchical role object."""

    includes = TextLine(
        title=u"Includes",
        description=u"Role includes other roles",
        required=False)

    
        
        
        
