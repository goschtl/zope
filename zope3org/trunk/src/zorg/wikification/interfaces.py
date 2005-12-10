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

$Id: $
"""

from zope.interface import Interface


class IEditPolicy(Interface) :
    """ This interface describes the requirements to switch between
        rest and html editable content.
        
    """   
    
    def update(self, content, contentType="text/html", asContentType=None):
        """Update the content object using the editor output.
        
           contentType describes the provided content
           targetContentType prescribes in which format the content should be
           saved.

        """
           
    def display(self, asContentType=None):
        """ Display the content as "text/html" or "text/plain" (rest) """