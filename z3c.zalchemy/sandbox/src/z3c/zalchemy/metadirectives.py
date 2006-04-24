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
    name = schema.TextLine(title = u'Engine name',
                           required = True,
                           )
    
    dns = schema.TextLine(title = u'DNS for the database connection',
                          required = True,
                          )
    
    echo = Bool(title = u'Echo SQL statement',
                required = False,
                default=False
                )

    convert_unicode = Bool(title = u'Convert Unicode',
            description=u"""If set to True, all String/character based
                           types will convert Unicode values to raw
                           byte values going into the database, and
                           all raw byte values to Python Unicode
                           coming out in result sets. This is an
                           engine-wide method to provide unicode
                           across the board. For unicode conversion on
                           a column-by-column level, use the Unicode
                           column type instead.""",
                           required = False,
                           default=False
                )

    encoding = schema.TextLine(title=u'Encoding',
                               default=u'utf-8',
                               required=False)

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
