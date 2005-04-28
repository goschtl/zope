##############################################################################
#
# Copyright (c) 2005 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Parrot directive and support classes

$Id: metaconfigure.py 5287 2004-06-25 11:42:27Z philikon $
"""

from zope.interface import Interface
from zope.configuration.fields import GlobalObject
from zope.schema import TextLine

class IParrotDirective(Interface):
    """State that a class implements something.
    """
    class_ = GlobalObject(
        title=u"Class",
        required=True
        )

    name = TextLine(
        title=u"Name",
        description=u"The parrots name.",
        required=True
        )
    
def parrot(_context, class_, name):
    parrot = class_()
    parrot.pineForFjords()
    
    
class NorwegianBlue(object):
    
    def pineForFjords(self):
        return "This parrot is no more!"
        
