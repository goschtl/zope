##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""Shard Database Interfaces

$Id:$
"""
import zope.interface
from zope import schema
from zope.app.container.interfaces import IContainer

# set up internationalization
import zope.i18nmessageid
_ = zope.i18nmessageid.MessageFactory("zope")

class IShardPartition(zope.interface.Interface):
    """Represents a database back-end"""

    database_name = schema.TextLine(
        title=u'Database name',
        description=u'The name of the database to access',
        required=True)

    weight = schema.Float(
        title=u'Weight',
        description=u'How much of the hash space to assign to this database',
        required=True,
        default=1.0)


class IShardContainer(IContainer):
    """A container that partitions its contents in multiple databases"""

    partitions = zope.interface.Attribute(
        "A tuple of IShardPartition objects describing where to store objects")

    auto_weight = schema.Bool(
        title=u'Automatic Weighting',
        description=
        u"""If true, partition weights are chosen automatically to balance
        the available storage space.  If false, weights come from the weight
        attribute of each IShardPartition.""",
        required=True,
        default=True)
