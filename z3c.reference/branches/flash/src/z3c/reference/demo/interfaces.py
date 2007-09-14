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
$Id: __init__.py 72084 2007-01-18 01:02:26Z rogerineichen $
"""
__docformat__ = 'restructuredtext'

from zope import interface, schema

from z3c.reference.schema import ViewReferenceField
from zope.app.file.interfaces import IImage


class IDemoFolder(interface.Interface):
    """ demo folder"""

    previewImage = ViewReferenceField(
        title=u'Preview Image',
        description=u'Referenced Preview Image',
        required=False,
        settingName=u'')

    assets = schema.List(
        title=u'Related',
        description=u'Referenced list of objects',
        value_type=ViewReferenceField(
            title=u'Related item',
            settingName=u''),
        required=False,
        default=[])


class IDemoImage(IImage):
    """ demo image"""


