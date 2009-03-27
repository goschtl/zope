##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""Zope Features Interfaces

$Id$
"""
import zope.interface
import zope.schema
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm

from z3c.feature.core.interfaces import IFeatureSchema

FieldsVocabulary = SimpleVocabulary(
    [SimpleTerm('zope.schema.TextLine', u'Text Line', u'Text Line'),
     SimpleTerm('zope.schema.Text', u'Text', u'Text'),
     SimpleTerm('zope.schema.Int', u'Integer', u'Integer'),
     SimpleTerm('zope.schema.Float', u'Float', u'Float'),
     ])

class IZopeProjectFeature(zope.interface.Interface):
    """A feature converting a project to a Zope project."""
zope.interface.directlyProvides(IZopeProjectFeature, IFeatureSchema)

class IZopePageFeature(zope.interface.Interface):
    """A feature to produce a simple page."""

    name = zope.schema.TextLine(
        title=u'Name',
        description=(u'The name by which the page can be accessed in a url '
                     u'i.e. index.html'),
        default=u'index.html')

    templateName = zope.schema.TextLine(
        title=u'Template Name',
        description=(u'The name of the template for the page. '
                     u'Defaults to the name of the page.'),
        required=False)

zope.interface.directlyProvides(IZopePageFeature, IFeatureSchema)


class IZopeContentFeature(zope.interface.Interface):
    """A feature to produce a Content Object with CRUD pages."""

    className = zope.schema.TextLine(
        title=u'Class Name',
        description=u'The name of the class to create. i.e. MyContent',
        default=u'MyContent')

    classFile = zope.schema.TextLine(
        title=u'Class File',
        description=(u'The file in which to put the class. i.e. mycontent.py. '
                     u'Defaults to the lowercased version of the class name'),
        required=False)

    fields = zope.schema.Dict(
        title=u'Fields',
        description=u'The fields for this object',
        key_type=zope.schema.TextLine(
            title=u'Name',
            description=u'The name of the field'),
        value_type=zope.schema.Choice(
            title=u'Type',
            description=u"The field's type.",
            vocabulary=FieldsVocabulary)
        )

zope.interface.directlyProvides(IZopeContentFeature, IFeatureSchema)


class IZopeSkinFeature(zope.interface.Interface):
    """A feature to produce a Skin with a layer."""

zope.interface.directlyProvides(IZopeSkinFeature, IFeatureSchema)
