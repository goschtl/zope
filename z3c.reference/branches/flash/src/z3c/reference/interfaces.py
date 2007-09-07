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
$Id$
"""
__docformat__ = 'restructuredtext'

import zope.interface
import zope.schema
from zope.location.interfaces import ILocation
from zope.app.file.interfaces import IImage
from zope.interface.interfaces import IInterface


class IViewReference(zope.interface.Interface):
    """a reference to a view of an object, by storing the name of the
    view. If the target is None, the view name is supposed to be an
    absolute url to an external target"""

    title = zope.schema.Text(
            title = u'Title',
            description = u'The title of the reference',
            )

    description = zope.schema.Text(
            title = u'Description',
            description = u'The description of the reference',
            )

    target = zope.schema.Object(
        schema=ILocation,
        title=u'Target Object',
        required=True,)

    view = zope.schema.TextLine(
        title=u'View',
        required=False)


class IImageReference(IViewReference):
    """a reference to an image with optional size constraints"""

    target = zope.schema.Object(
        schema=IImage,
        title=u'Target Image',
        required=False)


class IReferenced(zope.interface.Interface):
    """backrefs"""

    viewReferences = zope.schema.List(
        title=u"View references",
        value_type=zope.schema.Object(IViewReference),
        required=False,
        readonly=True,
        default=[])


class IViewReferenceField(zope.schema.interfaces.IObject):
    """a view reference field"""

    settingName = zope.schema.TextLine(
        title=u"Setting Name",
        required=False,
        default=u'')


class IViewReferenceSettings(zope.interface.Interface):

    settings = zope.schema.Dict(
        title=u'Settings',
        description=u'Settings used for setup the view reference editor.',
        required=False,
        default={})


class IImageReferenceField(zope.schema.interfaces.IObject):
    """an image reference field"""

    size = zope.schema.Tuple(
        title=u'Forced Size',
        value_type=zope.schema.Int(),
        required=True,
        min_length=2,
        max_length=2)


class IObjectReferenceField(IViewReferenceField):
    """a schema based reference field"""

    refSchema = zope.schema.Object(
        schema=IInterface,
        title=u'Reference Schema')


class IViewReferenceEditorSearch(zope.interface.Interface):
    """Marker interface for view reference editor search forms."""


class IViewReferenceEditorEdit(zope.interface.Interface):
    """Marker interface for view reference editor edit forms."""
