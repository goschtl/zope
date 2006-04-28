##############################################################################
#
# Copyright (c) 2006 ROBOTECH Logistiksysteme GmbH and Contributors.
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
from persistent import Persistent

from zope.security.proxy import removeSecurityProxy

from zope.app.container.contained import Contained
from zope.app.container.contained import ContainedProxy
from zope.app.container.contained import NameChooser
from zope.app.container.interfaces import IContained
from zope.app.location.interfaces import ILocation
from zope.app.exception.interfaces import UserError

from zope import interface
from zope.configuration.name import resolve

import sqlalchemy

from interfaces import ISQLAlchemyContainer


def contained(obj, parent=None, name=None):
    """An implementation of zope.app.container.contained.contained
    that doesn't generate events, for internal use.

    Borrowed from SQLOS.
    """
    if (parent is None):
        raise TypeError, 'Must provide a parent'

    if not IContained.providedBy(obj):
        if ILocation.providedBy(obj):
            directlyProvides(obj, IContained, directlyProvidedBy(obj))
        else:
            obj = ContainedProxy(obj)

    oldparent = obj.__parent__
    oldname = obj.__name__

    if (oldparent is None) or not (oldparent is parent
                                   or sameProxiedObjects(oldparent, parent)):
        obj.__parent__ = parent

    if oldname != name and name is not None:
        obj.__name__ = name

    return obj


class SQLAlchemyNameChooser(NameChooser):

    def checkName(self, name, container):

        if isinstance(name, str):
            name = unicode(name)
        elif not isinstance(name, unicode):
            raise TypeError("Invalid name type", type(name))

        unproxied = removeSecurityProxy(container)
        if not name.startswith(unproxied._class.__name__+'.'):
            raise UserError(
                _("Invalid name for SQLAlchemy object")
                )
        try:
            id = int(name.split('.')[-1])
        except:
            raise UserError(
                _("Invalid id for SQLAlchemy object")
                )

        return True

    def chooseName(self, name, obj):
        # commit the object to make sure it contains an id
        sqlalchemy.objectstore.commit(obj)
        return '%s.%i'%(obj.__class__.__name__, obj.id)


class SQLAlchemyContainer(Persistent, Contained):
    interface.implements(ISQLAlchemyContainer)

    _className = ''
    _class = None

    def setClassName(self, name):
        self._className = name
        self._class=resolve(name)

    def getClassName(self):
        return self._className
    className = property(getClassName, setClassName)

    def keys(self):
        for name, obj in self.items():
            yield name

    def values(self):
        for name, obj in self.items():
            yield obj

    def __iter__(self):
        return iter(self.keys())

    def items(self):
        for obj in self._class.mapper.select():
            name = '%s.%i'%(self._class.__name__, obj.id)
            yield (name, contained(obj, self, name) )

    def __getitem__(self, name):
        if not isinstance(name, basestring):
            raise KeyError, "%s is not a string" % name
        vals = name.split('.')
        try:
            id=int(vals[-1])
        except ValueError:
            return None
        obj = self._class.mapper.selectfirst(self._class.c.id==id)
        if obj is None:
            raise KeyError, name
        return contained(obj, self, name)

    def get(self, name, default = None):
        try:
            return self[name]
        except KeyError:
            return default
    
    def __contains__(self, name):
        return self.get(name) is not None

    def __len__(self):
        try:
            return self._class.mapper.count()
        except sqlalchemy.exceptions.SQLError:
            # we don't want an exception in case of database problems
            return 0

    def __delitem__(self, name):
        obj = self[name]
        #TODO: better delete objects using a delete adapter
        #      for dependency handling.
        obj.delete()

    def __setitem__(self, name, item):
        sqlalchemy.objectstore.commit(item)

