##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
$Id: layer.py 197 2007-04-13 05:03:32Z rineichen $
"""

import zope.interface
from zope.schema.fieldproperty import FieldProperty
from z3c.website import sample
from jquery.demo.jsonform import interfaces


class JSONFormSample(sample.Sample):
    """JSON form sample."""

    zope.interface.implements(interfaces.IJSONFormSample)


class AnotherSessionData(object):
    """None persistent sample content object for storing in a session."""

    zope.interface.implements(interfaces.IAnotherSessionData)

    asciiField = FieldProperty(interfaces.IAnotherSessionData['asciiField'])
    asciiLineField = FieldProperty(
        interfaces.IAnotherSessionData['asciiLineField'])
    dateField = FieldProperty(interfaces.IAnotherSessionData['dateField'])
    datetimeField = FieldProperty(
        interfaces.IAnotherSessionData['datetimeField'])
    decimalField = FieldProperty(
        interfaces.IAnotherSessionData['decimalField'])
    dottedNameField = FieldProperty(
        interfaces.IAnotherSessionData['dottedNameField'])
    floatField = FieldProperty(interfaces.IAnotherSessionData['floatField'])
    idField = FieldProperty(interfaces.IAnotherSessionData['idField'])
