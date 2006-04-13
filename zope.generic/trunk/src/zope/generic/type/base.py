##############################################################################
#
# Copyright (c) 2005, 2006 Zope Corporation and Contributors.
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
$Id$
"""

__docformat__ = 'restructuredtext'

from persistent import Persistent

from zope.interface import implements

from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.container import contained
from zope.app.container import btree
from zope.app import folder

from zope.generic.component.api import IAttributeConfigurable
from zope.generic.directlyprovides.api import provides
from zope.generic.directlyprovides.api import UpdateProvides
from zope.generic.directlyprovides.api import updateDirectlyProvided

from zope.generic.type import IDirectlyTyped
from zope.generic.type import IInitializer



class Object(object):
    """Default implementation for simple objects."""

    implements(IDirectlyTyped, IAttributeConfigurable, IAttributeAnnotatable)

    def __init__(self, interface, *pos, **kws):
        super(Object, self).__init__()
        self.__dict__['interface'] = interface
        updateDirectlyProvided(self, interface)
        initializer = IInitializer(self, None)
        if initializer:
            initializer(*pos, **kws)

    provides('interface')

    interface = UpdateProvides(IDirectlyTyped['interface'])



class Contained(contained.Contained, Persistent):
    """Default implementation local, persistend and contained objects."""

    implements(IDirectlyTyped, IAttributeConfigurable, IAttributeAnnotatable)

    def __init__(self, interface, *pos, **kws):
        super(Contained, self).__init__()
        self.__dict__['interface'] = interface
        updateDirectlyProvided(self, interface)
        initializer = IInitializer(self, None)
        if initializer:
            initializer(*pos, **kws)

    provides('interface')

    interface = UpdateProvides(IDirectlyTyped['interface'])



class Container(btree.BTreeContainer):
    """Default implementation local, persistend and containerish objects."""

    implements(IDirectlyTyped, IAttributeConfigurable, IAttributeAnnotatable)

    def __init__(self, interface, *pos, **kws):
        super(Container, self).__init__()
        self.__dict__['interface'] = interface
        updateDirectlyProvided(self, interface)
        initializer = IInitializer(self, None)
        if initializer:
            initializer(*pos, **kws)

    provides('interface')

    interface = UpdateProvides(IDirectlyTyped['interface'])



class Folder(folder.Folder):
    """Default implementation local, persistend and containerish possible sites."""

    implements(IDirectlyTyped, IAttributeConfigurable, IAttributeAnnotatable)

    def __init__(self, interface, *pos, **kws):
        super(Folder, self).__init__()
        self.__dict__['interface'] = interface
        updateDirectlyProvided(self, interface)
        initializer = IInitializer(self, None)
        if initializer:
            initializer(*pos, **kws)

    provides('interface')

    interface = UpdateProvides(IDirectlyTyped['interface'])
