##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Filesystem synchronization registry.

$Id: fsregistry.py,v 1.2 2003/05/05 18:01:01 gvanrossum Exp $
"""

from zope.app.interfaces.fssync import IGlobalFSSyncService
from zope.exceptions import DuplicationError, NotFoundError

class FSRegistry(object):
    """Registry Wrapper class.

    This is a maping from Class -> Serializer Factory Method.
    """

    __implements__ = IGlobalFSSyncService

    def __init__(self):
        self._class_factory_reg = {}
        
    def __call__(self):
        return self.__init__()

    def getSynchronizer(self, object):
        """Return factory method for a given class.

        The factory is returned of the object if None of the 
        Factory method is present return default factory.
        """

        factory = self._class_factory_reg.get(object.__class__)
        if factory is None:
            factory = self._class_factory_reg.get(None)
            if factory is None:
                raise NotFoundError
        return factory(object)


    def provideSynchronizer(self,class_, factory):
        """Set class_, factory into the dictionary."""
        if class_ in self._class_factory_reg:
            raise  DuplicationError
        else:
            self._class_factory_reg[class_] = factory

    _clear = __init__


# The FS registry serializer service instance
fsRegistry = FSRegistry()
provideSynchronizer = fsRegistry.provideSynchronizer
getSynchronizer = fsRegistry.getSynchronizer

_clear = fsRegistry._clear

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from zope.testing.cleanup import addCleanUp
addCleanUp(_clear)
del addCleanUp
