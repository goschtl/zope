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

$Id: interfaces.py 38949 2005-10-08 13:28:58Z dominikhuber $
"""

from zope.interface import Interface

from zope.app.annotation.interfaces import IAnnotatable
from zope.app.annotation.interfaces import IAttributeAnnotatable

from zope.interface.common.mapping import IEnumerableMapping
from zope.interface.common.mapping import IWriteMapping

class ISeeable(IAnnotatable):
    """This interface marks components that should provide annotable seen
       marker.
    
        Components has to provide a annotations mechanism.
    """


class ISeeableAttributeAnnotable(ISeeable, IAttributeAnnotatable):
    """This interface marks components that should provide 
       attribute annotable seen marker.
    """


class ISeen(IEnumerableMapping, IWriteMapping):
    """Mark an object as seen or unseen in an enumerable mapping with
       principal ids as keys and datetime objects as values.
    """

    def markAsSeen(self, principal_id, datetime=None) :
        """ Stores the datetime at which a principal has seen the item. 
            Uses the current datetime as a default value.
        """ 
        
    def markAsUnseen(self, principal_id) :
        """ Removes the mark. """
        
    def hasSeen(self, principal_id) :
        """ Returns `True` iff the principal has seen the item. """
        
    def when(self) :
        """ Returns the datetime at which the user has seen the item. """


