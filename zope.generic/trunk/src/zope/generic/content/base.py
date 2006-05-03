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

from zope.app import folder
from zope.app.component.interfaces import IPossibleSite
from zope.app.component.interfaces import ISite
from zope.app.component.interfaces import NewLocalSite 
from zope.app.container import btree
from zope.app.container import contained
from zope.app.container import ordered
from zope.component.interfaces import ComponentLookupError
from zope.component.interfaces import IComponentLookup
from zope.event import notify
from zope.interface import directlyProvidedBy
from zope.interface import directlyProvides
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

from zope.generic.content import IDirectlyTypedContent
from zope.generic.directlyprovides.api import UpdateProvides
from zope.generic.directlyprovides.api import provides
from zope.generic.face.api import Face



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



class OrderedFolder(ordered.OrderedContainer):
    """Default implementation local, persistend and ordered-folderish objects."""


    implements(IDirectlyTypedContent, IPossibleSite)

    def __init__(self, *pos, **kws):
        super(OrderedFolder, self).__init__()

    provides('__keyface__')

    __keyface__ = UpdateProvides(IDirectlyTypedContent['__keyface__'])
    __conface__ = FieldProperty(IDirectlyTypedContent['__conface__'])



    _sm = None

    def getSiteManager(self):
        if self._sm is not None:
            return self._sm
        else:
            raise ComponentLookupError('no site manager defined')

    def setSiteManager(self, sm):
        if ISite.providedBy(self):
            raise TypeError("Already a site")

        if IComponentLookup.providedBy(sm):
            self._sm = sm
            sm.__name__ = '++etc++site'
            sm.__parent__ = self
        else:
            raise ValueError('setSiteManager requires an IComponentLookup')

        directlyProvides(
            self, ISite,
            directlyProvidedBy(self))

        notify(NewLocalSite(sm))
 