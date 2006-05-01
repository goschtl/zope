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
from zope.schema.fieldproperty import FieldProperty

from zope.app.container import contained
from zope.app.container import btree
from zope.app.container import ordered
from zope.app import folder

from zope.generic.directlyprovides.api import provides
from zope.generic.directlyprovides.api import UpdateProvides
from zope.generic.face.api import Face

from zope.generic.content import IDirectlyTypedContent



class Object(Face, Persistent):
    """Default implementation for simple objects."""

    implements(IDirectlyTypedContent)

    def __init__(self, *pos, **kws):
        super(Object, self).__init__()

    provides('__keyface__')

    __keyface__ = UpdateProvides(IDirectlyTypedContent['__keyface__'])
    __conface__ = FieldProperty(IDirectlyTypedContent['__conface__'])
    
    @property
    def keyface(self):
        return self.__keyface__



class Contained(Face, contained.Contained, Persistent):
    """Default implementation local, persistend and contained objects."""

    implements(IDirectlyTypedContent)

    def __init__(self, *pos, **kws):
        super(Contained, self).__init__()

    provides('__keyface__')

    __keyface__ = UpdateProvides(IDirectlyTypedContent['__keyface__'])
    __conface__ = FieldProperty(IDirectlyTypedContent['__conface__'])

    @property
    def keyface(self):
        return self.__keyface__


class Container(Face, btree.BTreeContainer):
    """Default implementation local, persistend and containerish objects."""

    implements(IDirectlyTypedContent)

    def __init__(self, *pos, **kws):
        super(Container, self).__init__()

    provides('__keyface__')

    __keyface__ = UpdateProvides(IDirectlyTypedContent['__keyface__'])
    __conface__ = FieldProperty(IDirectlyTypedContent['__conface__'])

    @property
    def keyface(self):
        return self.__keyface__



class OrderedContainer(Face, ordered.OrderedContainer):
    """Default implementation local, persistend and ordered-containerish objects."""

    implements(IDirectlyTypedContent)

    def __init__(self, *pos, **kws):
        super(OrderedContainer, self).__init__()

    provides('__keyface__')

    __keyface__ = UpdateProvides(IDirectlyTypedContent['__keyface__'])
    __conface__ = FieldProperty(IDirectlyTypedContent['__conface__'])

    @property
    def keyface(self):
        return self.__keyface__



class Folder(Face, folder.Folder):
    """Default implementation local, persistend and containerish possible sites."""

    implements(IDirectlyTypedContent)

    def __init__(self, *pos, **kws):
        super(Folder, self).__init__()

    provides('__keyface__')

    __keyface__ = UpdateProvides(IDirectlyTypedContent['__keyface__'])
    __conface__ = FieldProperty(IDirectlyTypedContent['__conface__'])
