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

$Id: tests.py 38895 2005-10-07 15:09:36Z dominikhuber $
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface
from zope.interface import Attribute

from zope.i18n import MessageIDFactory


_ = MessageIDFactory("zorg.wikification")
          


class IWikiPage(Interface) :
    """ A wiki page that 'wikifies' a folder with ordinary HTML documents.
    
        See wikification/README.txt for a definition of what 
        'wikification' means and doctests of the methods of this class.
        
    """
   
        
class IWikiContainerPage(IWikiPage) :
    """ Wiki view for a container. """
    
class IWikiFilePage(IWikiPage) :
    """ Wiki view for a file. """
            
        
class IEditWikiPage(IWikiPage) :
    """ Edit view for a file. """

class ICreateWikiPage(IWikiPage) :
    """ Edit view for a folder. """