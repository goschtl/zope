##############################################################################
#
# Copyright (c) 2004-2009 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Shared dependency less Zope3 brwoser components.
"""
__docformat__ = 'restructuredtext'

from zope.interface import Attribute
from zope.interface import Interface

class IView(Interface):
    """ Views are multi-adapters for context and request objects.
    """
    context = Attribute("The context object the view renders")
    request = Attribute("The request object driving the view")

class IBrowserView(IView):
    """ Views which are specialized for requests from a browser
    
    o Such views are distinct from those geerated via WebDAV, FTP, XML-RPC,
      etc..
    """

class ITerms(Interface):
    """ Adapter providing lookups for vocabulary terms.
    """
    def getTerm(value):
        """Return an ITitledTokenizedTerm object for the given value

        LookupError is raised if the value isn't in the source
        """

    def getValue(token):
        """Return a value for a given identifier token

        LookupError is raised if there isn't a value in the source.
        """
