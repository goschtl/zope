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
"""Zope skin feature.

$Id$
"""
import os
import zope.interface
from zope.schema.fieldproperty import FieldProperty

from z3c.builder.core import project, zcml, python, form
from z3c.feature.core import base, xml
from z3c.feature.zope import interfaces

SKIN_DOCUMENTATION = """
The Zope Skin Feature lets you define a basic skin along with a layer
that can inherit from other layers.
"""

class ZopeSkinFeature(base.BaseFeature):
    zope.interface.implements(interfaces.IZopeSkinFeature)

    featureDocumentation = SKIN_DOCUMENTATION
    featureSingleton = True
    featureDependencies = ('zope-project',)

    @property
    def featureTitle(self):
        return u'Zope Skin'

    def _applyTo(self, project):
        if 'interfaces.py' not in project.package.keys():
            project.package.add(python.ModuleBuilder(u'interfaces.py'))
        ifaces = project.package['interfaces.py']

        # Step 1: define a layer
        layerIface = python.InterfaceBuilder(u'ILayer')
        layerIface.docstring = str("Browser Layer for %s" % project.name)
        layerIface.bases = ['zope.publisher.interfaces.browser.IBrowserRequest']
        ifaces.add(layerIface)

        # Step 2: define a skin
        skinIface = python.InterfaceBuilder(u'ISkin')
        skinIface.docstring = str("Browser Skin for %s" % project.name)
        skinIface.bases = ['z3c.form.interfaces.IFormLayer',
                           'z3c.formui.interfaces.IDivFormLayer',
                           'z3c.layer.pagelet.IPageletBrowserLayer',
                           layerIface.getPythonPath()]
        ifaces.add(skinIface)

        configure = project.package['configure']

        # Step 3: register the skin
        skinDirective = zcml.ZCMLDirectiveBuilder(
            namespace=zcml.ZOPE_NS,
            name='interface',
            attributes={'interface':skinIface.getPythonPath(),
                        'type':'zope.publisher.interfaces.browser.IBrowserSkinType',
                        'name':project.name})
        configure.add(skinDirective)

        # Step 4: make it the default skin
        appConfig = project.package['appConfig']
        appConfig.add(zcml.ZCMLDirectiveBuilder(
            namespace=zcml.BROWSER_NS,
            name='defaultSkin',
            attributes={'name':project.name}))
