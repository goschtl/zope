##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""

$Id: interfaces.py 39651 2005-10-26 18:36:17Z oestermeier $
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface
from zope.interface import Attribute

from zope.schema import Bytes, BytesLine

from zope.app.container.interfaces import IContainer
from zope.i18n import MessageIDFactory


_ = MessageIDFactory("zorg.ajax")

                
class IAjaxPage(Interface) :
    """ A web page that contains Ajax calls.
    """

class IAjaxLiveSearchPage(IAjaxPage) :
    """ A web page that contains a ajax live search facility.
    """
    
class ILiveChanges(IAjaxPage) :
    """ A web page with a periodical subscriber to server events. """

class ILivePage(IAjaxPage) :
    """ A web page with a subscriber to streamed server events. """

    
class IAjaxUpdateable(Interface) :
    """ An updatable part that produces HTML that can be used to update
        the innerHTML of an ajax page. """
        
    def render(method=None, parameter=None) :
        """ Renders the updated part of the page as HTML. """

        
class IPageElement(Interface) :
    """ A part of a page that can be accessed via path traversal. """
    
    name = Attribute(u"The name of the part.")
    parent = Attribute(u"The parent object that contains this part.")

    
class ISettingsStorage(Interface) :
    """ A persistent object for user specific settings. Can be stored
        in the session or principal annotations.
    """
