##############################################################################
#
# Copyright (c) 2006 ROBOTECH Logistiksysteme GmbH
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
from zope.configuration.fields import GlobalObject,Bool


class IEngineDirective(interface.Interface):
    """Define an engine.
    """
    name = schema.Text(
            title = u'Engine name',
            required = True,
            )
    dns = schema.Text(
            title = u'DNS for the database connection',
            required = True,
            )
    echo = schema.Bool(
            title = u'Echo SQL statement',
            required = False,
            default=False
            )

# Arbitrary keys and values are allowed to be passed to the viewlet.
IEngineDirective.setTaggedValue('keyword_arguments', True)


class IConnectDirective(interface.Interface):
    """
    """
    engine = schema.Text(
            title = u'Engine',
            description = u'The name of the engine to connect a table to',
            required = True,
            )
    table = GlobalObject(
            title = u'Table',
            description = u'The table to ceonnect the engine to.'\
                          u'The Table must contain a ProxyEngine !',
            required = True,
            )

    create = Bool(title=u'Create Table',default=False,
                  required=False)
