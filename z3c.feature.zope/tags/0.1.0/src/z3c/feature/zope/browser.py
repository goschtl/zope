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
"""Zope Page Features

$Id$
"""
import os
import zope.interface
from zope.schema.fieldproperty import FieldProperty

from z3c.builder.core import base, project, zcml
from z3c.feature.core.base import BaseFeature
from z3c.feature.zope import interfaces

PAGE_DOCUMENTATION = """
The Zope Page Feature creates a simple Zope 3 style page.
"""

class ZopePageFeature(BaseFeature):
    zope.interface.implements(interfaces.IZopePageFeature)

    featureTitle = u'Zope Page'
    featureDocumentation = PAGE_DOCUMENTATION
    featureSingleton = False

    name = FieldProperty(interfaces.IZopePageFeature['name'])
    templateName = FieldProperty(interfaces.IZopePageFeature['templateName'])

    @property
    def featureTitle(self):
        return u'Zope Page (%s)' % self.name

    def update(self):
        if not self.templateName:
            self.templateName = self.name.split('.')[0]+'.pt'
        super(ZopePageFeature, self).update()

    def _applyTo(self, project):
        project.package['browser'].add(
            base.SimpleFileBuilder(
                self.templateName,
                os.path.join(os.path.dirname(__file__),
                             'file-templates', 'simple-page.pt')
                )
            )
        config = project.package['browser']['configure']
        config.add(zcml.ZCMLDirectiveBuilder(
            namespace = zcml.BROWSER_NS,
            name = u'page',
            attributes = {
                'name': self.name,
                'for': '*',
                'template': 'page.pt',
                'permission': 'zope.Public'}
            ))

