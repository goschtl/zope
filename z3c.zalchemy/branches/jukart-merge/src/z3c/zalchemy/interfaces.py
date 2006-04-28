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
from zope import interface
from zope import schema
from zope.app.container.interfaces import IContainer
from zope.app.container.constraints import contains, containers


class ISQLAlchemyObject(interface.Interface):
    """Marker interface for mapped sqlalchemy objects.
    """


class ISQLAlchemyContainer(IContainer):
    """A zope container containing sqlalchemy objects.
    """
    className = schema.TextLine(
            title = u'Class',
            required = True,
            )
    contains(ISQLAlchemyObject)


class ISQLAlchemyObjectContained(interface.Interface):
    """Limit containment to SQLAlchemy containers
    """
    containers(ISQLAlchemyContainer)


class IAlchemyEngineUtility(interface.Interface):
    dns = schema.Text(
            title = u'DNS',
            required = True,
            )
    echo = schema.Bool(
            title=u'echo sql',
            required=False,
            default=False
            )
    proxyEngine = interface.Attribute(
            'Engine to bind related tables to one engine',
            )

    def addTable(name):
        """Add a table to the engine.

        The name must be unique within all utilities.
        This name can be used in a sqlalchemy table definition :
          t = Table('myName',
                    zalchemy.getProxyEngine('myNameInZAlchemy'
                    ...
                   )

        This allowes to bind all related tables to the same proxy which
        is neccessary for Relations.

        The name need not be the name of the table.
        """

