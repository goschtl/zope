##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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
"""The lovely relation interfaces.

$Id$
"""
__docformat__ = "reStructuredText"

from zope import interface
from zope import schema
from zope.schema.interfaces import IField
from zope.app.container import constraints
from zope.app.container.interfaces import IContainer

from i18n import _


class IFieldRelationManager(interface.Interface):

    fOut = schema.Object(IField)
    fIn = schema.Object(IField)
    relType = interface.Attribute("The relation type identifier")
    utilName = schema.TextLine(title=u'Relations Utility Name')


class IPropertyRelationManager(interface.Interface):

    def getRelations():
        """Return the relations for a property"""

    def getRelationTokens():
        """Return the relation tokens for a property"""


class IRelations(IContainer):
    """A container to manage relations"""

    def findTargets(source, relation=None):
        """Find all targets related to the source.

        The relation parameter allows to filter for specific relations.
        If no relation is given all targets are returned.
        """

    def findSources(target, relation=None):
        """Find all sources containing the target.

        The relation parameter allowes to filter for specific relations.
        If no relation is given all sources are returned.
        """


class IRelationType(interface.Interface):
    """A relationship type

    The relationship type is the verb of the relation.
    """
    constraints.containers('.IRelationTypes')

    title = schema.TextLine(
            title = _(u'title'),
            description = _(u'The title of this relation'),
            required = True,
            default = u''
            )

    description = schema.Text(
            title = _(u'description'),
            description = _(u'The description for the relation.'),
            required = False,
            default = u''
            )


class IRelationTypes(IContainer):
    """A container to manage relationtypes."""
    constraints.contains(IRelationType)


class IRelationTypeLookup(interface.Interface):
    """Encapsulate relation type lookup."""

    relationtypes = interface.Attribute(
        """Property returning the relationtypes container used for lookups. Readonly.
        """)

    def _lookup(relation):
        """Look up relation type objects

        If `relation` is a string, the corresponding relationtype
        object is looked up in the relationtypes container and returned.
        If `self.relationtypes` is None or `relation` is not a string,
        no lookup is performed and the argument is returned unchanged.
        """


class IRelationship(interface.Interface):
    """A one to many relationship"""

    __parent__ = interface.Attribute(
        """The relationship container of which this relationship is a member
        """)

    sources = interface.Attribute(
        """Sources pointing in the relationship.  Readonly.""")

    relations = interface.Attribute(
        """The relations the relation belongs to.""")

    targets = interface.Attribute(
        """Targets being pointed to in the relationship.  Readonly.""")


class IOneToManyRelationship(interface.Interface):
    """Allow the modification of the many part of a one-to-many relationship"""

    def add(obj):
        """A a target target to the relation"""

    def remove(obj):
        """Remove a target target from the relation"""


class IOneToManyRelationships(IRelations):
    """A container for one-to-many relationships"""
    constraints.contains(IOneToManyRelationship)


class IOneToOneRelationship(interface.Interface):
    """A simple one-to-one relationship"""


class IOneToOneRelationships(IRelations):
    """A container for one-to-one relationships"""
    constraints.contains(IOneToOneRelationship)

class IO2OStringTypeRelationships(IRelations):
    """A container for one-to-one relationships"""
    constraints.contains('IO2OStringTypeRelationships')

class IO2OStringTypeRelationship(IOneToOneRelationship):
    """A one to one relationship with a string as type"""
