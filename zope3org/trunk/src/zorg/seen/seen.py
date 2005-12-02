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

$Id: comments.py 39651 2005-10-26 18:36:17Z oestermeier $
"""

from persistent.dict import PersistentDict
from datetime import datetime
import pytz

from zope.component import adapts
from zope.event import notify
from zope.interface import implements

from zope.app.annotation.interfaces import IAnnotations
from zope.app.event.objectevent import ObjectModifiedEvent
from zope.app.event.objectevent import Sequence, Attributes
from zope.app.location import Location

from zorg.seen.interfaces import ISeeable
from zorg.seen.interfaces import ISeen


seenKey = 'zorg.seen'

def dottedName(klass):
    if klass is None:
        return 'None'
    return klass.__module__ + '.' + klass.__name__

def now() :
    return datetime.now(pytz.utc)

class SeenForAnnotableObjects(Location):
    """Annotate objects as seen or unseen."""

    adapts(ISeeable,)
    implements(ISeen)

    def __init__(self, context):
        self.context = context

    # private methods
    def _get_seen(self):
        annotations = self.__dict__.get('_annotations')
        
        if annotations is None:
            self.__dict__['_annotations']= annotations = IAnnotations(self.context)
        
        return annotations.get(seenKey, None)

    seen = property(_get_seen)

    def _assert_seen(self):
        if self._get_seen() is None:
            self.__dict__['_annotations'][seenKey] = PersistentDict()

    # public methods
    def __getitem__(self, key):
        """See zope.interface.common.mapping.IItemMapping"""
        if self.seen is not None:
            return self.seen.__getitem__(key)
        else:
            raise KeyError(key)

    def get(self, key, default=None):
        """See zope.interface.common.mapping.IReadMapping"""
        if self.seen is not None:
            return self.seen.get(key, default)
        else:
            return default

    def __contains__(self, key):
        """See zope.interface.common.mapping.IReadMapping"""
        if self.seen is not None:
            return self.seen.__contains__(key)
        else:
            return False

    def keys(self):
        """See zope.interface.common.mapping.IEnumerableMapping"""
        if self.seen is not None:
            return self.seen.keys()
        else:
            return []

    def __iter__(self):
        """See zope.interface.common.mapping.IEnumerableMapping"""
        if self.seen is not None:
            return self.seen.__iter__()
        else:
            return iter([])

    def values(self):
        """See zope.interface.common.mapping.IEnumerableMapping"""
        if self.seen is not None:
            return self.seen.values()
        else:
            return []

    def items(self):
        """See zope.interface.common.mapping.IEnumerableMapping"""
        if self.seen is not None:
            return self.seen.items()
        else:
            return []

    def __len__(self):
        """See zope.interface.common.mapping.IEnumerableMapping"""
        if self.seen is not None:
            return self.seen.__len__()
        else:
            return 0
            
    def __delitem__(self, key) :
        if self.seen is not None:
            self.seen.__delitem__(key)
            notify(ObjectModifiedEvent(self.context, Attributes(ISeen)))
        else:
            raise KeyError(key)
        

    def markAsSeen(self, principal_id, when=None):
        """ Stores the datetime at which a principal has seen the item. """
        
        if when is None :
            when = now()
            
        self._assert_seen()
        self.seen[principal_id] = when
        notify(ObjectModifiedEvent(self.context, Sequence(ISeen, principal_id)))
        return principal_id
        
    def markAsUnseen(self, principal_id) :
        """ Removes the mark. """
        if self.seen is not None:
            del self.seen[principal_id]
               
    def hasSeen(self, principal_id) :
        """ Returns `True` iff the principal has seen the item. """
        if self.seen :
            return self.get(principal_id) is not None
        return False
        
    def when(self, principal_id) :
        """ Returns the datetime at which the principal
            marked the item as seen.
        """
        return self.get(principal_id)

